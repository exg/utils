#!/usr/bin/env python3

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from collections.abc import Iterator


class Contact(TypedDict, total=False):
    N: list[str]
    EMAIL: str


# https://tools.ietf.org/html/rfc6350
def decode_N_value(value: str) -> list[str]:
    state = 0
    field = ""
    fields = []
    for c in value:
        if state == 0:
            if c == "\\":
                state = 1
            elif c == ";":
                if field:
                    fields.append(field)
                field = ""
            else:
                field += c
        else:
            if c not in ("\\", ";"):
                raise ValueError
            field += c
            state = 0
    return fields


class vCardParser:
    def __init__(self) -> None:
        self.state = 0
        self.line = ""
        self.contact: Contact = {}

    def _parse_line(self) -> Contact | None:
        if not self.line:
            return None
        key, value = self.line.split(":", maxsplit=1)
        fields = key.split(";")
        try:
            _, name = fields[0].split(".", maxsplit=1)
        except ValueError:
            name = fields[0]
        if self.state == 0:
            if name == "BEGIN" and value == "VCARD":
                self.state = 1
        elif self.state == 1:
            if name == "END" and value == "VCARD":
                contact = self.contact
                self.contact = {}
                self.state = 0
                if "EMAIL" in contact:
                    return contact
            elif name == "N":
                self.contact["N"] = decode_N_value(value)
            elif name == "EMAIL":
                self.contact["EMAIL"] = value
        return None

    def parse(self, path: str) -> Iterator[Contact]:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line[0] in (" ", "\t"):
                    self.line += line[1:].rstrip()
                else:
                    contact = self._parse_line()
                    if contact:
                        yield contact
                    self.line = line.rstrip()
        contact = self._parse_line()
        if contact:
            yield contact
        self.state = 0
        self.line = ""
        self.contact = {}


def main() -> None:
    """
    Convert a vcard file to a mutt alias file.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("file")
    args = parser.parse_args()

    vcard_parser = vCardParser()
    contacts = vcard_parser.parse(args.file)
    for contact in contacts:
        last = contact["N"][0].replace(" ", "")
        if len(contact["N"]) > 1:
            first = contact["N"][-1]
            alias = f"{first[0]}.{last}".lower()
        else:
            alias = last.lower()
        name = " ".join(reversed(contact["N"]))
        email = contact["EMAIL"]
        print(f"alias {alias} {name} <{email}>")


if __name__ == "__main__":
    main()
