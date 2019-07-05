#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import sys
from collections.abc import MutableMapping
from pathlib import Path
from subprocess import check_call
from typing import cast

Cmd = list[str | Path]
Env = MutableMapping[str, str]


def get_config_dir() -> Path:
    return Path.home() / ".config" / Path(sys.argv[0]).name


def get_configure_command(srcdir: Path, options: Cmd) -> Cmd | None:
    configure = srcdir.resolve() / "configure"
    if configure.is_file():
        return cast(Cmd, [configure]) + options
    if (srcdir / "meson.build").is_file():
        return ["meson", "setup", *options, ".", srcdir]
    return None


def get_swid(srcdir: Path) -> str:
    name = srcdir.resolve().name.lower()
    return re.sub(r"(-[\d.]+|\.git)$", "", name)


def source_file(name: str, template: str, args: Cmd, env: Env) -> bool:
    path = get_config_dir() / (name + ".json")
    if not path.is_file():
        return False
    with open(path, "rb") as f:
        config = json.load(f)
    if template not in config:
        return False
    if "args" in config[template]:
        args.extend(config[template]["args"])
    if "env" in config[template]:
        env.update(config[template]["env"])
    return True


def add_prefix(prefix: Path, env: Env) -> None:
    include_dir = prefix / "include"
    lib_dir = prefix / "lib"
    share_dir = prefix / "share"

    cppflags = env["CPPFLAGS"].split(" ")
    cppflags += (
        f"-I{include_dir}",
        f"-I{include_dir / 'freetype2'}",
        f"-I{include_dir / 'db48'}",
    )
    env["CPPFLAGS"] = " ".join(cppflags)

    ldflags = env["LDFLAGS"].split(" ")
    ldflags += (
        f"-L{lib_dir}",
        f"-L{lib_dir / 'db48'}",
    )
    env["LDFLAGS"] = " ".join(ldflags)

    pkg_config_path = env["PKG_CONFIG_PATH"].split(":")
    pkg_config_path += (
        str(lib_dir / "pkgconfig"),
        str(share_dir / "pkgconfig"),
    )
    env["PKG_CONFIG_PATH"] = ":".join(pkg_config_path)


def main() -> None:
    """
    Configure a source directory build.
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
        type=Path,
        help="search for libraries in %(metavar)s",
    )
    parser.add_argument(
        "-t",
        "--template",
        help="read configure arguments and environment from template TEMPLATE",
    )
    parser.add_argument(
        "srcdir",
        metavar="directory",
        type=Path,
        help="source directory",
    )

    parser.add_argument(
        "args",
        nargs="*",
        metavar="arg",
        help="additional configure arguments",
    )
    args = parser.parse_args()
    env = os.environ
    options: Cmd = []
    source_file("defaults", platform.system(), options, env)
    source_file("defaults", platform.node(), options, env)
    for prefix in args.prefixes:
        if prefix.is_dir():
            add_prefix(prefix, env)
    swid = get_swid(args.srcdir)
    if args.template:
        if not source_file(swid, args.template, options, env):
            print(f"failed to read template {swid}.{args.template}")
            sys.exit(1)
    else:
        source_file(swid, "default", options, env)
    configure = get_configure_command(args.srcdir, options)
    if not configure:
        print("failed to detect configure command")
        sys.exit(1)
    if args.debug:
        for k, v in env.items():
            print(f"{k}={v}")
        print(" ".join(map(str, configure)))
    else:
        check_call(configure)


if __name__ == "__main__":
    main()
