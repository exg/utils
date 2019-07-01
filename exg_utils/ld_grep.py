#!/usr/bin/env python3

import argparse
import platform
import re
from subprocess import Popen, PIPE
from ctypes import Structure, c_uint8, c_uint16, c_uint32, c_uint64


class e_ident(Structure):
    _pack_ = 1
    _fields_ = (
        ("EI_MAG", c_uint8 * 4),
        ("EI_CLASS", c_uint8),
        ("EI_DATA", c_uint8),
        ("EI_VERSION", c_uint8),
        ("EI_OSABI", c_uint8),
        ("EI_ABIVERSION", c_uint8),
        ("EI_PAD", c_uint8 * 7),
    )


class elf_header(Structure):
    _pack_ = 1
    _fields_ = (
        ("e_ident", e_ident),
        ("e_type", c_uint16),
        ("e_machine", c_uint16),
        ("e_version", c_uint32),
        ("e_entry", c_uint64),
        ("e_phoff", c_uint64),
        ("e_shoff", c_uint64),
        ("e_flags", c_uint32),
        ("e_ehsize", c_uint16),
        ("e_phentsize", c_uint16),
        ("e_phnum", c_uint16),
        ("e_shentsize", c_uint16),
        ("e_shnum", c_uint16),
        ("e_shstrndx", c_uint16),
    )


def is_elf(path):
    with open(path, "rb") as f:
        data = f.read(128)
    if len(data) < 5:
        return False
    if data[4] == 2:
        if len(data) < 64:
            return False
        header = elf_header.from_buffer_copy(data[:64])
    else:
        return False
    return header.e_ident.EI_MAG[0:4] == [0x7F, 0x45, 0x4C, 0x46]


class mach_header(Structure):
    _fields_ = (
        ("magic", c_uint32),
        ("cputype", c_uint32),
        ("cpusubtype", c_uint32),
        ("filetype", c_uint32),
        ("ncmds", c_uint32),
        ("sizeofcmds", c_uint32),
        ("flags", c_uint32),
    )


def is_mach(path):
    with open(path, "rb") as f:
        data = f.read(128)
    if len(data) < 28:
        return False
    header = mach_header.from_buffer_copy(data[:28])
    return header.magic in (0xCFFAEDFE, 0xFEEDFACF)


_SETTINGS = {
    "Darwin": {
        "dumper": ("otool", "-L"),
        "name_re": re.compile(r"^([^\t]+):$"),
        "dep_re": re.compile(r"^\t+(.+) \(.*\)"),
        "filter": is_mach,
    },
    "Linux": {
        "dumper": ("readelf", "-d"),
        "name_re": re.compile(r"^File: (.*)"),
        "dep_re": re.compile(r".*Shared library: \[(.*)\]"),
        "filter": is_elf,
    },
}


def grep(paths, include_re):
    settings = _SETTINGS[platform.system()]
    paths = list(filter(settings["filter"], paths))
    if not paths:
        return
    cmd = list(settings["dumper"]) + paths
    with Popen(cmd, stdout=PIPE) as p:
        name = ""
        deps = []
        dump = False
        for line in p.stdout:
            line = line.decode("utf-8").rstrip()
            match = settings["name_re"].match(line)
            if match:
                if name and dump:
                    print(name, " ".join(deps))
                name = match.group(1)
                deps = []
                dump = False
            else:
                match = settings["dep_re"].match(line)
                if match:
                    dep = match.group(1)
                    deps.append(dep)
                    if include_re.search(dep):
                        dump = True
        if name and dump:
            yield name, deps


def main():
    """
    Grep dependencies of executable files.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("-p", "--pattern", default=".")
    parser.add_argument("files", metavar="file", nargs="+")
    args = parser.parse_args()
    for name, deps in grep(args.files, re.compile(args.pattern)):
        print(name, " ".join(deps))


if __name__ == "__main__":
    main()
