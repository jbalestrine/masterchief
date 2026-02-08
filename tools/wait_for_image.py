#!/usr/bin/env python3
import time
from pathlib import Path
from pathlib import Path
import sys
base = Path(__file__).resolve().parent.parent
outdir = base / 'data' / 'echo_images'
outdir.mkdir(parents=True, exist_ok=True)
start_files = set(outdir.glob('*.png'))
start_max = max((f.stat().st_mtime for f in start_files), default=0)
print(f'Watcher started; initial files={len(start_files)}, start_max={start_max}')
# Wait up to 90 minutes
timeout = 60 * 90
deadline = time.time() + timeout
interval = 5
while time.time() < deadline:
    files = list(outdir.glob('*.png'))
    if files:
        cur_max = max((f.stat().st_mtime for f in files))
    else:
        cur_max = 0
    if cur_max > start_max:
        new_files = [f for f in files if f.stat().st_mtime > start_max]
        new = max(new_files, key=lambda x: x.stat().st_mtime)
        rel = new.relative_to(base).as_posix()
        print('FOUND', rel)
        sys.stdout.flush()
        # exit with success
        sys.exit(0)
    time.sleep(interval)
print('TIMEOUT waiting for image', file=sys.stderr)
sys.exit(2)
