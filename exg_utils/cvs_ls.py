#!/usr/bin/env python3

import argparse
import os
import re


def get_cvs_repo(root):
    try:
        with open(os.path.join(root, "CVS", "Repository")) as f:
            return f.read().rstrip()
    except:
        return None


def get_cvs_entries(root):
    try:
        files = []
        dirs = ["CVS"]
        with open(os.path.join(root, "CVS", "Entries")) as f:
            for line in f:
                m = re.search(r"^(D)?/([^/]+)/.*$", line)
                if m:
                    if m.group(1):
                        dirs.append(m.group(2))
                    else:
                        files.append(m.group(2))
        return files, dirs
    except:
        return [], []


def get_files(others):
    top_repo = get_cvs_repo(".")
    if not top_repo:
        return
    for root, dirs, files in os.walk("."):
        repo = get_cvs_repo(root)
        if repo and os.path.normpath(os.path.join(top_repo, root)) == repo:
            entries = get_cvs_entries(root)
            if others:
                _files = list(set(files) - set(entries[0]))
                _files += list(set(dirs) - set(entries[1]))
            else:
                _files = entries[0]
            for f in _files:
                yield os.path.normpath(os.path.join(root, f))


def main():
    """
    List the files tracked by a CVS checkout.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        "-o", "--others", action="store_true", help="show untracked files"
    )
    args = parser.parse_args()

    for f in get_files(args.others):
        print(f)


if __name__ == "__main__":
    main()
