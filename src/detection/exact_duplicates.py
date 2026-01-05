from pathlib import Path
from typing import List, Dict, Optional
import hashlib
import sqlite3

from src.utils.logger import get_logger


class ExactDuplicateDetector:
    """Detector de duplicatas exatas baseado em MD5.

    Pode calcular MD5s e consultar um banco SQLite (tabela `images`) para
    localizar arquivos já registrados com o mesmo hash.
    """

    def __init__(self, db_conn: Optional[sqlite3.Connection] = None):
        self.logger = get_logger()
        self.conn = db_conn

    @staticmethod
    def compute_md5(path: Path, chunk_size: int = 8192) -> str:
        h = hashlib.md5()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                h.update(chunk)
        return h.hexdigest()

    def find_in_db(self, md5: str) -> Optional[str]:
        """Retorna o `file_path` existente na DB com esse md5, ou None."""
        if not self.conn:
            return None
        try:
            cur = self.conn.execute("SELECT file_path FROM images WHERE md5_hash = ?", (md5,))
            row = cur.fetchone()
            return row[0] if row else None
        except Exception as e:
            self.logger.debug(f"Erro consultando DB por md5: {e}")
            return None

    def group_by_md5(self, paths: List[Path]) -> Dict[str, List[str]]:
        """Agrupa uma lista de caminhos por MD5 (útil para checar duplicatas em lote)."""
        groups: Dict[str, List[str]] = {}
        for p in paths:
            try:
                md5 = self.compute_md5(p)
                groups.setdefault(md5, []).append(str(p))
            except Exception as e:
                self.logger.warning(f"Erro ao calcular MD5 de {p}: {e}")
        return groups
