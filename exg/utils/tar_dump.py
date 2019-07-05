#!/usr/bin/env python3

import argparse
import tarfile


def main() -> None:
    """
    List the content of a TAR archive.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("file")
    args = parser.parse_args()

    with tarfile.open(args.file) as tf:
        for member in tf.getmembers():
            print(f"{member.name} {member.mode:o} {member.size}")
            for name, value in member.pax_headers.items():
                print("  ", name, value)


if __name__ == "__main__":
    main()
