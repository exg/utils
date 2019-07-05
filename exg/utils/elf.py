from __future__ import annotations

from ctypes import (
    BigEndianStructure,
    LittleEndianStructure,
    Structure,
    c_int32,
    c_int64,
    c_uint8,
    c_uint16,
    c_uint32,
    c_uint64,
    sizeof,
)
from dataclasses import dataclass


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


_ehdr32_fields = (
    ("e_ident", e_ident),
    ("e_type", c_uint16),
    ("e_machine", c_uint16),
    ("e_version", c_uint32),
    ("e_entry", c_uint32),
    ("e_phoff", c_uint32),
    ("e_shoff", c_uint32),
    ("e_flags", c_uint32),
    ("e_ehsize", c_uint16),
    ("e_phentsize", c_uint16),
    ("e_phnum", c_uint16),
    ("e_shentsize", c_uint16),
    ("e_shnum", c_uint16),
    ("e_shstrndx", c_uint16),
)


class ehdr32_le(LittleEndianStructure):
    _pack_ = 1
    _fields_ = _ehdr32_fields


class ehdr32_be(BigEndianStructure):
    _pack_ = 1
    _fields_ = _ehdr32_fields


_ehdr64_fields = (
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


class ehdr64_le(LittleEndianStructure):
    _pack_ = 1
    _fields_ = _ehdr64_fields


class ehdr64_be(BigEndianStructure):
    _pack_ = 1
    _fields_ = _ehdr64_fields


_phdr32_fields = (
    ("p_type", c_uint32),
    ("p_offset", c_uint32),
    ("p_vaddr", c_uint32),
    ("p_paddr", c_uint32),
    ("p_filesz", c_uint32),
    ("p_memsz", c_uint32),
    ("p_flags", c_uint32),
    ("p_align", c_uint32),
)


class phdr32_le(LittleEndianStructure):
    _pack_ = 1
    _fields_ = _phdr32_fields


class phdr32_be(BigEndianStructure):
    _pack_ = 1
    _fields_ = _phdr32_fields


_phdr64_fields = (
    ("p_type", c_uint32),
    ("p_flags", c_uint32),
    ("p_offset", c_uint64),
    ("p_vaddr", c_uint64),
    ("p_paddr", c_uint64),
    ("p_filesz", c_uint64),
    ("p_memsz", c_uint64),
    ("p_align", c_uint64),
)


class phdr64_le(LittleEndianStructure):
    _pack_ = 1
    _fields_ = _phdr64_fields


class phdr64_be(BigEndianStructure):
    _pack_ = 1
    _fields_ = _phdr64_fields


class dyn32_le(LittleEndianStructure):
    _pack_ = 1
    _fields_ = (("d_tag", c_int32), ("d_val", c_uint32))


class dyn32_be(BigEndianStructure):
    _pack_ = 1
    _fields_ = (("d_tag", c_int32), ("d_val", c_uint32))


class dyn64_le(LittleEndianStructure):
    _pack_ = 1
    _fields_ = (("d_tag", c_int64), ("d_val", c_uint64))


class dyn64_be(BigEndianStructure):
    _pack_ = 1
    _fields_ = (("d_tag", c_int64), ("d_val", c_uint64))


def read_struct(stream, stype):
    data = stream.read(sizeof(stype))
    if len(data) < sizeof(stype):
        return None
    return stype.from_buffer_copy(data)


class _StringTable:
    def __init__(self, stream, offset):
        self._stream = stream
        self._offset = offset

    def get_string(self, offset):
        self._stream.seek(self._offset + offset)
        CHUNKSIZE = 64
        string = b""
        while True:
            chunk = self._stream.read(CHUNKSIZE)
            end_index = chunk.find(b"\x00")
            if end_index >= 0:
                string += chunk[:end_index]
                return string.decode("latin-1")
            if len(chunk) < CHUNKSIZE:
                return None
            string += chunk


@dataclass
class Layout:
    ehdr: LittleEndianStructure | BigEndianStructure
    phdr: LittleEndianStructure | BigEndianStructure
    dyn: LittleEndianStructure | BigEndianStructure


class ELFInfo:
    def __init__(self, stream):
        self._stream = stream
        self._header = None
        self._read_header()
        if not self._header:
            raise ValueError

    def _read_header(self):
        self._stream.seek(0)
        data = self._stream.peek(sizeof(e_ident))
        if len(data) < sizeof(e_ident):
            return
        ident = e_ident.from_buffer_copy(data)
        if ident.EI_MAG[0:4] != [0x7F, 0x45, 0x4C, 0x46]:
            return
        if ident.EI_CLASS == 2:
            if ident.EI_DATA == 1:
                self._header = read_struct(self._stream, ehdr64_le)
                self._layout = Layout(ehdr64_le, phdr64_le, dyn64_le)
            else:
                self._header = read_struct(self._stream, ehdr64_be)
                self._layout = Layout(ehdr64_be, phdr64_be, dyn64_be)
        elif ident.EI_CLASS == 1:
            if ident.EI_DATA == 1:
                self._header = read_struct(self._stream, ehdr32_le)
                self._layout = Layout(ehdr32_le, phdr32_le, dyn32_le)
            else:
                self._header = read_struct(self._stream, ehdr32_be)
                self._layout = Layout(ehdr32_be, phdr32_be, dyn32_be)

    def _get_dyn_offset(self):
        if not self._header.e_phoff:
            return None
        self._stream.seek(self._header.e_phoff)
        for _ in range(self._header.e_phnum):
            pheader = read_struct(self._stream, self._layout.phdr)
            if not pheader:
                return None
            if pheader.p_type == 2:
                return pheader.p_offset
        return None

    def get_deps(self):
        offset = self._get_dyn_offset()
        if not offset:
            return
        self._stream.seek(offset)
        offsets = []
        strtab_offset = None
        while True:
            dyn = read_struct(self._stream, self._layout.dyn)
            if not dyn:
                return
            if dyn.d_tag == 0:
                break
            if dyn.d_tag == 1:
                offsets.append(dyn.d_val)
            elif dyn.d_tag == 5:
                strtab_offset = dyn.d_val
        if not strtab_offset:
            return
        string_table = _StringTable(self._stream, strtab_offset)
        yield from (string_table.get_string(offset) for offset in offsets)
