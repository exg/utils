#!/usr/bin/env python3

from __future__ import annotations

import argparse
import mailbox
import os
import sys
import tarfile
from abc import ABC, abstractmethod
from pathlib import Path


class Reader(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def test(self, path: str) -> bool:
        pass

    @abstractmethod
    def read(self, path: str) -> set[str]:
        pass


class DirReader(Reader):
    def __init__(self) -> None:
        super().__init__("dir")

    def test(self, path: str) -> bool:
        return os.path.isdir(path)

    def read(self, path: str) -> set[str]:
        return {
            str(p.relative_to(path))
            for p in Path(path).rglob("*")
            if p.is_file()
        }


class FileReader(Reader):
    def __init__(self) -> None:
        super().__init__("file")

    def test(self, path: str) -> bool:
        return os.path.isfile(path)

    def read(self, path: str) -> set[str]:
        with open(path, encoding="latin-1") as f:
            return {line.rstrip("\n") for line in f}


class MailboxReader(Reader):
    def __init__(self) -> None:
        super().__init__("mailbox")

    def _open(self, path: str) -> mailbox.Maildir | mailbox.mbox | None:
        try:
            md = mailbox.Maildir(path, create=False)
            next(md.iterkeys())
        except Exception:
            pass
        else:
            return md
        try:
            mb = mailbox.mbox(path, create=False)
            next(mb.iterkeys())
        except Exception:
            pass
        else:
            return mb
        return None

    def test(self, path: str) -> bool:
        return self._open(path) is not None

    def read(self, path: str) -> set[str]:
        mb = self._open(path)
        assert mb is not None
        return {
            f'{msg["From"]}, {msg["Subject"]}, {msg["Message-ID"]}'
            for msg in mb
        }


class TarReader(Reader):
    def __init__(self) -> None:
        super().__init__("tar")

    def test(self, path: str) -> bool:
        try:
            with open(path, "rb") as f:
                f.seek(257)
                return f.read(5) == b"ustar"
        except Exception:
            return False

    def read(self, path: str) -> set[str]:
        with tarfile.open(path) as tf:
            return {member.name for member in tf.getmembers()}


def get_reader(arg: str) -> Reader | None:
    readers = (
        MailboxReader(),
        TarReader(),
        DirReader(),
        FileReader(),
    )

    for reader in readers:
        if reader.test(arg):
            return reader
    return None


def main() -> None:
    """
    Diff files as sets.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("file1")
    parser.add_argument("file2")
    args = parser.parse_args()

    reader1 = get_reader(args.file1)
    if not reader1:
        sys.exit(1)

    reader2 = get_reader(args.file2)
    if not reader2:
        sys.exit(1)

    s1 = reader1.read(args.file1)
    s2 = reader2.read(args.file2)

    print("--- " + args.file1)
    print("+++ " + args.file2)
    for v in sorted(s1 - s2):
        print("-", v)
    for v in sorted(s2 - s1):
        print("+", v)


if __name__ == "__main__":
    main()
