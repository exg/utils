#!/usr/bin/env python3

import argparse
import re
from collections.abc import Iterator
from pathlib import Path


def get_cvs_repo(root: Path) -> Path:
    with open(root / "CVS/Repository") as f:
        return Path(f.read().rstrip())


def get_cvs_entries(
    root: Path,
    *,
    include_dirs: bool = False,
) -> Iterator[Path]:
    with open(root / "CVS/Entries") as f:
        for line in f:
            m = re.search(r"^(D)?/([^/]+)/.*$", line)
            if m and (include_dirs or not m.group(1)):
                yield root / m.group(2)


def get_files(*, others: bool) -> Iterator[Path]:
    top_root = Path()
    top_repo = get_cvs_repo(top_root)
    if not top_repo:
        return
    for cvs_dir in top_root.rglob("CVS"):
        root = cvs_dir.parent
        repo = get_cvs_repo(root)
        if repo and top_repo / str(root) == repo:
            if others:
                entries = set(get_cvs_entries(root, include_dirs=True))
                yield from (
                    child
                    for child in root.iterdir()
                    if child != cvs_dir and child not in entries
                )
            else:
                yield from get_cvs_entries(root)


def main() -> None:
    """
    List the files tracked by a CVS checkout.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        "-o",
        "--others",
        action="store_true",
        help="show untracked files",
    )
    args = parser.parse_args()

    for f in get_files(others=args.others):
        print(f)


if __name__ == "__main__":
    main()
