#!/usr/bin/env python3
"""Update imports from `platform` to `mc_platform` across the repo (no renaming).
Usage: python tools/update_imports_only.py
"""
import os, sys, re
from pathlib import Path
root = Path(__file__).resolve().parents[1]
py_files = []
for p in root.rglob('*.py'):
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
    text = re.sub(r'(^\s*from\s+)platform(\b)', r"\1mc_platform\2", text, flags=re.M)
    text = re.sub(r'(^\s*import\s+)platform(\b)', r"\1mc_platform\2", text, flags=re.M)
    text = re.sub(r'(?<!\w)platform\.', 'mc_platform.', text)
    if text != orig:
        p.write_text(text, encoding='utf-8')
        changed.append(str(p.relative_to(root)))
print('Updated', len(changed), 'files')
for c in changed[:200]:
    print(' -', c)
print('Done')
