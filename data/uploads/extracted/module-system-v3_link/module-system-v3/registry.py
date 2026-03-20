"""
Module Registry
Central discovery and registration engine for MasterChief addons.

Every addon folder can contain a manifest.json declaring:
  slug, label, category, nav_section, icon, color, version,
  capabilities[], requires[], entry_point, description

The registry:
  - Scans addons/modules/ on demand
  - Reads each manifest.json (falls back to plugin.py PLUGIN_META)
  - Writes addons/registry.json (consumed by main.py for nav injection)
  - Tracks capability providers so modules can find each other
  - Detects broken dependencies
"""
import json
import ast
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

CATEGORIES = {
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

# Known module assignments (for auto-generated modules that lack manifests)
KNOWN_CATEGORIES = {
    'module-system':      'admin_ops',
    'module-system-v2':   'admin_ops',
    'module-system-v3':   'admin_ops',
    'diagnostics-alchemy':'admin_ops',
    'cloud-command':      'cloud',
    'orphan-sweeper':     'sys_modules',
    'blueprint-extractor':'sys_modules',
    'log-streamer':       'addons',
    'health-monitor':     'addons',
    'env-auditor':        'devtools',
    'db-connector':       'data',
    'desktop-shell':      'admin_ops',
}


class Registry:
    def __init__(self, addons_dir: Path, registry_path: Path):
        self.addons_dir    = addons_dir
        self.registry_path = registry_path
        self._data: Dict   = {}

    # ── Public API ────────────────────────────────────────────────

    def discover(self) -> Dict:
        """Scan addons/modules/, build registry, write registry.json."""
        modules  = {}
        errors   = []

        if not self.addons_dir.exists():
            return {'modules': {}, 'errors': [f'addons dir not found: {self.addons_dir}']}

        for d in sorted(self.addons_dir.iterdir()):
            if not d.is_dir() or d.name.startswith('.') or d.name.startswith('_'):
                continue
            try:
                entry = self._read_module(d)
                modules[d.name] = entry
            except Exception as e:
                errors.append(f'{d.name}: {e}')

        # Resolve dependency status
        all_caps = set()
        for m in modules.values():
            all_caps.update(m.get('capabilities', []))

        for m in modules.values():
            broken = [r for r in m.get('requires', []) if r not in all_caps]
            m['deps_ok']    = len(broken) == 0
            m['broken_deps'] = broken

        self._data = {
            'modules':      modules,
            'categories':   CATEGORIES,
            'errors':       errors,
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'count':        len(modules),
        }

        # Pre-build nav sections and embed in registry.json
        # so main.py can serve /api/nav-sections without importing this module
        self._data['_nav_sections'] = self.nav_sections()

        # Write registry.json for main.py to consume
        self.registry_path.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        return self._data

    def get(self) -> Dict:
        """Return cached registry, re-discover if stale."""
        if not self._data and self.registry_path.exists():
            try:
                self._data = json.loads(self.registry_path.read_text(encoding='utf-8'))
            except Exception:
                return self.discover()
        return self._data or self.discover()

    def capabilities(self) -> Dict:
        """Return map of capability → list of modules that provide it."""
        data = self.get()
        cap_map: Dict[str, List[str]] = {}
        for slug, m in data.get('modules', {}).items():
            for cap in m.get('capabilities', []):
                cap_map.setdefault(cap, []).append(slug)
        return cap_map

    def nav_sections(self) -> List[Dict]:
        """
        Build nav structure for MasterChief to inject into its sidebar.
        Returns list of sections, each with items sorted by order.
        """
        data = self.get()
        sections: Dict[str, Dict] = {}

        for slug, m in data.get('modules', {}).items():
            if not m.get('has_app'):
                continue
            cat = m.get('category', 'uncategorized')
            cat_info = CATEGORIES.get(cat, CATEGORIES['uncategorized'])

            if cat not in sections:
                sections[cat] = {
                    'id':    cat,
                    'label': cat_info['label'],
                    'icon':  cat_info['icon'],
                    'order': cat_info['order'],
                    'items': [],
                }
            sections[cat]['items'].append({
                'slug':    slug,
                'label':   m.get('label', slug),
                'icon':    m.get('icon', '📦'),
                'color':   m.get('color', '#f5a623'),
                'url':     f"/addons/modules/{slug}/app",
                'version': m.get('version', ''),
            })

        result = sorted(sections.values(), key=lambda s: s['order'])
        for s in result:
            s['items'].sort(key=lambda i: i['label'])
        return result

    def update_manifest(self, slug: str, updates: Dict) -> bool:
        """Write/update manifest.json for a module."""
        d = self.addons_dir / slug
        if not d.exists():
            return False
        manifest_path = d / 'manifest.json'
        existing = {}
        if manifest_path.exists():
            try:
                existing = json.loads(manifest_path.read_text(encoding='utf-8'))
            except Exception:
                pass
        existing.update(updates)
        existing['slug'] = slug
        manifest_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding='utf-8')
        return True

    # ── Private ───────────────────────────────────────────────────

    def _read_module(self, d: Path) -> Dict:
        slug = d.name

        # 1. Try manifest.json first
        manifest_path = d / 'manifest.json'
        if manifest_path.exists():
            try:
                m = json.loads(manifest_path.read_text(encoding='utf-8'))
                m.setdefault('slug',     slug)
                m.setdefault('has_app',  (d / 'app.py').exists())
                m['_source'] = 'manifest'
                return m
            except Exception:
                pass

        # 2. Fall back to PLUGIN_META in plugin.py
        meta = {}
        plugin_path = d / 'plugin.py'
        if plugin_path.exists():
            try:
                src  = plugin_path.read_text(encoding='utf-8')
                tree = ast.parse(src)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for t in node.targets:
                            if isinstance(t, ast.Name) and t.id == 'PLUGIN_META':
                                try:
                                    meta = ast.literal_eval(node.value)
                                except Exception:
                                    pass
            except Exception:
                pass

        # 3. Build entry from what we know
        cat = KNOWN_CATEGORIES.get(slug, 'uncategorized')
        return {
            'slug':         slug,
            'label':        meta.get('label', slug.replace('-',' ').replace('_',' ').title()),
            'icon':         meta.get('icon', '📦'),
            'color':        meta.get('color', '#f5a623'),
            'description':  meta.get('description', ''),
            'version':      meta.get('version', ''),
            'category':     cat,
            'nav_section':  CATEGORIES.get(cat, CATEGORIES['uncategorized'])['label'],
            'capabilities': meta.get('capabilities', []),
            'requires':     meta.get('requires', []),
            'package':      meta.get('package', ''),
            'has_app':      (d / 'app.py').exists(),
            'has_plugin':   plugin_path.exists(),
            'is_generated': (d / 'plugin.py').exists() and (d / 'app.py').exists(),
            'size_kb':      round(sum(f.stat().st_size for f in d.rglob('*') if f.is_file()) / 1024, 1),
            '_source':      'plugin_meta' if meta else 'filesystem',
        }
