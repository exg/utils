#!/usr/bin/env python3

import argparse
import re
from collections.abc import Iterator
from subprocess import PIPE, Popen


def get_packages() -> Iterator[tuple[str, str]]:
    package_re = re.compile(r"^Package: (.*)")
    version_re = re.compile(r"^Version: (.*)-")
    state = 0
    with Popen(["apt-cache", "dumpavail"], stdout=PIPE) as p:
        assert p.stdout is not None
        for line in p.stdout:
            if state == 0:
                match = package_re.match(line.decode("utf-8"))
                if match:
                    name = match.group(1)
                    state = 1
            else:
                match = version_re.match(line.decode("utf-8"))
                if match:
                    version = match.group(1)
                    yield name, version
                    state = 0


def main() -> None:
    """
    List the available debian packages in a one-per-line format.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.parse_args()

    for name, version in get_packages():
        print(name + " " + version)


if __name__ == "__main__":
    main()
