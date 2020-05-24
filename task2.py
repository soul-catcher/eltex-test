#!/usr/bin/env python3
"""Database saver

This script read .json routing table file and saves
data to SQLite3 database, then read database and print data.

Example:
    # python3 task2.py routing_table.json routing_table.db
"""

import argparse
import sys
import sqlite3
import json
from typing import Iterable

SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = SECONDS_PER_MINUTE * 60
SECONDS_PER_DAY = SECONDS_PER_HOUR * 24
SECONDS_PER_WEEK = SECONDS_PER_DAY * 7


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
                        metavar="INFILE", help="Json file with routing table")
    parser.add_argument("output_file", metavar="OUTFILE",
                        help="Output sqlite file to store database")
    return parser.parse_args(args)


def is_table_exist(name: str, cursor: sqlite3.Cursor) -> bool:
    """Check if SQLite table already exist"""
    cursor.execute(f"""SELECT count(name) FROM sqlite_master
        WHERE type='table' AND name='{name}'""")
    return cursor.fetchone()[0] == 1


def create_next_hop_table(route_table: dict, cursor: sqlite3.Cursor) -> None:
    """Creates next_hop table in database and fills it"""
    cursor.execute("CREATE TABLE next_hop (address text)")
    for next_hop in route_table["route_table"]["next_hop"]:
        cursor.execute('INSERT INTO next_hop VALUES (?)', (next_hop,))
    cursor.close()


def age_to_seconds(age: str) -> int:
    """Converts age to seconds"""

    *date, time = age.split()
    hours, minutes, seconds = time.split(':')

    total_time = (int(seconds) + int(minutes) * SECONDS_PER_MINUTE +
                  int(hours) * SECONDS_PER_HOUR)
    if date:
        date = date[0].rstrip('d')
        *weeks, days = date.split('w')
        total_time += int(days) * SECONDS_PER_DAY
        if weeks:
            total_time += int(weeks[0]) * SECONDS_PER_WEEK
    return total_time


def seconds_to_age(seconds: int) -> str:
    """Converts seconds to age format"""
    weeks, seconds = divmod(seconds, SECONDS_PER_WEEK)
    days, seconds = divmod(seconds, SECONDS_PER_DAY)
    hours, seconds = divmod(seconds, SECONDS_PER_HOUR)
    minutes, seconds = divmod(seconds, SECONDS_PER_MINUTE)
    age = ""
    if weeks:
        age += f"{weeks}w"
    if weeks or days:
        age += f"{days}d "
    age += f"{hours:02}:{minutes:02}:{seconds:02}"
    return age


def create_destination_table(route_table: dict,
                             cursor: sqlite3.Cursor) -> None:
    """Creates destination table in database and fills it"""
    cursor.execute('''CREATE TABLE destination (destination text,
        preference integer, metric integer, next_hop text, interface text,
        age integer)''')
    for next_hop, dests_dict in route_table["route_table"]["next_hop"].items():
        for dest, data in dests_dict.items():
            cursor.execute("INSERT INTO destination VALUES (?, ?, ?, ?, ?, ?)",
                           (dest, data["preference"], data["metric"], next_hop,
                            data["via"], age_to_seconds(data["age"])))
    cursor.close()


def print_table(csr: sqlite3.Cursor) -> None:
    print("Destination        | Prf | Metric | Next hop        | "
          "Interface     | Age")
    prev_destination = None
    for row in csr.execute("SELECT * FROM destination ORDER BY destination"):
        row = list(row)
        if row[0] == prev_destination:
            row[0] = ''
        row[-1] = seconds_to_age(row[-1])
        print("{:<18} | {:<3} | {:<6} | {:<15} | {:<13} | {}".format(*row))

        prev_destination = row[0]


if __name__ == '__main__':
    commandline_args = parse_args()
    input_file = commandline_args.input_file
    output_file_name = commandline_args.output_file
    try:
        route_table_dict = json.load(input_file)
        with sqlite3.connect(output_file_name) as connect:
            if not is_table_exist("next_hop", connect.cursor()):
                create_next_hop_table(route_table_dict, connect.cursor())
            if not is_table_exist("destination", connect.cursor()):
                create_destination_table(route_table_dict, connect.cursor())
            print_table(connect.cursor())

    except json.decoder.JSONDecodeError as e:
        print("JSON file has bad format\n", e, file=sys.stderr)
    except sqlite3.OperationalError as e:
        print(e, file=sys.stderr)
    finally:
        input_file.close()
