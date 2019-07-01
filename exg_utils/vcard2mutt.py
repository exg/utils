#!/usr/bin/env python3

import argparse


# https://tools.ietf.org/html/rfc6350
def decode_N_value(value):
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
                raise ValueError("invalid character: {}".format(c))
            field += c
            state = 0
    return fields


class vCardParser:
    def __init__(self):
        self.state = 0
        self.line = ""
        self.contact = {}

    def _parse_line(self):
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
                self.contact[name] = decode_N_value(value)
            elif name == "EMAIL":
                self.contact[name] = value
        return None

    def parse(self, path):
        with open(path, "r", encoding="utf-8") as f:
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


def main():
    """
    Convert a vcard file to a mutt alias file.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("file")
    args = parser.parse_args()

    parser = vCardParser()
    contacts = parser.parse(args.file)
    for contact in contacts:
        last = contact["N"][0].replace(" ", "")
        if len(contact["N"]) > 1:
            first = contact["N"][-1]
            alias = "%s.%s" % (first[0:1], last)
        else:
            alias = last
        s = "alias %s %s <%s>" % (
            alias.lower(),
            " ".join(reversed(contact["N"])),
            contact["EMAIL"],
        )
        print(s)


if __name__ == "__main__":
    main()
