#!/usr/bin/env python3

import argparse
import json
import os
import re
import tempfile
import sys
import urllib.parse
from subprocess import check_call, Popen, PIPE


def get_config_dir():
    home = os.path.expanduser("~")
    name = os.path.basename(sys.argv[0])
    return os.path.join(home, ".config", name)


def spec_split(spec):
    spec_re = re.compile(r"(?:([^/:]*):)?(.*)")
    match = spec_re.match(spec)
    return match.group(1), match.group(2)


def spec_join(host, path):
    if host:
        return ":".join((host, path))
    return path


def encode_path(path):
    return urllib.parse.quote_from_bytes(path)


def decode_path(path):
    return urllib.parse.unquote(path, encoding="latin-1")


def source_file(name):
    path = os.path.join(get_config_dir(), name + ".json")
    with open(path) as f:
        return json.load(f)


def create_index(root, rsync_cmd):
    tempdir = tempfile.TemporaryDirectory()
    cmd = list(rsync_cmd)
    cmd.extend(["-n", r"--out-format=%n", root, tempdir.name])
    index = {}
    with Popen(cmd, stdout=PIPE) as p:
        for line in p.stdout:
            line = line.rstrip()
            path = root.encode("latin-1") + line
            if os.path.isfile(path):
                ino = os.lstat(path).st_ino
                index[str(ino)] = encode_path(line)
    return index


def rename_files(debug, root, old_index, new_index):
    moves = []
    moves2 = []
    tempdir = tempfile.TemporaryDirectory(dir=root)
    for ino in set(old_index.keys()) & set(new_index.keys()):
        old_path = decode_path(old_index[ino])
        new_path = decode_path(new_index[ino])
        if old_path != new_path:
            if debug:
                print("{0}{1} => {0}{2}".format(root, old_path, new_path))
            else:
                moves.append(
                    (
                        os.path.join(root, old_path),
                        os.path.join(tempdir.name, new_path),
                    )
                )
                moves2.append(
                    (
                        os.path.join(tempdir.name, new_path),
                        os.path.join(root, new_path),
                    )
                )
    if not debug:
        for move in moves + moves2:
            dst_dir = os.path.dirname(move[1])
            os.makedirs(dst_dir.encode("latin-1"), exist_ok=True)
            os.rename(move[0].encode("latin-1"), move[1].encode("latin-1"))


def mirror(debug, lspec, rspec, rsync_cmd):
    lhost, lpath = spec_split(lspec)
    rhost, rpath = spec_split(rspec)

    if not lpath.endswith(os.sep):
        name = os.path.basename(lpath)
        lpath += os.sep
        if rpath:
            rpath = os.path.join(rpath, name)
        else:
            rpath = name
        lspec = spec_join(lhost, lpath)
        rspec = spec_join(rhost, rpath)

    if not rpath.endswith(os.sep):
        rpath += os.sep

    index_file = (rpath + ".ino-index.json").encode("latin-1")
    lindex = None
    if not lhost and not rhost and os.path.isdir(lpath):
        lindex = create_index(lpath, rsync_cmd)
        if os.path.isfile(index_file):
            with open(index_file) as f:
                rindex = json.load(f)
            rename_files(debug, rpath, rindex, lindex)
    rsync_cmd.extend(["-v", lspec, rspec])
    if debug:
        print(rsync_cmd)
    else:
        check_call(rsync_cmd)
        if lindex:
            with open(index_file, "w") as f:
                json.dump(lindex, f, indent=4)


def main():
    """
    Synchronize two directories using rsync, with support for
    inode-based file rename detection.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument(
        "-p",
        "--pull",
        action="store_true",
        help="pull changes from destination",
    )
    parser.add_argument(
        "-t", "--template", help="read rsync arguments from template TEMPLATE"
    )
    opts, args = parser.parse_known_args()
    ignore_file = os.path.join(os.path.expanduser("~"), ".ignore")
    rsync_cmd = [
        "rsync",
        "-haOP",
        "--no-p",
        "--modify-window=1",
        "--exclude-from=%s" % ignore_file,
        "--filter=dir-merge,- .ignore",
    ]
    lspec, rspec = None, None
    if opts.template:
        try:
            template = source_file(opts.template)
            if "src" in template:
                lspec = decode_path(template["src"])
            if "dest" in template:
                rspec = decode_path(template["dest"])
            if "args" in template:
                rsync_cmd.extend(template["args"])
        except:
            print("failed to read template %s" % opts.template)
            sys.exit(1)
    if not rspec:
        rspec = args.pop()
    if not lspec:
        lspec = args.pop()
    if not lspec or not rspec:
        print("local or remote spec missing")
        sys.exit(1)
    if opts.pull:
        lspec, rspec = rspec, lspec
    rsync_cmd.extend(args)
    mirror(opts.debug, lspec, rspec, rsync_cmd)


if __name__ == "__main__":
    main()
