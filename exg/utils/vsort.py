#!/usr/bin/env python3

# version number sort (almost) compatible with coreutils sort -V
# https://www.debian.org/doc/debian-policy/ch-controlfields.html#version
# https://git.savannah.gnu.org/cgit/gnulib.git/plain/lib/filevercmp.c

import argparse
import re
import string
import sys


def order(c: str) -> int:
    if c in string.ascii_letters:
        return ord(c)
    if c == "~":
        return -1
    return ord(c) + 256


def version_key(version: str) -> list[int]:
    digit_re = re.compile(r"\d+")
    nondigit_re = re.compile(r"\D+")
    key = []
    while version:
        match = nondigit_re.match(version)
        if match:
            key.extend(order(c) for c in match.group(0))
            version = version[len(match.group(0)) :]
        else:
            key.append(0)
        match = digit_re.match(version)
        if match:
            key.append(int(match.group(0)))
            version = version[len(match.group(0)) :]
        else:
            key.append(0)
    return key


def main() -> None:
    """
    Sort version numbers.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("file", nargs="?")
    args = parser.parse_args()

    if args.file:
        with open(args.file) as f:
            versions = [line.rstrip() for line in f]
    else:
        versions = [line.rstrip() for line in sys.stdin]

    versions.sort(key=version_key)
    for version in versions:
        print(version)


if __name__ == "__main__":
    main()
