import math
import itertools
import matplotlib as mpl
from pandas import Categorical
from utils import mkdir

mpl.use('Agg')
import matplotlib.pyplot as plt


def individual_metric(nodes, loads, metrics, path, title, y_label,
                      y_lim=(0, 1.05)):
    """
    Plot a single metric for a single simulation.
    """

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


def individual_statistic(stat, folder):
    """
    Generate plots for each simulation.
    """

    # destination folder
    base = folder + 'individual/'
    mkdir(base)

    # process each version of the simulator independently from each other
    ids = stat.id.unique()
    for _id in ids:

        # extract current data
        df = stat.query('id=="' + _id + '"')

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
        individual_metric(nodes, loads, crs, base + _id + '_cr.png',
                          'Collision Rate', 'Collision rate at receiver (Mbps)')
        individual_metric(nodes, loads, drs, base + _id + '_dr.png',
                          'Packet Drop Rate', 'Packet drop rate at the sender')
        individual_metric(nodes, loads, trs, base + _id + '_tr.png',
                          'Throughput', 'Throughput at receiver (Mbps)',
                          y_lim=(0, 3))
        individual_metric(nodes, loads, ccs, base + _id + '_cc.png',
                          'Channel Corruption Rate',
                          'Channel corruption rate (Mbps)')


def agg_metric(legend, loc, loads, metrics, path, name, title, y_label,
               y_lim=(0, 1.05)):
    """
    Generate a plot for a single metric of all simulators.
    """

    # generate 2 formats, 1 for LaTeX, 1 for visualization
    for ext in ['eps', 'png']:

        # make sure the destination exits
        directory = path + ext + '/'
        mkdir(directory)

        # create the figure
        figure = plt.figure(figsize=(8, 6), dpi=80)
        ax = figure.add_subplot(111)

        # plots
        marker = itertools.cycle((',', '>', 's', 'x', 'o', 'd', '<'))
        for (v, l, m) in zip(legend, loads, metrics):
            ax.plot(l, m, label=str(v), marker=marker.next())

        # legend, title, axes
        ax.legend(shadow=True, loc=loc, borderpad=0.8, fontsize='large')
        ax.set_title(title, fontsize=20, y=1.02)
        ax.set_xlabel('Total offered load (Mbps)', fontsize=12, labelpad=10)
        ax.set_ylabel(y_label, fontsize=12, labelpad=10)
        ax.tick_params(axis='both', which='major', labelsize=12)

        # axes
        m = int(math.floor(min(map(min, loads))))
        mm = int(math.ceil(max(map(max, loads))))
        ax.xaxis.set_ticks(range(m, mm, 10))
        ax.set_ylim(y_lim)
        ax.grid(True)

        # save plot
        figure.subplots_adjust(left=0.115, right=0.955, top=0.89, bottom=0.125)
        figure.savefig(directory + name + '.' + ext, bbox_inches='tight')
        plt.close(figure)


def aggregated_statistics(agg, folder):
    """
    Generate plots for the aggregated statistics of all simulators.
    """

    def ids_by_propagation_model(prop):
        agg['simulator'] = Categorical(agg['simulator'],
                                       ['aloha', 'trivial', 'simple'])
        s = agg.query('propagation=="%s"' % prop) \
            .sort_values(['simulator', 'p'])
        return s.id.unique()

    def par_by_id(par):
        return lambda _id: list(agg.query('id=="%s"' % _id)[par])

    def id_to_legend(_id):
        s = _id.split('.')
        name = (' (p = %s.%s)' % (s[2], s[3]) if len(s) == 4 else '')
        return s[1].capitalize() + name

    # compute right directory
    base = folder + 'aggregated/'
    mkdir(base)

    # separate different propagation models
    propagation = agg.propagation.unique()
    for p in propagation:
        # extract ids to create the legend
        ids = ids_by_propagation_model(p)
        legend = map(id_to_legend, ids)

        # load
        loads = map(par_by_id('load'), ids)

        # Throughput
        trs = map(par_by_id('tr'), ids)
        agg_metric(legend, 'upper right', loads, trs, base, p + '_tr',
                   'Throughput', 'Throughput at receiver (Mbps)',
                   y_lim=(0, 2.5 if p == 'original' else 1.5))

        # Collision Rate
        crs = map(par_by_id('cr'), ids)
        agg_metric(legend, 'lower right', loads, crs, base, p + '_cr',
                   'Collision Rate', 'Collision rate at receiver (Mbps)')

        # Drop Rate
        drs = map(par_by_id('dr'), ids)
        agg_metric(legend, 'upper left', loads, drs, base, p + '_dr',
                   'Packet Drop Rate', 'Packet drop rate at the sender')

        # Channel Corruption
        ccs = map(par_by_id('cc'), ids)
        agg_metric(legend, 'upper right', loads, ccs, base, p + '_cc',
                   'Channel Corruption Rate', 'Channel corruption rate (Mbps)')
