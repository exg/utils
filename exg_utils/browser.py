#!/usr/bin/env python3

import argparse
import platform
import subprocess


def main():
    """
    Open a URL in a new browser window.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("url")
    args = parser.parse_args()

    if platform.system() == "Darwin":
        subprocess.call(("open", args.url))
    else:
        subprocess.call(("chromium", "--new-window", args.url))


if __name__ == "__main__":
    main()
