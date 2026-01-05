"""Generate metadata reports from the SQLite DB.

Outputs:
- output/reports/metadata_<ts>.csv  (one row per image)
- output/reports/summary_<ts>.json  (counts, duplicates summary)

Run: venv/Scripts/python.exe scripts/generate_reports.py
"""
import sys
from pathlib import Path
import csv
import json
from datetime import datetime

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))

from src.utils.config import get_config
from src.utils.logger import init_logger, get_logger
import sqlite3
from PIL import Image
from pathlib import Path
import os
from collections import defaultdict


def main():
    init_logger(level="INFO")
    log = get_logger()

    cfg = get_config()
    db_path = cfg.get_database_path()
    if not db_path.exists():
        log.error(f"DB not found: {db_path}")
        return

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.execute("SELECT * FROM images ORDER BY id")
    rows = [dict(r) for r in cur.fetchall()]

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_csv = Path("output/reports") / f"metadata_{ts}.csv"
    out_json = Path("output/reports") / f"summary_{ts}.json"

    fieldnames = [
        "id", "file_path", "file_name", "file_size", "format",
        "width", "height", "megapixels", "datetime", "camera_make", "camera_model", "md5_hash",
        "thumbnail_path", "folder"
    ]

    thumb_dir = Path("output/reports/thumbnails")
    thumb_dir.mkdir(parents=True, exist_ok=True)

    # Precompute md5 counts to mark duplicates per folder
    md5_counts = {}
    for r in rows:
        md5 = r.get("md5_hash") or ""
        md5_counts[md5] = md5_counts.get(md5, 0) + 1

    # Per-folder accumulators
    folders = defaultdict(lambda: {"count": 0, "total_size": 0, "total_width": 0, "total_height": 0, "duplicates": 0})

    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            file_path = r.get("file_path") or ""
            folder = ""
            thumb_path = ""
            try:
                p = Path(file_path)
                folder = str(p.parent)
                folders[folder]["count"] += 1
                size = int(r.get("file_size") or 0)
                folders[folder]["total_size"] += size
                w = int(r.get("width") or 0)
                h = int(r.get("height") or 0)
                folders[folder]["total_width"] += w
                folders[folder]["total_height"] += h
                md5 = r.get("md5_hash") or ""
                if md5 and md5_counts.get(md5, 0) > 1:
                    folders[folder]["duplicates"] += 1

                # Create thumbnail
                if p.exists():
                    try:
                        with Image.open(p) as im:
                            im = im.convert("RGB")
                            im.thumbnail((300, 300), Image.LANCZOS)
                            safe_name = f"{r.get('id')}_{p.name}".replace(os.path.sep, "_")
                            out_thumb = thumb_dir / safe_name
                            out_thumb = out_thumb.with_suffix('.jpg')
                            im.save(out_thumb, format="JPEG", quality=85)
                            thumb_path = str(out_thumb)
                    except Exception:
                        thumb_path = ""
                else:
                    thumb_path = ""
            except Exception:
                folder = ""

            row_out = {k: r.get(k, "") for k in fieldnames}
            row_out["thumbnail_path"] = thumb_path
            row_out["folder"] = folder
            writer.writerow(row_out)

    summary = {
        "generated": ts,
        "total_images": len(rows),
        "by_format": {},
    }
    for r in rows:
        fmt = r.get("format") or "UNKNOWN"
        summary["by_format"][fmt] = summary["by_format"].get(fmt, 0) + 1

    # Folder metrics
    folder_metrics = {}
    for fld, acc in folders.items():
        cnt = acc["count"]
        avg_w = int(acc["total_width"] / cnt) if cnt else 0
        avg_h = int(acc["total_height"] / cnt) if cnt else 0
        folder_metrics[fld] = {
            "count": cnt,
            "total_size_bytes": int(acc["total_size"]),
            "avg_width": avg_w,
            "avg_height": avg_h,
            "duplicates": int(acc["duplicates"]),
        }

    summary["by_folder"] = folder_metrics

    # Thumbnails listing (small index for dashboard)
    thumbnails_info = []
    for r in rows:
        tp = None
        try:
            p = Path(r.get("file_path") or "")
            thumb_candidate = thumb_dir / f"{r.get('id')}_{p.name}"
            thumb_candidate = thumb_candidate.with_suffix('.jpg')
            if thumb_candidate.exists():
                tp = str(thumb_candidate)
        except Exception:
            tp = None

        thumbnails_info.append({
            "id": int(r.get("id") or 0),
            "file_name": r.get("file_name") or "",
            "thumbnail_path": tp or "",
            "folder": str(Path(r.get("file_path") or "").parent) if r.get("file_path") else "",
            "md5_hash": r.get("md5_hash") or "",
        })

    summary["thumbnails"] = thumbnails_info

    with out_json.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # Also write a per-folder CSV for quick inspection
    out_folder_csv = Path("output/reports") / f"folder_metrics_{ts}.csv"
    with out_folder_csv.open("w", encoding="utf-8", newline="") as f:
        fieldnames_f = ["folder", "count", "total_size_bytes", "avg_width", "avg_height", "duplicates"]
        writer = csv.DictWriter(f, fieldnames=fieldnames_f)
        writer.writeheader()
        for fld, m in folder_metrics.items():
            row = {"folder": fld}
            row.update(m)
            writer.writerow(row)

    log.info(f"Reports generated: {out_csv}, {out_json}, {out_folder_csv}")


if __name__ == "__main__":
    main()
