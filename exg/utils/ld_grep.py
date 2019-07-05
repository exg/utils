#!/usr/bin/env python3

import argparse
import re

from . import elf, macho


def grep(paths, include_re):
    for path in paths:
        with open(path, "rb") as f:
            try:
                info = elf.ELFInfo(f)
            except ValueError:
                try:
                    info = macho.MachOInfo(f)
                except ValueError:
                    continue
            deps = list(info.get_deps())
            if any(include_re.search(dep) for dep in deps):
                yield path, deps


def main():
    """
    Grep dependencies of executable files.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("-p", "--pattern", default=".")
    parser.add_argument("files", metavar="file", nargs="+")
    args = parser.parse_args()
    for name, deps in grep(args.files, re.compile(args.pattern)):
        print(name, " ".join(deps))


if __name__ == "__main__":
    main()
