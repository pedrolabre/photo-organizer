from pathlib import Path
from typing import List, Dict
from PIL import Image
import imagehash
from src.utils.logger import get_logger


class SimilarDuplicateDetector:
    """Detecta duplicatas visuais usando hashes perceptuais (phash).

    Método simples: calcula `imagehash.phash` para cada imagem e agrupa
    imagens cuja distância de Hamming seja menor ou igual a um limite.
    """

    def __init__(self, hash_size: int = 16):
        self.logger = get_logger()
        self.hash_size = hash_size

    def compute_hash(self, path: Path) -> imagehash.ImageHash:
        try:
            with Image.open(path) as im:
                return imagehash.phash(im, hash_size=self.hash_size)
        except Exception as e:
            self.logger.debug(f"Erro ao calcular hash de {path}: {e}")
            raise

    def group_similar(self, paths: List[Path], max_distance: int = 5) -> Dict[str, List[str]]:
        """Agrupa imagens similares. Retorna dict: representative_hash -> [paths]."""
        hashes = {}
        for p in paths:
            try:
                h = self.compute_hash(p)
                hashes[str(p)] = h
            except Exception:
                continue

        visited = set()
        groups = {}

        items = list(hashes.items())
        for i, (p_i, h_i) in enumerate(items):
            if p_i in visited:
                continue
            group = [p_i]
            visited.add(p_i)
            for j in range(i + 1, len(items)):
                p_j, h_j = items[j]
                if p_j in visited:
                    continue
                try:
                    dist = h_i - h_j
                except Exception:
                    continue
                if dist <= max_distance:
                    group.append(p_j)
                    visited.add(p_j)

            if len(group) > 1:
                groups[p_i] = group

        return groups
