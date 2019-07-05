#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
import urllib.parse
from dataclasses import dataclass
from functools import cached_property
from subprocess import PIPE, Popen, run


@dataclass
class Address:
    host: str | None
    path: str

    def serialize(self) -> str:
        if self.host is not None:
            return f"{self.host}:{self.path}"
        return self.path


@dataclass
class Rsync:
    args: list[str]
    src: Address
    dest: Address

    def __post_init__(self) -> None:
        self.args = [
            "rsync",
            "--archive",
            "--delete",
            "--exclude=.DS_Store",
            "--filter=dir-merge,- .ignore",
            "--human-readable",
            "--modify-window=1",
            "--no-group",
            "--no-perms",
            "--no-specials",
            "--omit-dir-times",
            "--partial",
            "--progress",
            *self.args,
        ]

        if not self.src.path.endswith(os.sep):
            name = os.path.basename(self.src.path)
            self.src.path += os.sep
            if self.dest.path:
                self.dest.path = os.path.join(self.dest.path, name)
            else:
                self.dest.path = name

    @cached_property
    def _dest_index_path(self) -> bytes:
        return os.fsencode(os.path.join(self.dest.path, ".ino-index.json"))

    def _create_index(self) -> dict[str, str]:
        tempdir = tempfile.TemporaryDirectory()
        cmd = [
            *self.args,
            "-8",
            "-n",
            r"--out-format=%n",
            self.src.path,
            tempdir.name,
        ]
        index = {}
        with Popen(cmd, stdout=PIPE) as p:
            assert p.stdout is not None
            for line in p.stdout:
                rel_path = os.fsdecode(line.rstrip())
                path = os.fsencode(os.path.join(self.src.path, rel_path))
                if os.path.isfile(path):
                    ino = os.lstat(path).st_ino
                    index[str(ino)] = rel_path
        return index

    def _create_link_dest_dir(
        self,
        src_index: dict[str, str],
    ) -> tempfile.TemporaryDirectory[str]:
        dest_index = {}
        if os.path.isfile(self._dest_index_path):
            with open(self._dest_index_path, "rb") as f:
                dest_index = json.load(f)

        tempdir = tempfile.TemporaryDirectory(
            dir=os.path.dirname(self.dest.path),
        )
        for ino in set(dest_index.keys()) & set(src_index.keys()):
            dest_path = dest_index[ino]
            src_path = src_index[ino]
            if dest_path != src_path:
                src = os.path.join(self.dest.path, dest_path)
                dst = os.path.join(tempdir.name, src_path)
                os.makedirs(os.fsencode(os.path.dirname(dst)), exist_ok=True)
                os.link(os.fsencode(src), os.fsencode(dst))
        return tempdir

    def _run(self, *, dry_run: bool, link_dest: str | None) -> None:
        cmd = [
            *self.args,
            *(["-n"] if dry_run else []),
            *(["--link-dest", link_dest] if link_dest is not None else []),
            "-v",
            self.src.serialize(),
            self.dest.serialize(),
        ]
        run(cmd, check=True)

    def mirror(self, *, dry_run: bool) -> None:
        if (
            not self.src.host
            and not self.dest.host
            and os.path.isdir(self.src.path)
        ):
            src_index = self._create_index()
            tempdir = self._create_link_dest_dir(src_index)
            self._run(dry_run=dry_run, link_dest=os.path.abspath(tempdir.name))

            if not dry_run:
                with open(self._dest_index_path, "w", encoding="utf-8") as f:
                    json.dump(src_index, f, indent=4)
        else:
            self._run(dry_run=dry_run, link_dest=None)


def _parse_address(address: str) -> Address:
    address = os.fsdecode(urllib.parse.unquote_to_bytes(address))
    address_re = re.compile(r"(?:([^/:]*):)?(.*)")
    match = address_re.match(address)
    assert match is not None
    return Address(match.group(1), match.group(2))


def main() -> None:
    """
    Synchronize two directories using rsync, with support for
    inode-based file rename detection.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("src", type=_parse_address)
    parser.add_argument("dest", type=_parse_address)
    known_args, args = parser.parse_known_args()

    rsync = Rsync(args, known_args.src, known_args.dest)
    rsync.mirror(dry_run=known_args.dry_run)


if __name__ == "__main__":
    main()
