from pathlib import Path
from src.detection.similar_detector import SimilarDuplicateDetector
from PIL import Image, ImageDraw


def test_group_similar(tmp_path):
    d = tmp_path / "sim"
    d.mkdir()
    p1 = d / "base.jpg"
    p2 = d / "dot.jpg"
    p3 = d / "different.jpg"

    size = 200
    cell = 20
    img1 = Image.new("RGB", (size, size), (240, 240, 240))
    draw1 = ImageDraw.Draw(img1)
    for y in range(0, size, cell):
        for x in range(0, size, cell):
            c = (200, 200, 200) if ((x // cell) + (y // cell)) % 2 == 0 else (60, 60, 60)
            draw1.rectangle([x, y, x + cell - 1, y + cell - 1], fill=c)
    img1.save(p1)

    img2 = img1.copy()
    draw2 = ImageDraw.Draw(img2)
    draw2.rectangle([90, 90, 110, 110], fill=(255, 0, 0))
    img2.save(p2)

    img3 = Image.new("RGB", (size, size), (0, 0, 255))
    draw3 = ImageDraw.Draw(img3)
    for i in range(0, size, 10):
        color = (255, 255, 0) if (i // 10) % 2 == 0 else (0, 255, 0)
        draw3.rectangle([i, 0, i + 9, size - 1], fill=color)
    img3.save(p3)

    detector = SimilarDuplicateDetector(hash_size=8)
    h1 = detector.compute_hash(p1)
    h2 = detector.compute_hash(p2)
    h3 = detector.compute_hash(p3)

    d12 = h1 - h2
    d13 = h1 - h3

    assert d12 < d13, f"Expected p1 closer to p2 (d12={d12}) than to p3 (d13={d13})"


def test_group_similar_clusters_duplicates(tmp_path):
    d = tmp_path / "clusters"
    d.mkdir()

    p1 = d / "img1.png"
    p2 = d / "img2.png"
    p3 = d / "img3.png"

    img1 = Image.new("RGB", (200, 200))
    for x in range(200):
        for y in range(200):
            img1.putpixel((x, y), ((x * 7) % 256, (y * 11) % 256, ((x + y) * 13) % 256))
    img1.save(p1)

    img2 = img1.resize((190, 190))
    img2.save(p2)

    img3 = Image.new("RGB", (200, 200))
    for x in range(200):
        for y in range(200):
            img3.putpixel((x, y), ((x * 23) % 256, (y * 31) % 256, ((x * y) % 256)))
    img3.save(p3)

    detector = SimilarDuplicateDetector(hash_size=8)
    groups = detector.group_similar([p1, p2, p3], max_distance=5)

    assert len(groups) == 1
    rep = list(groups.keys())[0]
    members = groups[rep]
    assert str(p1) in members
    assert str(p2) in members
    assert str(p3) not in members


def test_build_tree_and_find_similar(tmp_path):
    d = tmp_path / "find_sim"
    d.mkdir()

    p1 = d / "a.png"
    p2 = d / "b.png"

    img1 = Image.new("RGB", (200, 200))
    for x in range(200):
        for y in range(200):
            img1.putpixel((x, y), ((x * 5) % 256, (y * 9) % 256, ((x + y) * 7) % 256))
    img1.save(p1)

    img2 = img1.resize((192, 192))
    img2.save(p2)

    detector = SimilarDuplicateDetector(hash_size=8)
    h1 = detector.compute_hash(p1)
    h2 = detector.compute_hash(p2)

    dist = h1 - h2
    tree = detector.build_tree([(h1, str(p1)), (h2, str(p2))])
    matches = detector.find_similar(h1, tree, max_distance=dist)

    paths = [match_path for match_path, _ in matches]
    assert str(p1) in paths
    assert str(p2) in paths


def test_group_similar_empty_and_single(tmp_path):
    detector = SimilarDuplicateDetector(hash_size=8)
    assert detector.group_similar([]) == {}

    p = tmp_path / "single.png"
    Image.new("RGB", (10, 10), (0, 0, 0)).save(p)
    assert detector.group_similar([p]) == {}
