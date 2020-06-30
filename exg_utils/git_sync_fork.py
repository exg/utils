#!/usr/bin/env python3

import argparse
from subprocess import check_call, Popen, PIPE


def get_refs(pattern):
    refs = {}
    n = pattern.count("/") + 1
    cmd = (
        "git",
        "for-each-ref",
        "--format=%(objectname)%09%(refname:strip={})".format(n),
        pattern,
    )
    with Popen(cmd, stdout=PIPE) as p:
        for line in p.stdout:
            obj, ref = line.decode("latin-1").rstrip("\n").split("\t")
            refs[obj] = ref
    return refs


def main():
    """
    Sync a git fork with the upstream repository.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("--fork", default="origin")
    parser.add_argument("--upstream", default="upstream")
    args = parser.parse_args()

    check_call(["git", "fetch", "-q", args.fork])
    check_call(["git", "fetch", "-q", args.upstream])

    f_branches = get_refs("refs/remotes/{}".format(args.fork))
    u_branches = get_refs("refs/remotes/{}".format(args.upstream))
    l_branches = get_refs("refs/heads")

    for obj in set(f_branches) - set(u_branches) - set(l_branches):
        branch = f_branches[obj]
        print("push {} :{}".format(args.fork, branch))

    for obj in set(u_branches) - set(f_branches):
        branch = u_branches[obj]
        print("push {} {}:refs/heads/{}".format(args.fork, obj, branch))


if __name__ == "__main__":
    main()
