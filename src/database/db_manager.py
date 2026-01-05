"""DB manager utilities for Photo Organizer.

Provides a small wrapper around SQLite for initializing tables,
basic queries with pagination, lookup by MD5 and simple backup.
"""
from pathlib import Path
import sqlite3
import shutil
from typing import List, Dict, Optional, Tuple
from src.utils.logger import get_logger
from src.utils.config import get_config


class DBManager:
    def __init__(self, db_path: Optional[str] = None):
        self.logger = get_logger()
        cfg = get_config()
        self.db_path = Path(db_path) if db_path else cfg.get_database_path()
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

    def init_tables(self) -> None:
        """Ensure required tables exist."""
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE,
                file_name TEXT,
                file_size INTEGER,
                format TEXT,
                width INTEGER,
                height INTEGER,
                megapixels REAL,
                datetime TEXT,
                camera_make TEXT,
                camera_model TEXT,
                md5_hash TEXT
            )
            """
        )
        self.conn.commit()

    def count_images(self) -> int:
        cur = self.conn.execute("SELECT COUNT(*) as cnt FROM images")
        row = cur.fetchone()
        return int(row["cnt"]) if row else 0

    def get_images(self, page: int = 1, page_size: int = 50) -> List[Dict]:
        """Return paginated list of images (dict rows)."""
        offset = (page - 1) * page_size
        cur = self.conn.execute(
            "SELECT * FROM images ORDER BY id LIMIT ? OFFSET ?", (page_size, offset)
        )
        return [dict(r) for r in cur.fetchall()]

    def get_by_md5(self, md5: str) -> Optional[Dict]:
        cur = self.conn.execute("SELECT * FROM images WHERE md5_hash = ? LIMIT 1", (md5,))
        row = cur.fetchone()
        return dict(row) if row else None

    def update_image_by_md5(self, md5: str, meta: Dict) -> None:
        """Update image row identified by md5 with new metadata."""
        self.conn.execute(
            """
            UPDATE images SET
                file_path = ?, file_name = ?, file_size = ?, format = ?, width = ?, height = ?, megapixels = ?, datetime = ?, camera_make = ?, camera_model = ?
            WHERE md5_hash = ?
            """,
            (
                meta.get("file_path"),
                meta.get("file_name"),
                meta.get("file_size"),
                meta.get("format"),
                meta.get("width"),
                meta.get("height"),
                meta.get("megapixels"),
                meta.get("datetime").isoformat() if meta.get("datetime") else None,
                meta.get("camera_make"),
                meta.get("camera_model"),
                md5,
            ),
        )
        self.conn.commit()

    def backup(self, dest: Optional[str] = None) -> Path:
        """Create a backup copy of the DB file. Returns backup path."""
        dest_dir = Path(dest) if dest else self.db_path.parent / "backups"
        dest_dir.mkdir(parents=True, exist_ok=True)
        ts = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = dest_dir / f"{self.db_path.stem}_backup_{ts}{self.db_path.suffix}"
        self.conn.close()
        shutil.copy2(self.db_path, backup_path)
        # re-open connection
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.logger.info(f"DB backup criado: {backup_path}")
        return backup_path

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass
