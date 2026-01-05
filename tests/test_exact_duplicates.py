import shutil
from pathlib import Path
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
    # create identical copy
    shutil.copy2(p1, p2)
    # different image
    make_image(p3, color=(0, 255, 0))

    detector = ExactDuplicateDetector()
    groups = detector.group_by_md5([p1, p2, p3])

    # expect one group with two identical files
    found = False
    for md5, files in groups.items():
        if len(files) == 2:
            assert str(p1) in files and str(p2) in files
            found = True
    assert found, "Did not find group of exact duplicates"
