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
# Copyright (C) 2016 Michele Segata <segata@ccs-labs.org>

import os
import sys
from pandas import DataFrame, Series, concat, read_csv, read_hdf

import matplotlib as mpl

mpl.use('Agg')
import matplotlib.pyplot as plt

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
    Determine whether a string contains a number
    """
    try:
        float(string)
        return True
    except ValueError:
        return False


def get_data_files(folder, suffix=".csv"):
    """
    Gets the list of files with a certain prefix and suffix in a folder
    """
    files_list = []
    for f in os.listdir(folder):
        if f.endswith(suffix):
            files_list.append(f)
    return files_list


def get_params(filename, fields, fields_index):
    """
    Splits the name of an output file by _ and extracts the values of
    simulation parameters
    """
    d = DataFrame()
    p = os.path.splitext(os.path.basename(filename))[0].split("_")
    for f in fields_index:
        v = p[f]
        if is_number(v):
            s = Series([float(v)])
        else:
            s = Series([v])
        d.loc[:, fields[f]] = s
    return d


def offered_load(l, n_nodes, packet_size=(1460 + 32) / 2):
    """
    Total offered load in Mbps.
    'l' is the Lambda parameter of distribution: number of packets / s.
    """
    return l * n_nodes * packet_size * 8 / 1024 / 1024


def statistics(x, sim_time):
    """
    Computes throughput, collision rate, and drop rate for a specific node
    and a specific simulation
    """
    rcv_packets_df = x.loc[x.event == PKT_RECEIVED]

    # number of packets for each type
    rcv_packets = len(rcv_packets_df)
    crp_packets = len(x.loc[x.event == PKT_CORRUPTED])
    crp_ch_packets = len(x.loc[x.event == PKT_CORRUPTED_BY_CHANNEL])
    gen_packets = len(x.loc[x.event == PKT_GENERATED])
    drp_packets = len(x.loc[x.event == PKT_QUEUE_DROPPED])
    inc_packets = rcv_packets + crp_packets + crp_ch_packets

    return DataFrame({
        'tr': [rcv_packets_df['size'].sum() * 8 / sim_time / 1024 ** 2],
        'cr': [float(crp_packets) / inc_packets],
        'dr': [float(drp_packets) / gen_packets],
        'cc': [float(crp_ch_packets) / inc_packets]
    })


def compute_statistics(d, sim_time):
    """
    Computes throughput, collision rate, and drop rate for all nodes and
    simulation runs
    """
    print('Computing statistics...')
    n_nodes = len(d['dst'].unique())
    d['load'] = offered_load(d['lambda'], n_nodes)
    grouped = d.groupby(['simulator', 'lambda', 'load', 'dst'])
    thr = grouped.apply(lambda x: statistics(x, sim_time))
    return thr.reset_index(level=4, drop=True).reset_index()


def replicate_rows(d, fields, n):
    """
    Generates a data frame replicating the row of
    a single-entry dataframe n times
    """
    df = DataFrame()
    for f in fields:
        df = concat([df, DataFrame({f: [d[f][0]] * n})], axis=1)
    return df


def plot_individual_metric(nodes, loads, metrics, path, title, y_label,
                           y_lim=(0, 1.05)):
    figure = plt.figure()
    ax = figure.add_subplot(111)
    for (node, metric) in zip(nodes, metrics):
        ax.plot(loads, metric, label=str(node), marker='o')
    ax.set_title(title, fontsize=16, y=1.02)
    ax.legend(shadow=True, loc='center left', bbox_to_anchor=(1.02, 0.5))
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.92, box.height])
    ax.set_xlabel('Total offered load (Mbps)')
    ax.set_ylabel(y_label)
    ax.set_ylim(y_lim)
    ax.grid(True)
    figure.savefig(path)
    plt.close(figure)


def plot_individual_statistic(stat, folder):
    versions = stat.simulator.unique()

    # process each version of the simulator independently from each other
    for v in versions:
        # extract current data
        df = stat.query('simulator=="' + v + '"')

        # x-axis: lambda ... load on network
        loads = list(df['load'].unique())

        # accumulators for the metrics
        crs = []
        drs = []
        trs = []
        ccs = []

        # extract nodes and metrics for each node
        nodes = df['dst'].unique()
        for n in nodes:
            crs.append(list(df.query('dst==' + str(n))['cr']))
            drs.append(list(df.query('dst==' + str(n))['dr']))
            trs.append(list(df.query('dst==' + str(n))['tr']))
            ccs.append(list(df.query('dst==' + str(n))['cc']))

        # plot the 3 metrics
        base = '0_plot_%s_' % v
        plot_individual_metric(nodes, loads, crs, folder + base + 'crs.png',
                               'Collision Rate',
                               'Collision rate at receiver (Mbps)')
        plot_individual_metric(nodes, loads, drs, folder + base + 'drs.png',
                               'Packet Drop Rate',
                               'Packet drop rate at the sender')
        plot_individual_metric(nodes, loads, trs, folder + base + 'trs.png',
                               'Throughput', 'Throughput at receiver (Mbps)',
                               y_lim=(0, 3))
        plot_individual_metric(nodes, loads, ccs, folder + base + 'ccs.png',
                               'Channel Corruption Rate',
                               'Channel corruption rate (Mbps)')


def aggregate_statistics(stats, folder):
    print("Aggregated stats by simulator and load ... \n")

    # aggregate by simulator version and load
    agg = stats.groupby(['simulator', 'load'], as_index=False).agg({
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
    })

    # remove multi-index from columns
    agg.columns = agg.columns.droplevel(1)

    # plots
    versions = agg.simulator.unique()
    loads = []
    crs = []
    drs = []
    trs = []
    ccs = []

    # extract metrics for each simulator
    for v in versions:
        # extract current data
        df = agg.query('simulator=="' + v + '"')

        # extract metrics
        loads.append(list(df['load']))
        crs.append(list(df['cr']))
        drs.append(list(df['dr']))
        trs.append(list(df['tr']))
        ccs.append(list(df['cc']))

    # plot
    base = '1_compare_simulators_'
    plot_aggregated_metric(versions, loads, crs, folder + base + 'crs.png',
                           'Collision Rate',
                           'Collision rate at receiver (Mbps)')
    plot_aggregated_metric(versions, loads, drs, folder + base + 'drs.png',
                           'Packet Drop Rate',
                           'Packet drop rate at the sender')
    plot_aggregated_metric(versions, loads, trs, folder + base + 'trs.png',
                           'Throughput', 'Throughput at receiver (Mbps)',
                           y_lim=(0, 3))
    plot_aggregated_metric(versions, loads, ccs, folder + base + 'ccs.png',
                           'Channel Corruption Rate',
                           'Channel corruption rate (Mbps)')

    return agg


def plot_aggregated_metric(versions, loads, metrics, path, title, y_label,
                           y_lim=(0, 1.05)):
    figure = plt.figure()
    ax = figure.add_subplot(111)
    for (v, l, m) in zip(versions, loads, metrics):
        ax.plot(l, m, label=str(v), marker='o')
    ax.set_title(title, fontsize=16, y=1.02)
    ax.legend(shadow=True, loc='upper center', bbox_to_anchor=(0.5, -0.18),
              ncol=3)
    box = ax.get_position()
    ax.set_position(
        [box.x0, box.y0 + box.height * 0.15, box.width, box.height * 0.85])
    ax.set_xlabel('Total offered load (Mbps)')
    ax.set_ylabel(y_label)
    ax.set_ylim(y_lim)
    ax.grid(True)
    figure.savefig(path)
    plt.close(figure)


def main():
    """
    Process the data generated by one or more versions of the simulator.
    """

    # compute the location wrt to this file
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    res_folder = os.path.join(__location__, "../output/")

    # or read it as a parameter of the script
    if len(sys.argv) != 1:
        res_folder = sys.argv[1]

    aggregated_file = "%s/all_data.h5" % res_folder

    if not os.path.isfile(aggregated_file):
        # if no aggregated file, load all csv files into a single dataframe
        print('\nLoading CSV files...')
        all_data = DataFrame()
        data_files = get_data_files(res_folder, ".csv")
        for (i, f) in enumerate(data_files):
            full_path = "%s/%s" % (res_folder, f)
            print(' -> %i of %i - %s' % (i, len(data_files), f))
            # get the simulation parameters from the file name
            pars = get_params(full_path,
                              ['prefix', 'simulator', 'lambda', 'seed'],
                              [1, 2, 3])
            d = read_csv(full_path)
            # replicate the parameters n times, with n being the number of
            # records in the csv file
            ext_pars = replicate_rows(pars, ['simulator', 'lambda', 'seed'],
                                      len(d))
            # join the csv data file with the parameters
            d = d.join(ext_pars)
            all_data = concat([all_data, d])

        # store the full database to a single file
        all_data.to_hdf(aggregated_file, 'table')

    else:
        # otherwise simply load the aggregated file
        print('\nCSV files already processed. Using H5 aggregated file...')
        all_data = read_hdf(aggregated_file, 'table')

    # get simulation duration and number of nodes
    sim_time = all_data.time.max()

    # compute the statistics
    stats = compute_statistics(all_data, sim_time)

    # plot graphs for each simulator
    plot_individual_statistic(stats, res_folder)

    # compute aggregated statistic for each version of the simulator
    pro = aggregate_statistics(stats, res_folder)
    print(pro)


# entry point
if __name__ == '__main__':
    main()
