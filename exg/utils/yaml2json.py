#!/usr/bin/env python3

import argparse
import json
import sys

import yaml


def main() -> None:
    """
    Convert a YAML document to a JSON document.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("file", nargs="?")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "rb") as f:
            data = yaml.safe_load(f)
    else:
        data = yaml.safe_load(sys.stdin.buffer)

    print(json.dumps(data))


if __name__ == "__main__":
    main()
