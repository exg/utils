#!/usr/bin/env python3

import argparse
import json
import re


class Index:
    def __init__(self) -> None:
        self.index: dict[str, int] = {}
        self.re = re.compile(r"([^\W\d_]\w+)\b")

    def add(self, line: str) -> None:
        for match in self.re.finditer(line):
            word = match.group(1)
            if word in self.index:
                self.index[word] += 1
            else:
                self.index[word] = 1

    def encode(self) -> str:
        return json.dumps(
            sorted(self.index, key=lambda x: self.index[x], reverse=True),
            indent=4,
        )


def main() -> None:
    """
    List the words contained in a file, sorted by frequency.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("file")
    args = parser.parse_args()

    index = Index()
    with open(args.file) as f:
        for line in f:
            index.add(line.rstrip())
    print(index.encode())


if __name__ == "__main__":
    main()
