#!/usr/bin/env python3

import argparse
import json
import mailbox
import os
import sys
import tarfile
from subprocess import Popen, PIPE


class Reader:
    def __init__(self, name):
        self.name = name

    def test(self, arg):
        return False


class DirReader(Reader):
    def __init__(self):
        super().__init__("dir")

    def test(self, arg):
        return os.path.isdir(arg)

    def read(self, path, fields):
        s = set()
        for root, dirs, files in os.walk(path):
            root = os.path.relpath(root, path)
            for f in files:
                s.add(os.path.join(root, f))
        return s


class FileReader(Reader):
    def __init__(self):
        super().__init__("file")

    def test(self, arg):
        return os.path.isfile(arg)

    def read(self, path, fields):
        s = set()
        with open(path, encoding="latin-1") as f:
            for line in f:
                s.add(line.rstrip("\n"))
        return s


class GitReader(Reader):
    def __init__(self):
        super().__init__("git")

    def read(self, branch, fields):
        s = set()
        cmd = ("git", "log", "--pretty=%an %ai %s", branch)
        with Popen(cmd, stdout=PIPE) as p:
            for line in p.stdout:
                s.add(line.decode("latin-1").rstrip("\n"))
        return s


class JSONReader(Reader):
    def __init__(self):
        super().__init__("json")

    def _find(self, obj, fields, out):
        if type(obj) == dict:
            for k in obj:
                if type(obj[k]) in (list, dict):
                    self._find(obj[k], fields, out)
                elif k in fields:
                    out.add(obj[k])
        if type(obj) == list:
            for i in obj:
                if type(i) in (list, dict):
                    self._find(i, fields, out)

    def read(self, path, fields):
        s = set()
        with open(path) as f:
            obj = json.load(f)
            self._find(obj, fields, s)
        return s


class MailboxReader(Reader):
    def __init__(self):
        super().__init__("mailbox")

    def _open(self, path):
        try:
            mb = mailbox.Maildir(path, create=False)
            next(mb.iterkeys())
            return mb
        except:
            pass
        try:
            mb = mailbox.mbox(path, create=False)
            next(mb.iterkeys())
            return mb
        except:
            pass
        return None

    def test(self, arg):
        return self._open(arg) is not None

    def read(self, path, fields):
        s = set()
        mb = self._open(path)
        for message in mb:
            s.add((message["From"], message["Subject"], message["Message-ID"]))
        return s


class TarReader(Reader):
    def __init__(self):
        super().__init__("tar")

    def test(self, arg):
        try:
            with open(arg, "rb") as f:
                f.seek(257)
                return f.read(5) == b"ustar"
        except:
            return False

    def read(self, path, fields):
        s = set()
        with tarfile.open(path) as tf:
            for member in tf.getmembers():
                s.add(member.name)
        return s


def get_reader(arg1, arg2, name):
    readers = (
        GitReader(),
        JSONReader(),
        MailboxReader(),
        TarReader(),
        DirReader(),
        FileReader(),
    )

    for reader in readers:
        if name:
            if reader.name == name:
                return reader
        else:
            if reader.test(arg1) and reader.test(arg2):
                return reader
    return None


def main():
    """
    Diff files as sets.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        "-f",
        "--field",
        dest="fields",
        default=[],
        action="append",
        metavar="FIELD",
        help="include only elements with name %(metavar)s",
    )
    parser.add_argument(
        "-r", "--reader", help="process files with reader READER"
    )
    parser.add_argument("file1")
    parser.add_argument("file2")
    args = parser.parse_args()

    reader = get_reader(args.file1, args.file2, args.reader)
    if not reader:
        sys.exit(1)

    s1 = reader.read(args.file1, args.fields)
    s2 = reader.read(args.file2, args.fields)

    print("--- " + args.file1)
    print("+++ " + args.file2)
    for v in sorted(s1 - s2):
        print("-", v)
    for v in sorted(s2 - s1):
        print("+", v)


if __name__ == "__main__":
    main()
