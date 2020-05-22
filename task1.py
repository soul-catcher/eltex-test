#!/usr/bin/env python3
"""Routing table parser.

This script parses routing table log file and saves it to JSON file.

Example:
    $ python3 task1.py dump.log routing_table.json
"""

import argparse
import sys
from typing import Iterable


def parse_args(args: Iterable[str] = None) -> argparse.Namespace:
    """Parse arguments

    Keyword arguments:
    args -- the arguments to parse (default sys.argv[1:])
    """
    # If you see warning here in PyCharm without noinspection comment
    # below, then this probably a bug in PyTypeChecker.
    # It exist in PyCharm 2020.1 and Pycharm 2020.2 RC
    # noinspection PyTypeChecker
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input_file", type=argparse.FileType('r'),
                        metavar="INFILE", help="File with routing table")
    parser.add_argument("output_file", type=argparse.FileType('w'),
                        metavar="OUTFILE",
                        help="Output JSON file to store results")
    return parser.parse_args(args)


if __name__ == '__main__':
    commandline_args = parse_args()
    input_file = commandline_args.input_file
    output_file = commandline_args.output_file
