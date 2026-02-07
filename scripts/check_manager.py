import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import importlib
m = importlib.import_module('main')
print('HAS manager_dashboard:', hasattr(m, 'manager_dashboard'))
print('HAS api_manager_tasks:', hasattr(m, 'api_manager_tasks'))
print('APP rules count:', len(list(m.app.url_map.iter_rules())))
for r in sorted([rule.rule for rule in m.app.url_map.iter_rules()]):
    if 'manager' in r:
        print('FOUND manager route:', r)
