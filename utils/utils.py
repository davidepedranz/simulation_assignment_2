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
import re
import json
import sys
from collections import OrderedDict


def locate(relative):
    """
    Return the absolute path of a path relative to the current main script.
    :param relative: Relative path.
    :return: Absolute path.
    """
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    return os.path.join(__location__, relative)


def mkdir(directory):
    """
    Make the directory if not already existing.
    :param directory: Directory.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def load_config(json_file):
    """
    Load the configuration of the simulator from a JSON file.
    :param json_file: JSON file (relative path).
    :return: Dictionary with the configuration.
    """

    # locate the file the file
    path = locate(json_file)
    content = ''.join(open(path).readlines())

    # remove comments
    cr = re.compile('(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
                    re.DOTALL | re.MULTILINE)
    match = cr.search(content)
    while match:
        # single line comment
        content = content[:match.start()] + content[match.end():]
        match = cr.search(content)

    # parse to json
    try:
        cfg = json.loads(content, object_pairs_hook=OrderedDict)
    except Exception as e:
        print('Unable to parse ' + json_file)
        print(e)
        sys.exit(1)

    # return the configuration
    return cfg
