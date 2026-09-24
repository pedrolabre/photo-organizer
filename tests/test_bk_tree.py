import pytest
from typing import Tuple
from src.detection.bk_tree import BKTree


def hamming_distance_str(s1: str, s2: str) -> int:
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


def abs_diff(a: int, b: int) -> int:
    return abs(a - b)


def test_bk_tree_empty():
    tree = BKTree[str](distance_fn=hamming_distance_str)
    assert tree.is_empty() is True
    assert len(tree) == 0
    assert tree.size == 0
    assert tree.search("1010", max_distance=1) == []


def test_bk_tree_insert_single():
    tree = BKTree[str](distance_fn=hamming_distance_str)
    tree.insert("1010")
    assert tree.is_empty() is False
    assert len(tree) == 1
    assert tree.size == 1

    results = tree.search("1010", max_distance=0)
    assert len(results) == 1
    assert results[0] == ("1010", 0)


def test_bk_tree_exact_match_duplicate_items():
    tree = BKTree[Tuple[str, str]](distance_fn=lambda a, b: hamming_distance_str(a[0], b[0]))
    tree.insert(("1010", "path1.jpg"))
    tree.insert(("1010", "path2.jpg"))
    tree.insert(("1110", "path3.jpg"))

    assert len(tree) == 3

    exact_matches = tree.search(("1010", "query"), max_distance=0)
    assert len(exact_matches) == 2
    paths = [item[0][1] for item in exact_matches]
    assert "path1.jpg" in paths
    assert "path2.jpg" in paths

    radius_matches = tree.search(("1010", "query"), max_distance=1)
    assert len(radius_matches) == 3


def test_bk_tree_radius_search_pruning():
    tree = BKTree[int](distance_fn=abs_diff)
    numbers = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    tree.build(numbers)

    assert len(tree) == len(numbers)

    matches = tree.search(22, max_distance=5)
    matched_values = [val for val, dist in matches]
    assert matched_values == [20]
    assert matches[0] == (20, 2)

    matches_wider = tree.search(35, max_distance=10)
    matched_wider_values = sorted([val for val, dist in matches_wider])
    assert matched_wider_values == [30, 40]


def test_bk_tree_ordering():
    tree = BKTree[int](distance_fn=abs_diff)
    tree.build([50, 45, 52, 60, 40, 51])

    results = tree.search(50, max_distance=10)
    distances = [dist for _, dist in results]
    assert distances == sorted(distances)
    assert results[0] == (50, 0)


def test_bk_tree_clear():
    tree = BKTree[int](distance_fn=abs_diff)
    tree.build([1, 2, 3])
    assert len(tree) == 3
    tree.clear()
    assert tree.is_empty() is True
    assert len(tree) == 0
