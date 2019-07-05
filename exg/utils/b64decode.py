#!/usr/bin/env python3

import argparse
import sys
from base64 import b64decode
from typing import BinaryIO


def decode(input_stream: BinaryIO, output_stream: BinaryIO) -> None:
    output_stream.write(b64decode(input_stream.read()))


def main() -> None:
    """
    Decode a Base64 encoded sequence.
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
