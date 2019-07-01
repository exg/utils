#!/usr/bin/env python3

import argparse
import re
from subprocess import Popen, PIPE


def get_packages():
    package_re = re.compile(r"^Package: (.*)")
    version_re = re.compile(r"^Version: (.*)-")
    state = 0
    with Popen(["apt-cache", "dumpavail"], stdout=PIPE) as p:
        for line in p.stdout:
            line = line.decode("utf-8")
            if state == 0:
                match = package_re.match(line)
                if match:
                    name = match.group(1)
                    state = 1
            else:
                match = version_re.match(line)
                if match:
                    version = match.group(1)
                    yield name, version
                    state = 0


def main():
    """
    List the available debian packages in a one-per-line format.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.parse_args()

    for name, version in get_packages():
        print(name + " " + version)


if __name__ == "__main__":
    main()
