#!/usr/bin/env python3

import argparse
import os
import subprocess


def main():
    """
    mutt mailcap helper to open attachments in the background.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("viewer", default="open", nargs="?")
    parser.add_argument("file")
    args = parser.parse_args()

    head, name = os.path.split(args.file)
    path = os.path.join(head, "att." + name)
    os.rename(args.file, path)
    subprocess.call([args.viewer, path])


if __name__ == "__main__":
    main()
