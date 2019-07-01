#!/usr/bin/env python3

import argparse
import sys
from base64 import decode


def main():
    """
    Decode a Base64 encoded sequence.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("file", nargs="?")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r") as f:
            decode(f, sys.stdout.buffer)
    else:
        decode(sys.stdin, sys.stdout.buffer)


if __name__ == "__main__":
    main()
