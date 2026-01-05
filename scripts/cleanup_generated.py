import os
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
removed = []

# Remove contents of output/reports
reports_dir = BASE / 'output' / 'reports'
if reports_dir.exists():
    for p in reports_dir.rglob('*'):
        try:
            if p.is_file():
                p.unlink()
                removed.append(str(p))
            elif p.is_dir():
                shutil.rmtree(p)
                removed.append(str(p))
        except Exception as e:
            print(f"Failed to remove {p}: {e}")

# Remove logs in data/logs
logs_dir = BASE / 'data' / 'logs'
if logs_dir.exists():
    for p in logs_dir.glob('*.log'):
        try:
            p.unlink()
            removed.append(str(p))
        except Exception as e:
            print(f"Failed to remove {p}: {e}")

# Remove __pycache__ directories recursively
for p in BASE.rglob('__pycache__'):
    try:
        shutil.rmtree(p)
        removed.append(str(p))
    except Exception as e:
        print(f"Failed to remove {p}: {e}")

# Print summary
print('Removed files/folders:')
for r in removed:
    print(r)
print(f'Total removed: {len(removed)}')
