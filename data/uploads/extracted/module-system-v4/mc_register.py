"""
MasterChief Module Registry Integration
========================================
ONE-TIME addition to main.py — paste the section below into your app setup.

This does three things:
  1. Reads addons/registry.json (written by Module Command Center)
  2. Injects module nav sections into MasterChief's sidebar automatically
  3. Exposes /api/registry and /api/nav-sections endpoints

Every future module just needs a manifest.json — zero main.py changes after this.

─────────────────────────────────────────────────────────────────────────────
PASTE INTO main.py (after app = Flask(__name__) and before your routes):
─────────────────────────────────────────────────────────────────────────────
"""

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  PASTE THIS BLOCK INTO main.py                                          ║
# ╚══════════════════════════════════════════════════════════════════════════╝

MAIN_PY_INTEGRATION = '''
# ── Module Registry Integration ─────────────────────────────────────────────
# Auto-discovers addons and injects their nav sections.
# Written by Module Command Center — do not remove.
import json as _json
from pathlib import Path as _Path

_REGISTRY_PATH = _Path(__file__).parent / 'addons' / 'registry.json'
_MODULE_REGISTRY = {}

def _load_module_registry():
    global _MODULE_REGISTRY
    try:
        if _REGISTRY_PATH.exists():
            _MODULE_REGISTRY = _json.loads(_REGISTRY_PATH.read_text(encoding='utf-8'))
    except Exception as _e:
        print(f"[registry] Failed to load: {_e}")

_load_module_registry()


@app.route('/api/registry')
def api_module_registry():
    """Public registry of all installed modules — used by Module Command Center."""
    _load_module_registry()  # refresh on each call
    return jsonify(_MODULE_REGISTRY)


@app.route('/api/nav-sections')
def api_nav_sections():
    """
    Nav sections for the MasterChief sidebar, auto-populated from registry.
    Returns grouped + sorted module list for UI injection.
    """
    _load_module_registry()
    modules   = _MODULE_REGISTRY.get('modules', {})
    sections  = {}
    CATS = {
        'admin_ops':    {'label': 'Admin Ops',       'icon': '⚙',  'order': 1},
        'addons':       {'label': 'Add Ons',          'icon': '🔌', 'order': 2},
        'sys_modules':  {'label': 'Systems Modules',  'icon': '🧩', 'order': 3},
        'integrations': {'label': 'Integrations',     'icon': '🔗', 'order': 4},
        'devtools':     {'label': 'Dev Tools',        'icon': '🛠', 'order': 5},
        'data':         {'label': 'Data & Analytics', 'icon': '📊', 'order': 6},
        'security':     {'label': 'Security',         'icon': '🔐', 'order': 7},
        'cloud':        {'label': 'Cloud & Infra',    'icon': '☁',  'order': 8},
        'uncategorized':{'label': 'Other',            'icon': '📦', 'order': 99},
    }
    for slug, m in modules.items():
        if not m.get('has_app'):
            continue
        cat = m.get('category', 'uncategorized')
        cat_info = CATS.get(cat, CATS['uncategorized'])
        if cat not in sections:
            sections[cat] = {
                'id': cat, 'label': cat_info['label'],
                'icon': cat_info['icon'], 'order': cat_info['order'],
                'items': []
            }
        sections[cat]['items'].append({
            'slug':  slug,
            'label': m.get('label', slug),
            'icon':  m.get('icon', '📦'),
            'color': m.get('color', '#f5a623'),
            'url':   f'/addons/modules/{slug}/app',
        })
    result = sorted(sections.values(), key=lambda s: s['order'])
    for s in result:
        s['items'].sort(key=lambda i: i['label'])
    return jsonify({'sections': result, 'total_modules': len(modules)})


@app.route('/api/capabilities')
def api_capabilities():
    """All capabilities declared by installed modules."""
    _load_module_registry()
    cap_map = {}
    for slug, m in _MODULE_REGISTRY.get('modules', {}).items():
        for cap in m.get('capabilities', []):
            cap_map.setdefault(cap, []).append(slug)
    return jsonify(cap_map)
# ── End Module Registry Integration ─────────────────────────────────────────
'''

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  SIDEBAR JS SNIPPET — paste into your nav template                      ║
# ╚══════════════════════════════════════════════════════════════════════════╝

SIDEBAR_JS = '''
// Auto-inject module nav sections from registry
(async function injectModuleNav() {
  try {
    const r = await fetch('/api/nav-sections');
    const d = await r.json();
    const sidebar = document.getElementById('sidebar-modules');
    if (!sidebar || !d.sections) return;

    sidebar.innerHTML = d.sections.map(section => `
      <div class="nav-section">
        <div class="nav-section-label">${section.icon} ${section.label}</div>
        ${section.items.map(item => `
          <a class="nav-item" href="${item.url}" style="border-left-color:${item.color}">
            ${item.icon} ${item.label}
          </a>`).join('')}
      </div>`).join('');
  } catch(e) {
    console.warn('[registry] Nav inject failed:', e.message);
  }
})();
'''

if __name__ == '__main__':
    print("Module Registry Integration")
    print("=" * 50)
    print()
    print("1. Paste MAIN_PY_INTEGRATION into main.py (after app = Flask(__name__))")
    print("2. Paste SIDEBAR_JS into your nav template HTML")
    print("3. Add <div id='sidebar-modules'></div> in your sidebar where you want module links")
    print()
    print("That's it. No other changes needed.")
    print("Module Command Center writes registry.json automatically when you install/update modules.")
