from pathlib import Path
import sqlite3
import datetime
from typing import List, Dict, Optional, Any
from src.utils.logger import get_logger
from src.utils.config import get_config


class DBManager:
    def __init__(self, db_path: Optional[str] = None) -> None:
        self.logger = get_logger()
        cfg = get_config()
        self.db_path: Path = Path(db_path) if db_path else cfg.get_database_path()
        if str(self.db_path) != ":memory:":
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: sqlite3.Connection = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._apply_pragmas()

    def _apply_pragmas(self) -> None:
        if str(self.db_path) != ":memory:":
            self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.execute("PRAGMA synchronous = NORMAL")
        self.conn.execute("PRAGMA cache_size = -65536")
        self.conn.execute("PRAGMA temp_store = MEMORY")
        self.conn.execute("PRAGMA foreign_keys = ON")

    def get_pragma(self, name: str) -> str:
        cur = self.conn.execute(f"PRAGMA {name}")
        row = cur.fetchone()
        return str(row[0]) if row else ""

    def init_tables(self) -> None:
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
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_images_md5 ON images (md5_hash)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_images_file_size ON images (file_size)"
        )
        self.conn.commit()

    def count_images(self) -> int:
        cur = self.conn.execute("SELECT COUNT(*) as cnt FROM images")
        row = cur.fetchone()
        return int(row["cnt"]) if row else 0

    def get_images(self, page: int = 1, page_size: int = 50) -> List[Dict[str, Any]]:
        offset = (page - 1) * page_size
        cur = self.conn.execute(
            "SELECT * FROM images ORDER BY id LIMIT ? OFFSET ?", (page_size, offset)
        )
        return [dict(r) for r in cur.fetchall()]

    def get_by_md5(self, md5: str) -> Optional[Dict[str, Any]]:
        cur = self.conn.execute(
            "SELECT * FROM images WHERE md5_hash = ? LIMIT 1", (md5,)
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def insert_images_batch(self, images: List[Dict[str, Any]]) -> int:
        if not images:
            return 0
        records = []
        for img in images:
            dt = img.get("datetime")
            dt_str = (
                dt.isoformat()
                if hasattr(dt, "isoformat")
                else (str(dt) if dt is not None else None)
            )
            records.append(
                (
                    (
                        str(img.get("file_path"))
                        if img.get("file_path") is not None
                        else None
                    ),
                    img.get("file_name"),
                    img.get("file_size"),
                    img.get("format"),
                    img.get("width"),
                    img.get("height"),
                    img.get("megapixels"),
                    dt_str,
                    img.get("camera_make"),
                    img.get("camera_model"),
                    img.get("md5_hash"),
                )
            )
        query = """
            INSERT OR REPLACE INTO images (
                file_path, file_name, file_size, format, width, height, megapixels, datetime, camera_make, camera_model, md5_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self.conn:
            self.conn.executemany(query, records)
        return len(records)

    def insert_image(self, meta: Dict[str, Any], md5: str) -> None:
        payload = dict(meta)
        payload["md5_hash"] = md5
        self.insert_images_batch([payload])

    def update_images_batch(self, updates: List[Dict[str, Any]]) -> int:
        if not updates:
            return 0
        records = []
        for meta in updates:
            dt = meta.get("datetime")
            dt_str = (
                dt.isoformat()
                if hasattr(dt, "isoformat")
                else (str(dt) if dt is not None else None)
            )
            records.append(
                (
                    (
                        str(meta.get("file_path"))
                        if meta.get("file_path") is not None
                        else None
                    ),
                    meta.get("file_name"),
                    meta.get("file_size"),
                    meta.get("format"),
                    meta.get("width"),
                    meta.get("height"),
                    meta.get("megapixels"),
                    dt_str,
                    meta.get("camera_make"),
                    meta.get("camera_model"),
                    meta.get("md5_hash"),
                )
            )
        query = """
            UPDATE images SET
                file_path = ?, file_name = ?, file_size = ?, format = ?, width = ?, height = ?, megapixels = ?, datetime = ?, camera_make = ?, camera_model = ?
            WHERE md5_hash = ?
        """
        with self.conn:
            self.conn.executemany(query, records)
        return len(records)

    def update_image_by_md5(self, md5: str, meta: Dict[str, Any]) -> None:
        payload = dict(meta)
        payload["md5_hash"] = md5
        self.update_images_batch([payload])

    def backup(self, dest: Optional[str] = None) -> Path:
        dest_dir = Path(dest) if dest else self.db_path.parent / "backups"
        dest_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = (
            dest_dir / f"{self.db_path.stem}_backup_{ts}{self.db_path.suffix}"
        )
        backup_conn = sqlite3.connect(str(backup_path))
        try:
            self.conn.backup(backup_conn)
        finally:
            backup_conn.close()
        self.logger.info(f"DB backup criado: {backup_path}")
        return backup_path

    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass
