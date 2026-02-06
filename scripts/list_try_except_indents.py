from pathlib import Path
import re
text = Path('main.py').read_text(encoding='utf-8')
lines = text.splitlines()
for i,l in enumerate(lines, start=1):
    m = re.match(r"^([ \t]*)(try:)\s*$", l)
    if m:
        ind = m.group(1).count('\t')
        print(f"{i}: try (tabs={ind}) -> {repr(l)}")
    m2 = re.match(r"^([ \t]*)(except\b.*)$", l)
    if m2:
        ind = m2.group(1).count('\t')
        print(f"{i}: except (tabs={ind}) -> {repr(l)}")
