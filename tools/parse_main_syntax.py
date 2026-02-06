import ast
from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'main.py'
src = p.read_text(encoding='utf-8')
try:
    ast.parse(src)
    print('AST parsed OK')
except SyntaxError as e:
    print('SyntaxError:', e.msg, 'at', e.lineno, e.offset)
    lines = src.splitlines()
    for i in range(max(1,e.lineno-5), e.lineno+5):
        print(i, lines[i-1].rstrip('\n'))
