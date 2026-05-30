"""Analyze main.py structure."""
import re

code = open('main.py', encoding='utf-8').read()
lines = code.splitlines()

# Count basics
imports = [i for i,l in enumerate(lines) if l.strip().startswith(('import ','from '))]
routes = re.findall(r'@app\.route\(', code)
funcdefs = re.findall(r'^def \w+', code, re.MULTILINE)
classdefs = re.findall(r'^class \w+', code, re.MULTILINE)

print(f"Total lines: {len(lines)}")
print(f"Import lines: {len(imports)}")
print(f"Route decorators (@app.route): {len(routes)}")
print(f"Function defs: {len(funcdefs)}")
print(f"Class defs: {len(classdefs)}")

# Find big inline string blocks
print("\n=== LARGE INLINE STRINGS (>20 lines) ===")
in_str = False
start = 0
varname = ""
for i, l in enumerate(lines):
    if not in_str:
        m = re.match(r'^(\w[\w_]*)\s*=\s*(?:r)?("{3})', l)
        if not m:
            m = re.match(r"^(\w[\w_]*)\s*=\s*(?:r)?('{3})", l)
        if m:
            varname = m.group(1)
            delim = m.group(2)
            count_delim = l.count(delim)
            if count_delim == 1:
                in_str = True
                start = i
            # if 2, it opens and closes on same line - skip
    else:
        if '"""' in l or "'''" in l:
            size = i - start + 1
            if size > 20:
                print(f"  L{start+1:5d}-L{i+1:5d}  ({size:5d} lines)  {varname}")
            in_str = False

# Route groups by first path segment
print("\n=== ROUTE GROUPS ===")
from collections import Counter
prefixes = Counter()
route_lines = []
for i, l in enumerate(lines):
    m = re.search(r"@app\.route\(['\"]([^'\"]+)", l)
    if m:
        path = m.group(1)
        route_lines.append((i+1, path))
        parts = path.strip('/').split('/')
        prefix = '/' + parts[0] if parts[0] else '/'
        prefixes[prefix] += 1

for p, c in prefixes.most_common(40):
    print(f"  {p:30s}  {c:3d} routes")

# Blueprint registrations
print("\n=== BLUEPRINT REGISTRATIONS ===")
for i, l in enumerate(lines):
    if 'register_blueprint' in l:
        print(f"  L{i+1:5d}  {l.strip()}")

# Key line ranges
print("\n=== KEY SECTIONS (by line range) ===")
sections = []
for i, l in enumerate(lines):
    if l.startswith('# ===') or l.startswith('# ---') or l.startswith('# ###'):
        sections.append((i+1, l.strip()))
    elif re.match(r'^#{1,3}\s+[A-Z]', l):
        sections.append((i+1, l.strip()))

for ln, txt in sections[:60]:
    print(f"  L{ln:5d}  {txt[:80]}")

print("\n=== SUMMARY ===")
print(f"File has {len(lines)} lines with {len(routes)} routes and {len(funcdefs)} functions in ONE file.")
print(f"Large inline strings account for significant bloat.")
print("This file needs to be split into logical modules.")
