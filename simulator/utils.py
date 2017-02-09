import os


def locate(relative):
    """
    Return the absolute path of a path relative to the current main script.
    :param relative: Relative path.
    :return: Absolute path.
    """
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    return os.path.join(__location__, relative)


def mkdir_for_file(path):
    """
    Make the directory for the specified file (if not existing).
    :param path: Path ot file.
    """
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
