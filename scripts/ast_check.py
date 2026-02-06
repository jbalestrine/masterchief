import ast
from pathlib import Path
text = Path('main.py').read_text(encoding='utf-8')
try:
    ast.parse(text, filename='main.py')
    print('Parsed OK')
except SyntaxError as e:
    print('SyntaxError:', e.msg)
    print('  File:', e.filename)
    print('  Line:', e.lineno)
    print('  Offset:', e.offset)
    # show context
    lines = text.splitlines()
    for i in range(max(0, e.lineno-4), min(len(lines), e.lineno+2)):
        prefix = '>' if i+1==e.lineno else ' '
        print(f"{prefix} {i+1}: {lines[i]!r}")
