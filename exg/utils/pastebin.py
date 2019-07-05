#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from subprocess import check_call

from urllib3 import PoolManager


class Pastebin(ABC):
    @abstractmethod
    def paste(self, path: Path, *, expire: str, hash_name: bool) -> str:
        pass


class DpastePastebin(Pastebin):
    def __init__(self) -> None:
        self._pool = PoolManager()

    def paste(self, path: Path, *, expire: str, hash_name: bool) -> str:
        with open(path, "rb") as f:
            data: dict[str, str | bytes] = {
                "expiry_days": expire,
                "content": f.read(),
            }

        resp = self._pool.request(
            "POST",
            "http://dpaste.com/api/v2/",
            fields=data,
        )
        return f'{resp.headers["Location"]}.txt'


# expire values
# https://raw.githubusercontent.com/sayakb/sticky-notes/master/app/config/expire.php
class SnotesPastebin(Pastebin):
    def __init__(self, url: str):
        self._url = url
        self._pool = PoolManager()

    def paste(self, path: Path, *, expire: str, hash_name: bool) -> str:
        with open(path, encoding="utf-8") as f:
            data = {
                "expire": int(expire) * 86400,
                "language": "text",
                "data": f.read(),
            }

        resp = self._pool.request(
            "POST",
            self._url + "api/json/create",
            json=data,
        )
        return f'{self._url}{resp.json()["result"]["id"]}'


class SSHPastebin(Pastebin):
    def __init__(self, host: str, path: str, url: str):
        self._host = host
        self._path = path
        self._url = url

    def paste(self, path: Path, *, expire: str, hash_name: bool) -> str:
        if hash_name:
            m = hashlib.md5()
            m.update(bytes(path))
            name = m.hexdigest() + ".txt"
        else:
            name = re.sub(r"[ ()]", "_", path.name)
            if not path.suffix:
                name += ".txt"

        check_call(["scp", "-q", path, f"{self._host}:{self._path}/{name}"])
        check_call(["ssh", self._host, "chmod", "644", f"{self._path}/{name}"])

        return f"{self._url}/{name}"


def main() -> None:
    """
    Upload a file to a pastebin.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        "-e",
        dest="expire",
        default="1",
        choices=("1", "7", "30"),
        help="expire time in days",
    )
    parser.add_argument(
        "-p",
        dest="hash_name",
        action="store_false",
        help="preserve filename in pastebin link (ssh only)",
    )
    parser.add_argument(
        "-s",
        dest="server",
        default="default",
        help="use the specified server file",
    )
    parser.add_argument("file", nargs="?", type=Path)
    args = parser.parse_args()

    config_file = Path.home() / ".pastebin" / (args.server + ".json")
    with open(config_file, "rb") as f:
        config = json.load(f)

    pastebins = {
        "dpaste": DpastePastebin,
        "snotes": SnotesPastebin,
        "ssh": SSHPastebin,
    }
    pastebin = pastebins[config.pop("type")](**config)

    if args.file:
        if not args.file.is_file():
            sys.exit(1)
        url = pastebin.paste(
            args.file,
            expire=args.expire,
            hash_name=args.hash_name,
        )
    else:
        with tempfile.NamedTemporaryFile() as f:
            f.write(sys.stdin.buffer.read())
            f.flush()
            url = pastebin.paste(
                f.name,
                expire=args.expire,
                hash_name=args.hash_name,
            )
    print(url)


if __name__ == "__main__":
    main()
