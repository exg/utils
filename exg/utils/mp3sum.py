#!/usr/bin/env python3

import argparse
import hashlib
import os
from ctypes import Structure, c_uint8


class id3v2_header(Structure):
    _pack_ = 1
    _fields_ = (
        ("id", c_uint8 * 3),
        ("version", c_uint8 * 2),
        ("flags", c_uint8),
        ("size", c_uint8 * 4),
    )


def hash_mp3(path: str) -> str:
    with open(path, "rb") as f:
        data_size = os.fstat(f.fileno()).st_size

        tag_size = 0
        data = f.read(10)
        if len(data) == 10 and data[:3] == b"ID3":
            header = id3v2_header.from_buffer_copy(data)
            for byte in header.size:
                tag_size = (tag_size << 7) + byte
            tag_size += 10
            if header.flags & (1 << 4):
                tag_size += 10
            data_size -= tag_size

        f.seek(-128, 2)
        if f.read(3) == b"TAG":
            data_size -= 128

        f.seek(tag_size)
        h = hashlib.sha256()
        h.update(f.read(data_size))
        return h.hexdigest()


def main() -> None:
    """
    Compute the SHA256 hash of a MP3 file excluding ID3 tags, if any.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("file")
    args = parser.parse_args()

    print(hash_mp3(args.file))


if __name__ == "__main__":
    main()
