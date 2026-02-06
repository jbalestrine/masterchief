from importlib import import_module
import main
app = main.app
routes = sorted([str(r) for r in app.url_map.iter_rules()])
for r in routes:
    print(r)
