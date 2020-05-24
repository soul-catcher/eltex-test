#!/usr/bin/env python3
"""Routing table parser.

This script parses routing table log file and saves it to JSON file.

Example:
    $ python3 task1.py dump.log routing_table.json
"""

import argparse
import sys
import json
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Iterable, TextIO


def parse_args(args: Iterable[str] = None) -> argparse.Namespace:
    """Parse arguments and returns namespace of arguments

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


@dataclass
class DestinationData:
    """Class contains data about destination route"""
    destination: str
    protocol: str
    preference: int
    age: str
    metric: int


@dataclass
class NextHopData:
    """Class contains data about next hop route"""
    next_hop: str
    via: str


def parse_destination_line(line: str) -> DestinationData:
    """Parses destination line of routing table"""
    destination, protocol, *age, _, metric = line.split()
    protocol, preference = protocol.strip('*[]').split('/')
    age = ' '.join(age).rstrip(',')
    return DestinationData(destination, protocol, int(preference), age,
                           int(metric))


def parse_next_hop_line(line: str) -> NextHopData:
    """Parses next hop line of routing table"""
    *_, next_hop, _, via = line.split()
    return NextHopData(next_hop, via)


def parse_log_file(log_file: TextIO) -> defaultdict:
    """Parses routing table log file and returns a next hop dict"""
    next_hop_dict = defaultdict(dict)
    for line in log_file:
        if line.startswith((' ', '\t')):
            next_hop_line = line
        else:
            destination_line = line
            continue
        destination_data = parse_destination_line(destination_line)
        next_hop_data = parse_next_hop_line(next_hop_line)
        destination_dict = asdict(destination_data)
        del destination_dict['destination']
        del destination_dict['protocol']
        destination_dict['via'] = next_hop_data.via
        next_hop_dict[next_hop_data.next_hop][
            destination_data.destination] = destination_dict
    return next_hop_dict


if __name__ == '__main__':
    commandline_args = parse_args()
    input_file = commandline_args.input_file
    output_file = commandline_args.output_file
    data_dict = parse_log_file(input_file)
    rout_table_dict = {"route_table": {"next_hop": data_dict}}
    input_file.close()
    json.dump(rout_table_dict, output_file, indent=2)
    output_file.close()
