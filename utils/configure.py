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

import sys
import json

from utils import load_config


def main():
    """
    Generate a modified version of the configuration file given a base one.
    """

    # parse command line arguments
    n = len(sys.argv)
    if n != 3 and n != 4:
        print('Usage: python generate.py [propagation] [sim] [persistence]')
        sys.exit(1)

    # load the configuration
    config = load_config('config.json')

    # edit the configuration
    config['simulation']['propagation'] = sys.argv[1]
    config['simulation']['simulator'] = sys.argv[2]
    if n == 4:
        config['simulation']['persistence'] = sys.argv[3]
    else:
        del config['simulation']['persistence']
        config['simulation']['output'] = config['simulation']['output'] \
            .replace('.{persistence}', '')

    # print to the shell
    print(json.dumps(config, indent=4))


# entry point
if __name__ == '__main__':
    main()
