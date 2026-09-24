from pathlib import Path
from typing import List, Dict, Optional
import hashlib
import sqlite3
from src.utils.logger import get_logger


class ExactDuplicateDetector:
    def __init__(self, db_conn: Optional[sqlite3.Connection] = None) -> None:
        self.logger = get_logger()
        self.conn: Optional[sqlite3.Connection] = db_conn

    @staticmethod
    def compute_md5(path: Path, chunk_size: int = 65536) -> str:
        h = hashlib.md5()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                h.update(chunk)
        return h.hexdigest()

    def find_in_db(self, md5: str) -> Optional[str]:
        if not self.conn:
            return None
        try:
            cur = self.conn.execute(
                "SELECT file_path FROM images WHERE md5_hash = ?", (md5,)
            )
            row = cur.fetchone()
            return row[0] if row else None
        except Exception as e:
            self.logger.debug(f"Erro consultando DB por md5: {e}")
            return None

    def group_by_size(self, paths: List[Path]) -> Dict[int, List[Path]]:
        size_map: Dict[int, List[Path]] = {}
        for p in paths:
            try:
                if not p.is_file():
                    continue
                size = p.stat().st_size
                size_map.setdefault(size, []).append(p)
            except OSError as e:
                self.logger.warning(f"Erro obtendo tamanho de {p}: {e}")
        return size_map

    def filter_candidates_by_size(self, paths: List[Path]) -> List[Path]:
        size_map = self.group_by_size(paths)
        candidates: List[Path] = []
        for candidate_list in size_map.values():
            if len(candidate_list) >= 2:
                candidates.extend(candidate_list)
        return candidates

    def group_by_md5(self, paths: List[Path]) -> Dict[str, List[str]]:
        size_map = self.group_by_size(paths)
        groups: Dict[str, List[str]] = {}

        for candidate_list in size_map.values():
            if len(candidate_list) < 2:
                continue

            for p in candidate_list:
                try:
                    md5 = self.compute_md5(p)
                    groups.setdefault(md5, []).append(str(p))
                except Exception as e:
                    self.logger.warning(f"Erro ao calcular MD5 de {p}: {e}")

        return groups
