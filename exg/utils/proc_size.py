#!/usr/bin/env python3

import argparse

import psutil

from . import util


def visit_process(proc, depth):
    try:
        mem_info = proc.memory_full_info()
    except psutil.AccessDenied:
        mem_info = proc.memory_info()
    indent = " " * depth * 2
    rss = util.format_size(mem_info.rss)
    uss = util.format_size(getattr(mem_info, "uss", 0))
    print(f"{indent}{proc.pid} {proc.name()} {uss} {rss}")
    for child in proc.children():
        visit_process(child, depth + 1)


def main():
    """
    Show the amount of unique and total memory used by a process tree.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("name")
    args = parser.parse_args()

    roots = (
        p
        for p in psutil.process_iter(["name"])
        if p.info["name"] == args.name and p.parent().name() != args.name
    )
    for root in roots:
        visit_process(root, 0)


if __name__ == "__main__":
    main()
