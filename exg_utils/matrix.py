#!/usr/bin/env python3

import argparse


def op_sum(iterable):
    count = 0
    for v in iterable:
        try:
            count += int(v)
        except ValueError:
            pass
    return str(count)


def op_mean(iterable):
    count = op_sum(iterable)
    return "%.2f" % (float(count) / len(iterable))


def main():
    """
    Process a matrix.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        "-s", dest="sep", default=" ", help="specify the input field separator"
    )
    parser.add_argument(
        "-t", dest="transpose", action="store_true", help="transpose matrix"
    )
    parser.add_argument(
        "--sum",
        dest="op",
        action="store_const",
        const=op_sum,
        help="reduce rows to the sum of their elements",
    )
    parser.add_argument(
        "--mean",
        dest="op",
        action="store_const",
        const=op_mean,
        help="reduce rows to the mean of their elements",
    )
    parser.add_argument("file")
    parser.add_argument(
        "indices",
        type=int,
        nargs="*",
        metavar="index",
        help="row index to process",
    )
    args = parser.parse_args()

    matrix = []
    cols = 0

    with open(args.file) as f:
        for line in f:
            line = line.rstrip("\n").split(args.sep)
            matrix.append(line)
            cols = max(len(line), cols)

    for r in matrix:
        if len(r) < cols:
            r.extend(" " for i in range(cols - len(r)))

    if args.transpose:
        matrix = zip(*matrix)

    for i, row in enumerate(matrix):
        if not args.indices or i in args.indices:
            if args.op:
                print(args.op(row))
            else:
                print(" ".join(row))


if __name__ == "__main__":
    main()
