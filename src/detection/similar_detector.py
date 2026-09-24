from pathlib import Path
from typing import List, Dict, Tuple, Optional
from PIL import Image
import imagehash
from src.utils.logger import get_logger
from src.detection.bk_tree import BKTree


class SimilarDuplicateDetector:
    def __init__(self, hash_size: int = 16) -> None:
        self.logger = get_logger()
        self.hash_size: int = hash_size

    def compute_hash(self, path: Path) -> imagehash.ImageHash:
        try:
            with Image.open(path) as im:
                return imagehash.phash(im, hash_size=self.hash_size)
        except Exception as e:
            self.logger.debug(f"Erro ao calcular hash de {path}: {e}")
            raise

    def build_tree(
        self, items: List[Tuple[imagehash.ImageHash, str]]
    ) -> BKTree[Tuple[imagehash.ImageHash, str]]:
        def _distance(
            a: Tuple[imagehash.ImageHash, str], b: Tuple[imagehash.ImageHash, str]
        ) -> int:
            return int(a[0] - b[0])

        tree = BKTree[Tuple[imagehash.ImageHash, str]](distance_fn=_distance)
        tree.build(items)
        return tree

    def find_similar(
        self,
        query_hash: imagehash.ImageHash,
        tree: BKTree[Tuple[imagehash.ImageHash, str]],
        max_distance: int = 5,
    ) -> List[Tuple[str, int]]:
        matches = tree.search((query_hash, ""), max_distance=max_distance)
        return [(item[1], dist) for item, dist in matches]

    def group_similar(
        self, paths: List[Path], max_distance: int = 5
    ) -> Dict[str, List[str]]:
        items: List[Tuple[imagehash.ImageHash, str]] = []
        for p in paths:
            try:
                h = self.compute_hash(p)
                items.append((h, str(p)))
            except Exception:
                continue

        if len(items) < 2:
            return {}

        tree = self.build_tree(items)
        visited = set()
        groups: Dict[str, List[str]] = {}

        for h_i, p_i in items:
            if p_i in visited:
                continue
            group: List[str] = [p_i]
            visited.add(p_i)

            matches = tree.search((h_i, p_i), max_distance=max_distance)
            for (matched_h, matched_p), _ in matches:
                if matched_p not in visited:
                    group.append(matched_p)
                    visited.add(matched_p)

            if len(group) > 1:
                groups[p_i] = group

        return groups
