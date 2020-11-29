#!/usr/bin/env python3

import argparse
import os.path
import hashlib
import json
import re
import sys
import tempfile
from subprocess import check_call
import requests


def pastebin_dpaste(fname, config):
    with open(fname, "rb") as f:
        data = {"expiry_days": config["expire"], "content": f.read()}

    resp = requests.post("http://dpaste.com/api/v2/", data)
    print(resp.headers["Location"] + ".txt")


# expire values
# https://raw.githubusercontent.com/sayakb/sticky-notes/master/app/config/expire.php
def pastebin_snotes(fname, config):
    with open(fname, "rb") as f:
        data = {
            "expire": int(config["expire"]) * 86400,
            "language": "text",
            "data": f.read(),
        }

    resp = requests.post(config["url"] + "api/json/create", json=data)
    print(config["url"] + resp.json()["result"]["id"])


def pastebin_ssh(fname, config):
    host = config["host"]
    path = config["path"]
    url = config["url"]
    if config["hash_name"]:
        m = hashlib.md5()
        m.update(fname.encode("latin-1"))
        name = m.hexdigest() + ".txt"
    else:
        name = os.path.basename(fname)
        name = re.sub(r"[ ()]", "_", name)
        (stub, ext) = os.path.splitext(name)
        if not ext:
            ext = ".txt"
        name = stub + ext

    check_call(["scp", "-q", fname, "%s:%s/%s" % (host, path, name)])
    check_call(["ssh", host, "chmod", "644", "%s/%s" % (path, name)])

    print("%s/%s" % (url, name))


def main():
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
    parser.add_argument("file", nargs="?")
    args = parser.parse_args()

    config_file = os.path.join("~", ".pastebin", args.server + ".json")
    with open(os.path.expanduser(config_file)) as f:
        config = json.load(f)
    config["expire"] = args.expire
    config["hash_name"] = args.hash_name
    paster = globals()["pastebin_" + config["type"]]

    if args.file:
        if not os.path.isfile(args.file):
            sys.exit(1)
        paster(args.file, config)
    else:
        with tempfile.NamedTemporaryFile() as f:
            f.write(sys.stdin.buffer.read())
            f.flush()
            paster(f.name, config)


if __name__ == "__main__":
    main()
