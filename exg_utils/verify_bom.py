#!/usr/bin/env python3

import argparse
import xml.etree.ElementTree as ET
import os
import re
import sys
from subprocess import check_output, Popen, PIPE
from . import util


def get_install_prefix(plist_path):
    cmd = ["plutil", "-convert", "xml1", "-o", "-", plist_path]
    with Popen(cmd, stdout=PIPE) as p:
        tree = ET.parse(p.stdout)
    prefix = util.xml_dict_get(tree, "InstallPrefixPath")
    return os.path.join("/", prefix or "")


def checksum(path):
    cmd = ["cksum", path]
    output = check_output(cmd)
    return output.decode("utf-8").split(" ")[0]


def verify_bom(bom_path, pattern):
    include_re = re.compile(pattern)
    plist_path = os.path.splitext(bom_path)[0] + ".plist"
    prefix = get_install_prefix(plist_path)
    print("InstallPrefixPath={}".format(prefix), file=sys.stderr)
    cmd = ["lsbom", "-f", "-p", "fc", bom_path]
    with Popen(cmd, stdout=PIPE) as p:
        for line in p.stdout:
            fields = line.decode("utf-8").rstrip().split("\t")
            path = os.path.join(prefix, fields[0])
            if include_re.search(path):
                crc = checksum(path)
                if crc != fields[1]:
                    yield path


def main():
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
    parser.add_argument("file")
    args = parser.parse_args()

    for path in verify_bom(args.file, args.pattern):
        print(path)


if __name__ == "__main__":
    main()
