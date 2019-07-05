#!/usr/bin/env python3

import argparse
from collections.abc import Iterator

VLINE = "|"
HLINE = "\n\\hline\n"
COL = ["l"]


def justify(row: list[str], widths: list[int]) -> Iterator[str]:
    return (s.rjust(w + 2) for s, w in zip(row, widths))


def main() -> None:
    """
    Convert a matrix to a latex table.
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
    parser.add_argument("--header", help="specify the table header")
    parser.add_argument("--justify", action="store_true", help="justify fields")
    parser.add_argument(
        "--min",
        dest="hl_func",
        action="store_const",
        const=min,
        help="highlight minimum elements",
    )
    parser.add_argument(
        "--max",
        dest="hl_func",
        action="store_const",
        const=max,
        help="highlight maximum elements",
    )
    parser.add_argument("file")
    args = parser.parse_args()

    with open(args.file) as f:
        matrix = [line.rstrip("\n").split(args.sep) for line in f]

    if args.transpose:
        matrix = [list(i) for i in zip(*matrix)]

    if args.hl_func:
        for row in matrix:
            val = args.hl_func(map(float, row[1:]))
            for i, v in enumerate(row):
                if float(v) == val:
                    row[i] = r"\fbox{" + v + "}"

    if args.header:
        header = args.header.split()
        if len(header) == len(matrix[0]):
            matrix.insert(0, header)

    if args.transpose:
        matrix = [list(i) for i in zip(*matrix)]

    if args.justify:
        widths = [
            max(len(str(r[i])) for r in matrix) for i in range(len(matrix[0]))
        ]
        lines = [" & ".join(justify(r, widths)) + r" \\" for r in matrix]
    else:
        lines = [" & ".join(r) + r" \\" for r in matrix]

    print(r"\begin{tabular}{|" + VLINE.join(COL * len(matrix[0])) + "|}")
    print(r"\hline")

    print(HLINE.join(lines))

    print(r"\hline")
    print(r"\end{tabular}")


if __name__ == "__main__":
    main()
