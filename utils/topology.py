import math
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

from utils import load_config, locate, mkdir


def distance((x, y), (_x, _y)):
    """
    Compute the distance between 2 nodes.
    """
    return math.sqrt((x - _x) ** 2.0 + (y - _y) ** 2.0)


def draw_nodes(_nodes, _range, output_file):
    """
    Plot the topology of the network.
    """

    # extract the coordinates
    xs = map(lambda node: node[0], _nodes)
    ys = map(lambda node: node[1], _nodes)

    # compute some colors
    # noinspection PyUnresolvedReferences
    colors = cm.rainbow(np.linspace(0, 1, len(xs)))

    # create the graph
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, aspect='equal')

    # compute the axes
    a = 2
    min_x = round(min(xs) - a - 1)
    max_x = round(max(xs) + a + 1)
    min_y = round(min(ys) - a - 1)
    max_y = round(max(ys) + a + 1)

    # set the axes
    ax.set_xlim((min_x, max_x))
    ax.set_ylim((min_y, max_y))

    # set labels
    ax.set_title('Network Topology', fontsize=16, y=1.02)
    ax.set_xlabel('X coordinate (m)', fontsize=12, labelpad=10)
    ax.set_ylabel('Y coordinate (m)', fontsize=12, labelpad=10)
    ax.tick_params(axis='both', which='major', labelsize=12)

    # positions of labels
    positions = [
        (0, -25),
        (25, 0),
        (-25, 0),
        (0, -25),
        (25, 0),
        (0, 25),
        (0, -25),
        (25, 0),
        (-25, 0),
        (-5, 25)
    ]

    # add each point to the graph
    for i, (x, y, c, p) in enumerate(zip(xs, ys, colors, positions)):

        # nodes
        ax.scatter(x, y, s=350, marker='o', edgecolor='black', linewidth=1,
                   facecolor=c, zorder=2)

        # labels
        ax.annotate(i + 1, xy=(x, y), xytext=p, zorder=3, size='large',
                    textcoords='offset points', ha='center', va='center')

        # lines
        for _x, _y in zip(xs, ys):
            if distance((x, y), (_x, _y)) < _range and x < _x:
                ax.plot([x, _x], [y, _y], 'k--', dashes=(5, 3), zorder=1)

    # save the graph
    fig.savefig(output_file, bbox_inches='tight')


def main():
    """
    Plot the network topology.
    """
    config = load_config('config.json')
    nodes = config['simulation']['nodes'][0]
    _range = config['simulation']['range']

    # plot topology
    directory = locate('../plots/topology/')
    mkdir(directory)
    for f in ['png', 'eps']:
        draw_nodes(nodes, _range, directory + 'topology.' + f)


# entry point
if __name__ == '__main__':
    main()
