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

    home = os.path.expanduser("~")
    name = os.path.basename(args.file)
    cache_dir = os.path.join(home, ".cache", "mutt", "tmp")
    path = os.path.join(cache_dir, name)
    os.makedirs(cache_dir, mode=0o700, exist_ok=True)
    os.rename(args.file, path)
    subprocess.call([args.viewer, path])


if __name__ == "__main__":
    main()
