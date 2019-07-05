import hashlib
import os
from pathlib import Path

from exg.utils import mirror

PATHS = (
    Path("1") / "a",
    Path("2") / "b",
    Path("3") / os.fsdecode(b"c\xc3\x97"),
)


def map_dir(function, root):
    return {
        path.relative_to(root): function(path)
        for path in root.rglob("*")
        if path.is_file() and path.name != ".ino-index.json"
    }


def file_inode(path):
    return path.stat().st_ino


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_mirror(tmp_path):
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    src_address = mirror.Address(None, f"{src_dir}/")
    dst_address = mirror.Address(None, str(dst_dir))
    rsync = mirror.Rsync(
        args=[],
        src=src_address,
        dest=dst_address,
    )

    for i, path in enumerate(PATHS):
        (src_dir / path).parent.mkdir(parents=True, exist_ok=True)
        (src_dir / path).write_text(str(i))

    rsync.mirror(dry_run=False)
    assert map_dir(hash_file, src_dir) == map_dir(hash_file, dst_dir)

    tmp_path = src_dir / "tmp"
    (src_dir / PATHS[0]).rename(tmp_path)
    (src_dir / PATHS[1]).rename(src_dir / PATHS[0])
    tmp_path.rename(src_dir / PATHS[1])
    (src_dir / PATHS[2]).rename(src_dir / PATHS[2].with_suffix(".txt"))

    inodes_pre = map_dir(file_inode, dst_dir)
    rsync.mirror(dry_run=False)
    inodes_post = map_dir(file_inode, dst_dir)
    assert map_dir(hash_file, src_dir) == map_dir(hash_file, dst_dir)
    assert inodes_pre[PATHS[0]] == inodes_post[PATHS[1]]
    assert inodes_pre[PATHS[1]] == inodes_post[PATHS[0]]
    assert inodes_pre[PATHS[2]] == inodes_post[PATHS[2].with_suffix(".txt")]
