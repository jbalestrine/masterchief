import re
code = open('main.py', 'r', encoding='utf-8').read()
refs = re.findall(r'["\']([A-Za-z_/]+\.html)["\']', code)
unique = sorted(set(refs))
print(len(unique), 'unique HTML refs')
for r in unique:
    print(r)
