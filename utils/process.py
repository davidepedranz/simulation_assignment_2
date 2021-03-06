#!/usr/bin/env python

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2017 Davide Pedranz <davide.pedranz@gmail.com>

import os
import plots
from collections import OrderedDict
from pandas import DataFrame, concat, read_csv, read_hdf
from utils import locate, mkdir

# possible packet states
# NB: make sure this codes match to the one used by the Log class

PKT_RECEIVING = 0
PKT_RECEIVED = 1
PKT_CORRUPTED = 2
PKT_CORRUPTED_BY_CHANNEL = 3
PKT_GENERATED = 10
PKT_QUEUE_DROPPED = 11


def is_number(string):
    """
    Determine whether a string contains a number.
    """
    try:
        float(string)
        return True
    except ValueError:
        return False


def get_data_files(folder, suffix=".csv"):
    """
    Gets the list of files with a certain prefix and suffix in a folder.
    """
    files_list = []
    for f in os.listdir(folder):
        if f.endswith(suffix):
            files_list.append(f)
    return files_list


def parse_file_name(name):
    """
    Parse the name of a CSV file generated by a run of the simulator,
    according to the following format: 'output_{simulator}_{lambda}_{seed}.csv'
    :param name: Name of the file.
    :return: Dictionary of the parameters used to run the simulation.
    """
    tokens = os.path.splitext(name)[0].split("_")
    a = tokens[1].split('.')
    return {
        'id': tokens[1],
        'lambda': float(tokens[2]),
        'seed': float(tokens[3]),
        'propagation': a[0],
        'simulator': a[1],
        'p': a[2] + '.' + a[3] if len(a) == 4 else '_'
    }


def offered_load(l, n_nodes, packet_size=(1460 + 32) / 2):
    """
    Total offered load in Mbps.
    'l' is the Lambda parameter of the distribution (packets / s).
    """
    assert is_number(l)
    return l * n_nodes * packet_size * 8 / 1024 / 1024


def statistics(x, sim_time, load):
    """
    Computes throughput, collision rate and drop rate for a specific node
    and a specific simulation.
    :param x Dataframe for a single node.
    :param sim_time Total simulation time.
    :param load Load offered for this simulation.
    """

    rcv_packets_df = x.loc[x.event == PKT_RECEIVED]

    # number of packets for each type
    rcv_packets = len(rcv_packets_df)
    crp_packets = len(x.loc[x.event == PKT_CORRUPTED])
    crp_ch_packets = len(x.loc[x.event == PKT_CORRUPTED_BY_CHANNEL])
    gen_packets = len(x.loc[x.event == PKT_GENERATED])
    drp_packets = len(x.loc[x.event == PKT_QUEUE_DROPPED])
    inc_packets = rcv_packets + crp_packets + crp_ch_packets

    # return the statistics
    return DataFrame(OrderedDict({
        'tr': [rcv_packets_df['size'].sum() * 8 / sim_time / 1024 ** 2],
        'cr': [float(crp_packets) / inc_packets],
        'dr': [float(drp_packets) / gen_packets],
        'cc': [float(crp_ch_packets) / inc_packets],
        'load': load
    }))


def compute_stats_single_run(dataframe, lambda_par):
    """
    Compute the statistics for a single run of the simulator.
    :param dataframe: Pandas Dataframe with the raw data (CSV file).
    :param lambda_par: Lambda parameter.
    :return: Statistics for this run.
    """
    n_nodes = len(dataframe['dst'].unique())
    load = offered_load(lambda_par, n_nodes)
    stats = dataframe.groupby('dst').apply(
        lambda x: statistics(x, dataframe.time.max(), load))
    stats_no_index = stats.reset_index(level=1, drop=True).reset_index()
    return stats_no_index


def process_csv_raw_files(folder):
    """
    Compute the statistics for a single run of the simulator.
    :param folder: Folder where the raw CSV files are stored.
    :return: Statistics as a Pandas Dataframe.
    """

    # store all statistics in memory
    all_statistics = DataFrame()

    # get the list of files
    files = get_data_files(folder, ".csv")

    # compute the statistics one run at a time
    for i, f in enumerate(files):
        print ('  -> Analyze simulation %i of %i' % (i + 1, len(files)))

        # parse the parameters
        params = parse_file_name(f)

        # read the CSV
        current_csv = read_csv("%s/%s" % (folder, f))

        # compute statistics
        current_stats = compute_stats_single_run(current_csv, params['lambda'])

        # add columns
        current_stats.insert(0, 'id', params['id'])
        current_stats.insert(1, 'propagation', params['propagation'])
        current_stats.insert(2, 'simulator', params['simulator'])
        current_stats.insert(3, 'p', params['p'])
        current_stats['lambda'] = params['lambda']
        current_stats['seed'] = params['seed']

        # save statistics
        all_statistics = concat([all_statistics, current_stats])

    # return the statistics for all files
    return all_statistics.reset_index(drop=True)


def aggregate_statistics(stats):
    """
    Aggregate the raw statistics.
    """

    # aggregate by simulator version and load
    agg = stats.groupby(['id', 'simulator', 'propagation', 'p', 'load'],
                        as_index=False).agg(
        {
            'cr': {
                'cr_mean': 'mean'
            },
            'dr': {
                'dr_mean': 'mean'
            },
            'tr': {
                'tr_mean': 'mean'
            },
            'cc': {
                'cc_mean': 'mean'
            }
        }
    )

    # remove multi-index from columns
    agg.columns = agg.columns.droplevel(1)
    return agg


def main():
    """
    Process the data generated by one or more versions of the simulator.
    """

    # compute the location of the CSV files
    csv_folder = locate('../output/')

    # compute the location for the processing
    results_folder = locate('../results/')
    mkdir(results_folder)

    # compute the statistics
    # use cache if available, otherwise load data from raw CSV
    aggregated_file = results_folder + 'statistics.h5'
    if not os.path.isfile(aggregated_file):
        print('Loading CSV files...')
        all_statistics = process_csv_raw_files(csv_folder)
        all_statistics.to_hdf(aggregated_file, 'statistics', format='fixed')
    else:
        print('Using cached statistics...')
        all_statistics = read_hdf(aggregated_file)

    # get rid of the seeds (take the average over all seeds)
    mean_stats = all_statistics \
        .groupby(['id', 'propagation', 'simulator', 'p',
                  'dst', 'load', 'lambda'], as_index=False) \
        .mean() \
        .reset_index(level=3, drop=True) \
        .drop('seed', 1)

    # make sure the plots folder exists
    plots_folder = locate('../results/plots/')
    mkdir(plots_folder)

    # plot graphs for each simulator
    print("Plotting individual statistics...")
    plots.individual_statistic(mean_stats, plots_folder)

    # compute aggregated statistic for each version of the simulator
    print("Aggregated stats by simulator and load...")
    pro = aggregate_statistics(mean_stats)
    print("Plotting aggregated statistics...")
    plots.aggregated_statistics(pro, plots_folder)

    # store aggregated statistic in a file
    pro.to_hdf(results_folder + 'summary.h5', 'summary', format='table')


# entry point
if __name__ == '__main__':
    main()
