from __future__ import annotations

import struct
from ctypes import BigEndianStructure, LittleEndianStructure, c_uint32, sizeof
from dataclasses import dataclass

_mach_header_fields = (
    ("magic", c_uint32),
    ("cputype", c_uint32),
    ("cpusubtype", c_uint32),
    ("filetype", c_uint32),
    ("ncmds", c_uint32),
    ("sizeofcmds", c_uint32),
    ("flags", c_uint32),
    ("pad", c_uint32),
)


class mach_header_le(LittleEndianStructure):
    _fields_ = _mach_header_fields


class mach_header_be(BigEndianStructure):
    _fields_ = _mach_header_fields


class load_command_le(LittleEndianStructure):
    _pack_ = 1
    _fields_ = (("cmd", c_uint32), ("cmdsize", c_uint32))


class load_command_be(BigEndianStructure):
    _pack_ = 1
    _fields_ = (("cmd", c_uint32), ("cmdsize", c_uint32))


_dylib_fields = (
    ("name", c_uint32),
    ("timestamp", c_uint32),
    ("current_version", c_uint32),
    ("compatibility_version", c_uint32),
)


class dylib_le(LittleEndianStructure):
    _pack_ = 1
    _fields_ = _dylib_fields


class dylib_be(BigEndianStructure):
    _pack_ = 1
    _fields_ = _dylib_fields


def read_struct(stream, stype):
    data = stream.read(sizeof(stype))
    if len(data) < sizeof(stype):
        return None
    return stype.from_buffer_copy(data)


@dataclass
class Layout:
    load_command: LittleEndianStructure | BigEndianStructure
    dylib: LittleEndianStructure | BigEndianStructure


class MachOInfo:
    def __init__(self, stream):
        self._stream = stream
        self._header = None
        self._read_header()
        if not self._header:
            raise ValueError

    def _read_header(self):
        self._stream.seek(0)
        data = self._stream.peek(4)
        if len(data) < 4:
            return
        magic = struct.unpack("I", data[:4])[0]
        if magic == 0xFEEDFACF:
            self._header = read_struct(self._stream, mach_header_le)
            self._layout = Layout(load_command_le, dylib_le)
        elif magic == 0xCFFAEDFE:
            self._header = read_struct(self._stream, mach_header_be)
            self._layout = Layout(load_command_be, dylib_be)

    def get_deps(self):
        self._stream.seek(sizeof(self._header))
        for _ in range(self._header.ncmds):
            lc = read_struct(self._stream, self._layout.load_command)
            if not lc:
                return
            if lc.cmd == 0xC:
                dylib = read_struct(self._stream, self._layout.dylib)
                if not dylib:
                    return
                size = lc.cmdsize - sizeof(lc) - sizeof(dylib)
                name = self._stream.read(size)
                if len(name) < size:
                    return
                end_index = name.find(b"\x00")
                if end_index >= 0:
                    name = name[:end_index]
                yield name.decode("latin-1")
            else:
                self._stream.seek(lc.cmdsize - sizeof(lc), 1)
