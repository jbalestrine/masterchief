#!/usr/bin/env python3
"""Rename repo 'platform' package to 'mc_platform' and update imports.
Usage: python tools/rename_platform_pkg.py
This script will:
- Create a zip backup of the current `platform` directory under `data/backups`.
- Rename the `platform` directory to `mc_platform`.
- Update Python source files to replace `import platform` / `from platform` with `mc_platform`.
- Print a summary of changed files.
"""
import os, sys, shutil, time, re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
platform_dir = root / 'platform'
new_dir = root / 'mc_platform'
backups = root / 'data' / 'backups'
backups.mkdir(parents=True, exist_ok=True)

if not platform_dir.exists():
    print('No platform directory found at', platform_dir)
    sys.exit(1)

stamp = time.strftime('%Y%m%d_%H%M%S')
zip_name = backups / f'platform_backup_{stamp}'
print('Creating backup archive:', zip_name.with_suffix('.zip'))
shutil.make_archive(str(zip_name), 'zip', root_dir=str(platform_dir))

# Rename directory
if new_dir.exists():
    print('Target mc_platform already exists:', new_dir)
    print('Aborting to avoid overwrite. Remove that folder first if you want to proceed.')
    sys.exit(1)

print('Renaming', platform_dir, '->', new_dir)
try:
    os.rename(platform_dir, new_dir)
except Exception as e:
    print('Failed to rename:', e)
    sys.exit(1)

# Patterns to replace in .py files
py_files = []
for p in root.rglob('*.py'):
    # skip venv and backups and .git
    if 'venv' in p.parts or 'data' in p.parts or '.git' in p.parts:
        continue
    py_files.append(p)

changed = []
for p in py_files:
    try:
        text = p.read_text(encoding='utf-8')
    except Exception:
        continue
    orig = text
    # Replace `from platform` and `import platform` only at statement level
    text = re.sub(r'(^\s*from\s+)platform(\b)', r"\1mc_platform\2", text, flags=re.M)
    text = re.sub(r'(^\s*import\s+)platform(\b)', r"\1mc_platform\2", text, flags=re.M)
    # Replace usages like `mc_platform.` with `mc_platform.` but avoid replacing strings
    # We'll do a cautious replacement: only in code (naive) - skip inside triple quotes by removing them temporarily
    triple_q = re.findall(r'([\'\"]{3})([\s\S]*?)\1', text)
    # remove triple-quoted blocks
    mask = []
    def _mask_triple(m):
        mask.append(m.group(0))
        return '{{TRIPLE_QUOTE_BLOCK_{} }}'.format(len(mask)-1)
    text_masked = re.sub(r'([\'\"]{3})([\s\S]*?)\1', _mask_triple, text)
    text_masked = re.sub(r'(?<!\w)platform\.', 'mc_platform.', text_masked)
    # restore triple blocks
    for i,blk in enumerate(mask):
        text_masked = text_masked.replace('{{TRIPLE_QUOTE_BLOCK_{} }}'.format(i), blk)
    text = text_masked

    if text != orig:
        p.write_text(text, encoding='utf-8')
        changed.append(str(p.relative_to(root)))

print('Updated', len(changed), 'files')
for c in changed[:200]:
    print(' -', c)
print('\nDone. Please run your tests and start the venv python server:')
print(' & .\\venv\\Scripts\\python.exe main.py --debug --port 8080')
