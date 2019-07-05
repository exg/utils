#!/usr/bin/env python3

import argparse
import tarfile

from . import util


def main() -> None:
    """
    Show the content size in bytes of a TAR archive.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("--prefix", default="")
    parser.add_argument("file")
    args = parser.parse_args()

    with tarfile.open(args.file) as tf:
        size = 0
        for member in tf.getmembers():
            if member.name.startswith(args.prefix):
                size += member.size
        print(util.format_size(size))


if __name__ == "__main__":
    main()
