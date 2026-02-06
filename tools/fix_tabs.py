from pathlib import Path
p = Path(__file__).parent.parent / 'main.py'
s = p.read_text(encoding='utf-8')
if '\t' in s:
    s2 = s.replace('\t', '    ')
    p.write_text(s2, encoding='utf-8')
    print('Rewrote', p)
else:
    print('No tabs found')
