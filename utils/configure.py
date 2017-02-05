import sys
import json
import os
import re
from collections import OrderedDict


def load_config(json_file):
    """
    Load the configuration of the simulator from a JSON file.
    :param json_file: JSON file (relative path).
    :return: Dictionary with the configuration.
    """

    # locate the file the file
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    path = os.path.join(__location__, json_file)
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
