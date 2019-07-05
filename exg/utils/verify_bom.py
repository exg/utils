#!/usr/bin/env python3

from __future__ import annotations

import argparse
import plistlib
import re
import sys
from pathlib import Path
from subprocess import PIPE, Popen
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator


def checksum(paths: list[str]) -> dict[str, str]:
    cmd = ["cksum", *paths]
    data = {}
    with Popen(cmd, stdout=PIPE) as p:
        assert p.stdout is not None
        for line in p.stdout:
            fields = line.decode("utf-8").rstrip().split(" ", maxsplit=2)
            data[fields[2]] = fields[0]
    return data


def read_bom(bom_path: Path, pattern: str) -> dict[str, str]:
    include_re = re.compile(pattern)
    plist_path = bom_path.with_suffix(".plist")
    with open(plist_path, "rb") as f:
        plist_data = plistlib.load(f)
    prefix = Path("/") / (plist_data["InstallPrefixPath"] or "")
    print(f"InstallPrefixPath={prefix}", file=sys.stderr)
    cmd: list[str | Path] = ["lsbom", "-f", "-p", "fc", bom_path]
    data = {}
    with Popen(cmd, stdout=PIPE) as p:
        assert p.stdout is not None
        for line in p.stdout:
            fields = line.decode("utf-8").rstrip().split("\t")
            path = str(prefix / fields[0])
            if include_re.search(path):
                data[path] = fields[1]
    return data


def verify_bom(bom_path: Path, pattern: str) -> Iterator[str]:
    bom_data = read_bom(bom_path, pattern)
    cksum_data = checksum(list(bom_data.keys()))
    for path in bom_data:
        if bom_data[path] != cksum_data[path]:
            yield path


def main() -> None:
    """
    Verify the integrity of the files indexed by a BOM file.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        "-p",
        "--pattern",
        default=".",
        help="verify only files matching the regexp PATTERN",
    )
    parser.add_argument("file", type=Path)
    args = parser.parse_args()

    for path in verify_bom(args.file, args.pattern):
        print(path)


if __name__ == "__main__":
    main()
