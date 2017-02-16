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
import random
import sys
import json

import math

from utils import load_config


def main():
    """
    Generate a modified version of the configuration file given a base one.
    """

    # number of nodes
    n = 10

    # ring radius in meters
    r = 3.0

    nodes = []
    for i in range(n):
        angle = math.radians(360.0 / n * i)
        x = math.sin(angle) * r
        y = math.cos(angle) * r
        nodes.append([x, y])

    # load the configuration
    config = load_config('config.json')
    config['simulation']['nodes'] = [nodes]

    # print to the shell
    print(json.dumps(config, indent=4))


# entry point
if __name__ == '__main__':
    main()
