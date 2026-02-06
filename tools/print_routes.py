import runpy
_g = runpy.run_path('main.py')
app = _g.get('app')
if not app:
    print('No Flask `app` found in main.py')
else:
    for r in sorted(app.url_map.iter_rules(), key=lambda x: x.rule):
        methods = ','.join(sorted([m for m in r.methods if m not in ('HEAD','OPTIONS')]))
        print(f"{r.rule} -> {methods}")
