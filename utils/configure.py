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
