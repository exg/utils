#!/usr/bin/env python3

import argparse
import contextlib


def op_sum(row: list[str]) -> str:
    count = 0
    for v in row:
        with contextlib.suppress(ValueError):
            count += int(v)
    return str(count)


def op_mean(row: list[str]) -> str:
    count = op_sum(row)
    mean = float(count) / len(row)
    return f"{mean:.2f}"


def main() -> None:
    """
    Process a matrix.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        "-s",
        dest="sep",
        default=" ",
        help="specify the input field separator",
    )
    parser.add_argument(
        "-t",
        dest="transpose",
        action="store_true",
        help="transpose matrix",
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

    with open(args.file) as f:
        matrix = [line.rstrip("\n").split(args.sep) for line in f]
    cols = max(len(row) for row in matrix)

    for r in matrix:
        if len(r) < cols:
            r.extend(" " for i in range(cols - len(r)))

    for i, row in enumerate(zip(*matrix) if args.transpose else matrix):
        if not args.indices or i in args.indices:
            if args.op:
                print(args.op(row))
            else:
                print(" ".join(row))


if __name__ == "__main__":
    main()
