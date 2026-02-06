import re
from pathlib import Path

text = Path('main.py').read_text(encoding='utf-8')
lines = text.splitlines()
stack = []
for i, line in enumerate(lines, start=1):
    m = re.match(r"^([ \t]*)try:\s*$", line)
    if m:
        indent = len(m.group(1))
        stack.append((i, indent))
    m2 = re.match(r"^([ \t]*)except\b", line)
    if m2:
        indent = len(m2.group(1))
        # find matching try at same indent
        for j in range(len(stack)-1, -1, -1):
            if stack[j][1] == indent:
                stack.pop(j)
                break

if stack:
    print('Unmatched try blocks:')
    for lineno, indent in stack:
        print(f'  try at line {lineno} (indent={indent}) has no matching except/finally')
else:
    print('All try blocks have matching except at same indentation (heuristic)')
