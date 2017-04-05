from __future__ import division
from __future__ import print_function

import argparse

from dependency_handler.resolve_dependencies import resolve_dependencies


def create_parser():
    """A function to create the argument parser to parse the user's input.

    :return: The argument parser.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', dest='config',
                        required=True, action='store',
                        help='The dependencies configuration file')
    return parser


def parse_arguments():
    """A function to parse the user's arguments and return an object which 
    holds the user's parsed arguments.

    :return: The user's parsed arguments as object.
    """
    parser = create_parser()
    args = parser.parse_args()
    return args


def main():
    """The main function to handle the user's input."""
    arguments = parse_arguments()
    resolve_dependencies(arguments)


if __name__ == '__main__':
    main()
