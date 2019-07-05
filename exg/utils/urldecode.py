#!/usr/bin/env python3

import argparse
import sys
from typing import BinaryIO
from urllib.parse import unquote_to_bytes


def decode(input_stream: BinaryIO, output_stream: BinaryIO) -> None:
    output_stream.write(unquote_to_bytes(input_stream.read()))


def main() -> None:
    """
    Decode a percent encoded sequence.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("file", nargs="?")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "rb") as f:
            decode(f, sys.stdout.buffer)
    else:
        decode(sys.stdin.buffer, sys.stdout.buffer)


if __name__ == "__main__":
    main()
