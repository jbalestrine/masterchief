import importlib, sys
from pathlib import Path
# ensure repo root is on sys.path when running from scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

m = importlib.import_module('main')
print('ROUTES:')
for r in sorted([rule.rule for rule in m.app.url_map.iter_rules()]):
    print(r)
