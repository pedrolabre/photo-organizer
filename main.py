"""Main CLI MVP for Photo Organizer.

Runs: scan -> metadata -> md5 hash -> store in SQLite -> detect exact duplicates -> move duplicates to quarantine -> write JSON report
"""
from pathlib import Path
import sys
import sqlite3
import json
import shutil
from datetime import datetime
import hashlib
import argparse

from src.utils.logger import init_logger, get_logger
from src.utils.config import get_config
from src.core.file_scanner import FileScanner
from src.core.metadata_reader import MetadataReader
from src.detection.exact_duplicates import ExactDuplicateDetector
from src.detection.similar_detector import SimilarDuplicateDetector
from src.detection.keep_policy import choose_keeper, choose_keeper_among
from src.database.db_manager import DBManager


DB_PATH = Path("data/database/photo_organizer.db")
QUARANTINE_DIR = Path("output/quarantine/groups")
REPORTS_DIR = Path("output/reports")


def compute_md5(path: Path, chunk_size: int = 8192) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_dirs():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def init_db(conn: sqlite3.Connection):
    conn.execute(
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
    conn.commit()


def store_image(conn: sqlite3.Connection, meta: dict, md5: str):
    conn.execute(
        """
        INSERT OR IGNORE INTO images (
            file_path, file_name, file_size, format, width, height, megapixels,
            datetime, camera_make, camera_model, md5_hash
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    conn.commit()


def find_existing_by_md5(conn: sqlite3.Connection, md5: str):
    cur = conn.execute("SELECT file_path FROM images WHERE md5_hash = ?", (md5,))
    row = cur.fetchone()
    return row[0] if row else None


def move_to_quarantine(path: Path, md5: str, dry_run: bool = False) -> Path:
    dest_dir = QUARANTINE_DIR / md5
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / path.name
    if dry_run:
        # simulate move: just return destination path and log
        return dest
    shutil.move(str(path), str(dest))
    return dest


def main():
    parser = argparse.ArgumentParser(prog="photo-organizer", description="MVP photo organizer pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without moving files")
    parser.add_argument("--threshold", type=int, default=None, help="Override visual similarity threshold")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    logger = init_logger(level="INFO")
    log = get_logger()

    cfg = get_config(args.config)
    # override threshold if provided
    if args.threshold is not None:
        cfg.duplicates.similarity_threshold = args.threshold

    scanner = FileScanner(cfg)
    reader = MetadataReader()

    ensure_dirs()
    conn = sqlite3.connect(str(DB_PATH))
    init_db(conn)

    dbm = DBManager(str(DB_PATH))
    detector = ExactDuplicateDetector(conn)

    log.info("Iniciando pipeline MVP: scan -> metadata -> hash -> store -> duplicates")

    files = scanner.scan_all_sources()
    log.info(f"Arquivos encontrados: {len(files)}")

    duplicates = []

    for p in files:
        try:
            meta = reader.read_metadata(p)
            md5 = detector.compute_md5(p)

            existing = detector.find_in_db(md5)
            if existing and Path(existing) != p:
                # duplicate found: decide keep policy
                existing_row = dbm.get_by_md5(md5)
                decision = choose_keeper(existing_row or {}, meta, cfg.duplicates.keep_policy)
                if decision == "existing":
                    # keep DB entry, move current to quarantine
                    new_path = move_to_quarantine(p, md5, dry_run=args.dry_run)
                    log.info(f"Duplicata detectada. Mantendo existente. Movendo {p} → {new_path}")
                    duplicates.append({"original": existing, "duplicate": str(new_path), "md5": md5})
                    continue
                else:
                    # keep new: move existing file to quarantine and update DB entry
                    try:
                        existing_path = Path(existing_row.get("file_path")) if existing_row else Path(existing)
                        if existing_path.exists():
                            moved = move_to_quarantine(existing_path, md5, dry_run=args.dry_run)
                            log.info(f"Duplicata detectada. Mantendo novo. Movendo existente {existing_path} → {moved}")
                            duplicates.append({"original": str(p), "duplicate": str(moved), "md5": md5})
                    except Exception as e:
                        log.warning(f"Falha movendo existente: {e}")

                    # update DB row to point to new file
                    dbm.update_image_by_md5(md5, meta)
                    continue

            # store and continue
            store_image(conn, meta, md5)

        except Exception as e:
            log.warning(f"Erro processando {p}: {e}")

    # write duplicates report
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS_DIR / f"duplicates_{ts}.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump({"generated": ts, "duplicates": duplicates}, f, ensure_ascii=False, indent=2)

    # --- Detectar duplicatas visuais (similares) entre imagens armazenadas ---
    try:
        if cfg.duplicates.detect_similar:
            threshold = cfg.duplicates.similarity_threshold or 5
            detector_sim = SimilarDuplicateDetector()
            cur = conn.execute("SELECT file_path FROM images")
            stored = [Path(r[0]) for r in cur.fetchall()]
            log.info(f"Verificando duplicatas visuais entre {len(stored)} imagens armazenadas com limiar={threshold}...")
            groups = detector_sim.group_similar(stored, max_distance=threshold)
            sim_count = 0
            for rep, group in groups.items():
                # choose keeper according to policy
                keeper = choose_keeper_among([Path(p) for p in group], cfg.duplicates.keep_policy)
                for dup_path in group:
                    pdup = Path(dup_path)
                    if pdup == keeper:
                        continue
                    if not pdup.exists():
                        continue
                    new_path = move_to_quarantine(pdup, compute_md5(pdup), dry_run=args.dry_run)
                    log.info(f"Similar detectado. Mantendo {keeper}. Movendo {pdup} → {new_path}")
                    duplicates.append({"original": str(keeper), "duplicate": str(new_path), "reason": "visual"})
                    sim_count += 1

            log.info(f"Detecção visual concluída. Duplicatas visuais movidas: {sim_count}")
        else:
            log.info("Detecção visual desativada nas configurações; pulando etapa.")
    except Exception as e:
        log.warning(f"Erro na detecção de similares: {e}")

    log.info(f"Pipeline concluído. Duplicatas: {len(duplicates)}. Relatório: {report_path}")


if __name__ == "__main__":
    main()
