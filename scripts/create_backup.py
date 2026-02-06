#!/usr/bin/env python3
import sys
import zipfile
from pathlib import Path
import time

root = Path(__file__).resolve().parents[1]
backups = root / 'backups'
backups.mkdir(parents=True, exist_ok=True)

# Collect files excluding backups folder
files = [p for p in root.rglob('*') if p.is_file() and backups not in p.parents]
if not files:
    ts = time.strftime('%Y%m%d-%H%M%S')
else:
    latest = max(files, key=lambda p: p.stat().st_mtime)
    ts = time.strftime('%Y%m%d-%H%M%S', time.localtime(latest.stat().st_mtime))

zip_name = backups / f'backup-lastchange-{ts}.zip'
print('Creating zip:', zip_name)
try:
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            try:
                zf.write(f, f.relative_to(root))
            except Exception as e:
                print('Skipped', f, '->', e)
    if zip_name.exists():
        print('Created:', zip_name)
        sys.exit(0)
    else:
        print('Failed to create:', zip_name)
        sys.exit(2)
except Exception as e:
    print('ERROR:', e)
    sys.exit(3)
