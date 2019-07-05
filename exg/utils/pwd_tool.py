#!/usr/bin/env python3

import argparse
import platform
import subprocess
import sys


def lookup(user: str) -> int:
    if platform.system() == "Darwin":
        cmd = ["security", "find-internet-password", "-a", user, "-w"]
    else:
        cmd = ["secret-tool", "lookup", "user", user]
    return subprocess.call(cmd)


def store(user: str, host: str) -> int:
    if platform.system() == "Darwin":
        cmd = [
            "security",
            "add-internet-password",
            "-r",
            "smtp",
            "-a",
            user,
            "-s",
            host,
            "-w",
        ]
    else:
        cmd = [
            "secret-tool",
            "store",
            "--label",
            host,
            "service",
            "smtp",
            "user",
            user,
            "host",
            host,
        ]
    return subprocess.call(cmd)


def main() -> None:
    """
    Manage mail passwords in the system keychain.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    subparsers = parser.add_subparsers(dest="command")
    parser_lookup = subparsers.add_parser("lookup")
    parser_lookup.add_argument("user")
    parser_store = subparsers.add_parser("store")
    parser_store.add_argument("user")
    parser_store.add_argument("host")
    args = parser.parse_args()

    if args.command == "lookup":
        sys.exit(lookup(args.user))
    else:
        sys.exit(store(args.user, args.host))


if __name__ == "__main__":
    main()
