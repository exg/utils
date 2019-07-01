#!/usr/bin/env python3

import argparse
import os.path
import tempfile
from subprocess import Popen, PIPE


def find_locations(name):
    locations = {}
    cmd = ("rc", "-e", "-K", "-N", "--rename", "-R", name)
    with Popen(cmd, stdout=PIPE) as p:
        for line in p.stdout:
            fields = line.decode("latin-1").rstrip().split(":")
            path = fields[0]
            line = int(fields[1])
            col = int(fields[2]) - 1
            if path not in locations:
                locations[path] = {}
            if line not in locations[path]:
                locations[path][line] = []
            locations[path][line].append(col)
    return locations


def compose_line(line, columns, name, new_name):
    segments = []
    left = 0
    for col in sorted(columns):
        segments.append(line[left:col])
        left = col + len(name)
    segments.append(line[left:])
    return new_name.join(segments)


def rename_symbol(name, new_name):
    locations = find_locations(name)
    for path, index in locations.items():
        content = ""
        with open(path, "r") as f:
            for n, line in enumerate(f, 1):
                content += compose_line(line, index.get(n, []), name, new_name)
        with tempfile.NamedTemporaryFile(
            dir=os.path.dirname(path),
            mode="w",
            encoding="latin-1",
            delete=False,
        ) as f:
            f.write(content)
            os.rename(f.name, path)


def main():
    """
    Rename a symbol using rtags.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("name")
    parser.add_argument("new_name")
    args = parser.parse_args()

    rename_symbol(args.name, args.new_name)


if __name__ == "__main__":
    main()
