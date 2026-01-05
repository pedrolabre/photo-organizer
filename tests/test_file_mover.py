import pytest
from pathlib import Path
from src.organization.file_mover import FileMover

class DummySafety:
    file_operation = "copy"
    verify_after_copy = True
class DummyConfig:
    safety = DummySafety()

def create_file(path: Path, content: bytes):
    path.write_bytes(content)
    return path

def test_copy_and_conflict(tmp_path):
    config = DummyConfig()
    mover = FileMover(config)
    src = create_file(tmp_path / "a.txt", b"abc123")
    dest_folder = tmp_path / "dest"
    # Test copy
    ok, msg, dest = mover.process_file(src, dest_folder)
    assert ok and dest.exists() and dest.read_bytes() == b"abc123"
    # Test conflict: copy again, should create a new file
    src2 = create_file(tmp_path / "a.txt", b"abc123")
    ok2, msg2, dest2 = mover.process_file(src2, dest_folder)
    assert ok2 and dest2.exists() and dest2 != dest
    # Test verify_after_copy (should be True)
    assert mover._verify_copy(dest, dest2)
    # Test stats
    stats = mover.get_stats()
    assert stats["copied"] >= 2
    assert stats["errors"] == 0
