"""Package report outputs into a timestamped ZIP file.

Run: venv\Scripts\python.exe scripts/package_reports.py
"""
from pathlib import Path
from datetime import datetime
import zipfile

def main():
    rpt_dir = Path("output/reports")
    if not rpt_dir.exists():
        print("No reports found in output/reports")
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_zip = rpt_dir / f"package_{ts}.zip"
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in rpt_dir.rglob("*"):
            if p.is_file():
                # store relative to reports dir
                z.write(p, arcname=str(p.relative_to(rpt_dir)))
    print(f"Packaged reports: {out_zip}")

if __name__ == "__main__":
    main()
