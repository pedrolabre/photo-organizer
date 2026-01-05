from pathlib import Path
from src.detection.similar_detector import SimilarDuplicateDetector
from PIL import Image, ImageDraw


def make_image(path: Path, draw_dot: bool = False, size=(200, 200)):
    img = Image.new("RGB", size, (128, 128, 128))
    if draw_dot:
        d = ImageDraw.Draw(img)
        d.ellipse((90, 90, 110, 110), fill=(255, 0, 0))
    img.save(path)


def test_group_similar(tmp_path):
    d = tmp_path / "sim"
    d.mkdir()
    p1 = d / "base.jpg"
    p2 = d / "dot.jpg"
    p3 = d / "different.jpg"

    # create checkerboard base for p1
    size = 200
    cell = 20
    img1 = Image.new("RGB", (size, size), (240, 240, 240))
    draw1 = ImageDraw.Draw(img1)
    for y in range(0, size, cell):
        for x in range(0, size, cell):
            c = (200, 200, 200) if ((x // cell) + (y // cell)) % 2 == 0 else (60, 60, 60)
            draw1.rectangle([x, y, x + cell - 1, y + cell - 1], fill=c)
    img1.save(p1)

    # p2: small local modification from p1 (should remain visually similar)
    img2 = img1.copy()
    draw2 = ImageDraw.Draw(img2)
    draw2.rectangle([90, 90, 110, 110], fill=(255, 0, 0))
    img2.save(p2)

    # p3: significantly different stripes
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

    # p1 should be more similar to p2 (small dot) than to p3 (different color)
    assert d12 < d13, f"Expected p1 closer to p2 (d12={d12}) than to p3 (d13={d13})"
