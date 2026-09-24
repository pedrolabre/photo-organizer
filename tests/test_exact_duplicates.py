import shutil
import sqlite3
from pathlib import Path
from unittest.mock import patch
from src.detection.exact_duplicates import ExactDuplicateDetector
from PIL import Image


def make_image(path: Path, color=(255, 0, 0), size=(100, 100)):
    img = Image.new("RGB", size, color)
    img.save(path)


def test_group_by_md5(tmp_path):
    d = tmp_path / "images"
    d.mkdir()

    p1 = d / "a.jpg"
    p2 = d / "b.jpg"
    p3 = d / "c.jpg"

    make_image(p1)
    shutil.copy2(p1, p2)
    make_image(p3, color=(0, 255, 0))

    detector = ExactDuplicateDetector()
    groups = detector.group_by_md5([p1, p2, p3])

    found = False
    for md5, files in groups.items():
        if len(files) == 2:
            assert str(p1) in files and str(p2) in files
            found = True
    assert found, "Did not find group of exact duplicates"


def test_group_by_size_and_filter_candidates(tmp_path):
    d = tmp_path / "sizes"
    d.mkdir()

    p1 = d / "file1.bin"
    p2 = d / "file2.bin"
    p3 = d / "file3.bin"

    p1.write_bytes(b"hello world")
    p2.write_bytes(b"other world")
    p3.write_bytes(b"different length text!")

    detector = ExactDuplicateDetector()
    size_map = detector.group_by_size([p1, p2, p3])

    assert len(size_map[11]) == 2
    assert len(size_map[len(b"different length text!")]) == 1

    candidates = detector.filter_candidates_by_size([p1, p2, p3])
    assert p1 in candidates
    assert p2 in candidates
    assert p3 not in candidates


def test_fast_discard_avoids_hashing_unique_sizes(tmp_path):
    d = tmp_path / "discard"
    d.mkdir()

    p1 = d / "unique1.bin"
    p2 = d / "unique2.bin"

    p1.write_bytes(b"1")
    p2.write_bytes(b"12")

    detector = ExactDuplicateDetector()

    with patch.object(
        ExactDuplicateDetector, "compute_md5", wraps=ExactDuplicateDetector.compute_md5
    ) as mock_md5:
        groups = detector.group_by_md5([p1, p2])
        assert groups == {}
        assert mock_md5.call_count == 0


def test_find_in_db(tmp_path):
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE images (id INTEGER PRIMARY KEY, file_path TEXT, md5_hash TEXT)"
    )
    conn.execute(
        "INSERT INTO images (file_path, md5_hash) VALUES ('/path/to/test.jpg', 'fake_md5')"
    )
    conn.commit()

    detector = ExactDuplicateDetector(db_conn=conn)
    assert detector.find_in_db("fake_md5") == "/path/to/test.jpg"
    assert detector.find_in_db("non_existent") is None
    conn.close()
