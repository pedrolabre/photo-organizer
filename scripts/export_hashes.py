"""Exportador de hashes e distâncias para inspeção manual.

Gera CSV e JSON em output/reports/ contendo para cada imagem:
- caminho, md5, phash (hex), closest_distance, closest_path

Execute: venv/Scripts/python.exe scripts/export_hashes.py
"""
import sys
from pathlib import Path as _Path
_root = _Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))
import sqlite3
from pathlib import Path
import csv
import json
from datetime import datetime
from src.detection.similar_detector import SimilarDuplicateDetector
from src.utils.config import get_config
from src.utils.logger import init_logger, get_logger


def main():
    init_logger(level="INFO")
    log = get_logger()

    cfg = get_config()
    db_path = cfg.get_database_path()

    if not db_path.exists():
        log.error(f"Banco não encontrado: {db_path}")
        return

    conn = sqlite3.connect(str(db_path))
    cur = conn.execute("SELECT file_path, md5_hash FROM images")
    rows = cur.fetchall()
    paths = []
    for r in rows:
        p = Path(r[0])
        if p.exists():
            paths.append((p, r[1]))
        else:
            log.warning(f"Arquivo listado no DB não existe: {p}")

    detector = SimilarDuplicateDetector()

    # compute phashes
    entries = []
    for p, md5 in paths:
        try:
            ph = detector.compute_hash(p)
            entries.append({"path": str(p), "md5": md5, "phash": str(ph)})
        except Exception as e:
            log.warning(f"Falha ao gerar phash para {p}: {e}")

    # compute pairwise distances (small N expected)
    for i, e in enumerate(entries):
        min_dist = None
        min_path = None
        hi = detector.compute_hash(Path(e["path"]))
        for j, f in enumerate(entries):
            if i == j:
                continue
            hj = detector.compute_hash(Path(f["path"]))
            try:
                dist = hi - hj
            except Exception:
                continue
            if min_dist is None or dist < min_dist:
                min_dist = dist
                min_path = f["path"]
        e["closest_distance"] = int(min_dist) if min_dist is not None else -1
        e["closest_path"] = min_path

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_csv = Path("output/reports") / f"hashes_{ts}.csv"
    out_json = Path("output/reports") / f"hashes_{ts}.json"

    # write csv
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "md5", "phash", "closest_distance", "closest_path"])
        writer.writeheader()
        for e in entries:
            writer.writerow(e)

    # write json
    with out_json.open("w", encoding="utf-8") as f:
        json.dump({"generated": ts, "entries": entries}, f, ensure_ascii=False, indent=2)

    log.info(f"Exportados {len(entries)} hashes: {out_csv}, {out_json}")


if __name__ == "__main__":
    main()
