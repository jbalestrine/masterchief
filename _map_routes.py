"""Map route functions with line numbers."""
import re

lines = open('main.py', encoding='utf-8').readlines()
route_funcs = []
for i, l in enumerate(lines):
    if l.startswith('def '):
        fname = l.strip().split('(')[0].replace('def ','')
        routes = []
        j = i - 1
        while j >= 0 and (lines[j].strip().startswith('@') or lines[j].strip() == ''):
            if '@app.route' in lines[j]:
                m = re.search(r"@app\.route\(['\"]([^'\"]+)", lines[j])
                if m:
                    routes.append(m.group(1))
            j -= 1
        if routes:
            route_funcs.append((i+1, fname, routes))

print('Line   Function                          Route')
print('-' * 90)
for ln, fn, rts in route_funcs:
    r = rts[0] if rts else ""
    print(f"{ln:5d}  {fn:35s}  {r}")
