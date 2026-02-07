from pathlib import Path
p=Path('main.py').read_text(encoding='utf-8')
count=p.count("\"\"\"")
print('triple quote count',count)
# show around first 2000 chars for inspection
for i,idx in enumerate([i for i in range(len(p)) if p.startswith('"""',i)][:50]):
    print(i, 'pos', idx)
# find any lone triple quotes and show context
pos=0
while True:
    i=p.find('"""',pos)
    if i==-1: break
    print('found at',i)
    print(p[i-40:i+60])
    pos=i+3
