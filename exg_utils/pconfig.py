#!/usr/bin/env python3

import argparse
import json
import os
import os.path
import platform
import re
import sys
from subprocess import check_call


def get_config_dir():
    home = os.path.expanduser("~")
    name = os.path.basename(sys.argv[0])
    return os.path.join(home, ".config", name)


def get_swid(srcdir):
    name = os.path.basename(os.path.realpath(srcdir)).lower()
    name = re.sub(r"-[\d.]+$", "", name)
    name = re.sub(r"\.git$", "", name)
    return name


def source_file(name, template, args, env):
    path = os.path.join(get_config_dir(), name + ".json")
    if not os.path.isfile(path):
        return False
    with open(path) as f:
        config = json.load(f)
    if template not in config:
        return False
    if "args" in config[template]:
        args.extend(config[template]["args"])
    if "env" in config[template]:
        env.update(config[template]["env"])
    return True


def add_prefix(prefix, env):
    include_dir = os.path.join(prefix, "include")
    lib_dir = os.path.join(prefix, "lib")
    share_dir = os.path.join(prefix, "share")
    env["CPPFLAGS"] += " -I%s -I%s -I%s" % (
        include_dir,
        os.path.join(include_dir, "freetype2"),
        os.path.join(include_dir, "db48"),
    )
    env["LDFLAGS"] += " -L%s -L%s" % (lib_dir, os.path.join(lib_dir, "db48"))
    env["PKG_CONFIG_PATH"] += ":%s:%s" % (
        os.path.join(lib_dir, "pkgconfig"),
        os.path.join(share_dir, "pkgconfig"),
    )


def main():
    """
    Configure an autoconf-based source directory.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument(
        "-p",
        "--prefix",
        dest="prefixes",
        default=[],
        action="append",
        metavar="PREFIX",
        help="search for libraries in %(metavar)s",
    )
    parser.add_argument(
        "-t",
        "--template",
        help="read configure arguments and environment from template TEMPLATE",
    )
    parser.add_argument("srcdir", metavar="directory", help="source directory")
    parser.add_argument(
        "args", nargs="*", metavar="arg", help="additional configure arguments"
    )
    args = parser.parse_args()
    configure = [os.path.join(args.srcdir, "configure")]
    env = os.environ
    if not os.path.isfile(configure[0]):
        print("missing configure")
        sys.exit(1)
    source_file("defaults", platform.system(), configure, env)
    source_file("defaults", platform.node(), configure, env)
    for prefix in args.prefixes:
        if os.path.isdir(prefix):
            add_prefix(prefix, env)
    swid = get_swid(args.srcdir)
    if args.template:
        if not source_file(swid, args.template, configure, env):
            print("failed to read template %s.%s" % (swid, args.template))
            sys.exit(1)
    else:
        source_file(swid, "default", configure, env)
    configure += args.args
    if args.debug:
        for k, v in env.items():
            print("%s=%s" % (k, v))
        print(" ".join(configure))
    else:
        check_call(configure)


if __name__ == "__main__":
    main()
