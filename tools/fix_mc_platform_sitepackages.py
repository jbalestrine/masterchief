"""Scan venv site-packages for occurrences of 'mc_platform' imports and replace
with the stdlib 'platform' imports. Creates backups of modified files.
"""
import os
from pathlib import Path
root = Path(__file__).resolve().parent.parent / 'venv' / 'Lib' / 'site-packages'
if not root.exists():
    print('site-packages not found:', root)
    raise SystemExit(1)

changed = []
for p in root.rglob('*.py'):
    try:
        text = p.read_text(encoding='utf-8')
    except Exception:
        continue
    new = text
    if 'import mc_platform' in new:
        new = new.replace('import mc_platform', 'import platform')
    if 'from mc_platform import' in new:
        new = new.replace('from mc_platform import', 'from platform import')
    if new != text:
        bak = p.with_suffix(p.suffix + '.bak')
        bak.write_text(text, encoding='utf-8')
        p.write_text(new, encoding='utf-8')
        changed.append(str(p))

print('Modified', len(changed), 'files')
for c in changed[:50]:
    print(' ', c)
