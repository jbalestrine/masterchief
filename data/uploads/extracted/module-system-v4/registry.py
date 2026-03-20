"""
Module Registry  —  Read-Only Mirror of MasterChief's launch_addon Logic
=========================================================================

Scans the SAME locations and uses the SAME detection algorithm as
MasterChief's detect_entry_point() / launch_addon() functions so the
registry is always consistent with what the platform actually does.

Key design decisions (matching main.py behaviour):
  • Modules live in  uploads/extracted/<slug>/  — NOT addons/modules/
  • Blueprint detection: addon.py exists AND contains an  init()  function
  • Entry-point priority list mirrors ENTRY_POINT_PRIORITY in main.py exactly
  • manifest.json is OPTIONAL enrichment; the registry never requires it
  • Live status is queried from MasterChief's /addons/modules/<slug>/status
  • No writes to module directories — this registry is fully read-only
"""

import ast
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ── Entry-point priority list (mirrors ENTRY_POINT_PRIORITY in main.py) ──────
ENTRY_POINT_PRIORITY: List[Tuple[str, str]] = [
    ('main.py',       'python'),
    ('index.py',      'python'),
    ('app.py',        'python'),
    ('run.py',        'python'),
    ('__main__.py',   'python_module'),
    ('install.php',   'php'),
    ('setup.php',     'php'),
    ('installer.php', 'php'),
    ('wizard.php',    'php'),
    ('index.php',     'php'),
    ('main.php',      'php'),
    ('index.html',    'html'),
    ('index.htm',     'html'),
    ('server.js',     'node'),
    ('app.js',        'node'),
    ('index.js',      'node'),
    ('main',          'executable'),
]

# Directories to skip during scanning (mirrors _SKIP_DIRS in main.py)
_SKIP_DIRS = frozenset({
    'node_modules', 'vendor', '__pycache__', 'venv', 'env',
    '.git', 'dist', 'build', 'migrations',
})

# ── Category metadata ─────────────────────────────────────────────────────────
CATEGORIES = {
    'admin_ops':     {'label': 'Admin Ops',       'icon': '⚙',  'order': 1},
    'addons':        {'label': 'Add Ons',          'icon': '🔌', 'order': 2},
    'sys_modules':   {'label': 'Systems Modules',  'icon': '🧩', 'order': 3},
    'integrations':  {'label': 'Integrations',     'icon': '🔗', 'order': 4},
    'devtools':      {'label': 'Dev Tools',        'icon': '🛠', 'order': 5},
    'data':          {'label': 'Data & Analytics', 'icon': '📊', 'order': 6},
    'security':      {'label': 'Security',         'icon': '🔐', 'order': 7},
    'cloud':         {'label': 'Cloud & Infra',    'icon': '☁',  'order': 8},
    'uncategorized': {'label': 'Other',            'icon': '📦', 'order': 99},
}

# Known slug → category hints (used when module has no manifest)
KNOWN_CATEGORIES: Dict[str, str] = {
    'module-system':         'admin_ops',
    'module-system-v2':      'admin_ops',
    'module-system-v3':      'admin_ops',
    'module-system-v3_link': 'admin_ops',
    'module-system-v4_auto_Install': 'admin_ops',
    'diagnostics-alchemy':   'admin_ops',
    'cloud-command':         'cloud',
    'orphan-sweeper':        'sys_modules',
    'blueprint-extractor':   'sys_modules',
    'log-streamer':          'addons',
    'health-monitor':        'addons',
    'env-auditor':           'devtools',
    'db-connector':          'data',
    'desktop-shell':         'admin_ops',
}


# ── Entry-point detection (mirrors detect_entry_point() in main.py) ──────────

def _detect_entry_point(extract_dir: Path) -> Optional[Dict]:
    """
    Mirrors MasterChief's detect_entry_point() — returns a dict describing the
    entry point, or None if nothing is found.
    """
    # ── Pass 1: exact-name priority list (root → immediate subdirs → deep) ──
    search_dirs = [extract_dir]
    try:
        for d in extract_dir.iterdir():
            if d.is_dir() and not d.name.startswith('.') and d.name not in ('node_modules', 'vendor', '__pycache__', '.git', 'venv', 'env'):
                search_dirs.append(d)
    except Exception:
        pass

    deep_dirs = []
    try:
        for d in extract_dir.rglob('*'):
            if d.is_dir() and not any(
                p.startswith('.') or p in ('node_modules', 'vendor', '__pycache__', 'venv', 'env')
                for p in d.parts
            ):
                if d not in search_dirs:
                    deep_dirs.append(d)
    except Exception:
        pass

    for search_dir in search_dirs + deep_dirs:
        for fname, handler in ENTRY_POINT_PRIORITY:
            candidate = search_dir / fname
            if candidate.exists():
                return {'file': candidate, 'working_dir': search_dir, 'type': handler}

    # ── Pass 2: fuzzy fallback ────────────────────────────────────────────────
    _PY_HINTS  = {'start', 'run', 'server', 'api', 'application', 'bootstrap', 'launch', 'web', 'http', 'serve', 'bot', 'app', 'main'}
    _PHP_HINTS = {'start', 'run', 'server', 'api', 'bootstrap', 'launch', 'app', 'web', 'portal', 'admin', 'home'}
    _JS_HINTS  = {'start', 'run', 'server', 'api', 'index', 'app', 'main', 'http', 'bot', 'web'}

    best_py = best_php = best_js = best_html = None
    best_py_s = best_php_s = best_js_s = best_html_s = 999

    try:
        for f in extract_dir.rglob('*'):
            if not f.is_file():
                continue
            if any(p in _SKIP_DIRS for p in f.parts):
                continue
            depth = len(f.relative_to(extract_dir).parts)
            stem = f.stem.lower()
            ext  = f.suffix.lower()

            if ext == '.py':
                score = depth + (0 if stem in _PY_HINTS else 5)
                if score < best_py_s:
                    best_py_s, best_py = score, f
            elif ext == '.php':
                score = depth + (0 if stem in _PHP_HINTS else 5)
                if score < best_php_s:
                    best_php_s, best_php = score, f
            elif ext == '.js' and not f.name.endswith('.min.js'):
                score = depth + (0 if stem in _JS_HINTS else 5)
                if score < best_js_s:
                    best_js_s, best_js = score, f
            elif ext in ('.html', '.htm'):
                if depth < best_html_s:
                    best_html_s, best_html = depth, f
    except Exception:
        pass

    for candidate, handler in [(best_py, 'python'), (best_php, 'php'), (best_js, 'node'), (best_html, 'html')]:
        if candidate is not None:
            return {'file': candidate, 'working_dir': candidate.parent, 'type': handler}

    return None


def _is_blueprint(module_dir: Path) -> bool:
    """
    Returns True if addon.py exists AND contains an init() function —
    which is the same condition MasterChief uses to choose Blueprint vs subprocess.
    """
    addon_py = module_dir / 'addon.py'
    if not addon_py.exists():
        return False
    try:
        src  = addon_py.read_text(encoding='utf-8', errors='ignore')
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == 'init':
                return True
    except Exception:
        pass
    return False


# ── Registry class ────────────────────────────────────────────────────────────

class Registry:
    """
    Read-only registry that mirrors MasterChief's addon loader.

    Parameters
    ----------
    extracted_dir : Path
        Path to uploads/extracted/  (where module folders actually live).
        This is app.config['UPLOAD_FOLDER'] / 'extracted' in main.py.
    registry_path : Path
        Where to write registry.json (consumed by the Module Command Center UI).
    masterchief_base : str
        Base URL of the MasterChief platform, e.g. 'http://127.0.0.1:8080'.
        Used to query live status from /addons/modules/<slug>/status.
    """

    def __init__(
        self,
        extracted_dir: Path,
        registry_path: Path,
        masterchief_base: str = 'http://127.0.0.1:8080',
    ):
        self.extracted_dir    = extracted_dir
        self.registry_path    = registry_path
        self.masterchief_base = masterchief_base.rstrip('/')
        self._data: Dict      = {}

    # ── Public API ─────────────────────────────────────────────────────────

    def discover(self) -> Dict:
        """
        Scan uploads/extracted/, build registry, write registry.json.
        This is the main entry point — call it to refresh.
        """
        modules: Dict[str, Dict] = {}
        errors:  List[str]       = []

        if not self.extracted_dir.exists():
            return {
                'modules': {},
                'errors':  [f'extracted dir not found: {self.extracted_dir}'],
            }

        for d in sorted(self.extracted_dir.iterdir()):
            if not d.is_dir() or d.name.startswith('.') or d.name.startswith('_'):
                continue
            try:
                entry = self._read_module(d)
                modules[d.name] = entry
            except Exception as exc:
                errors.append(f'{d.name}: {exc}')

        # Resolve dependency status across all discovered modules
        all_caps = set()
        for m in modules.values():
            all_caps.update(m.get('capabilities', []))
        for m in modules.values():
            broken = [r for r in m.get('requires', []) if r not in all_caps]
            m['deps_ok']     = not broken
            m['broken_deps'] = broken

        self._data = {
            'modules':      modules,
            'categories':   CATEGORIES,
            'errors':       errors,
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'count':        len(modules),
        }
        self._data['_nav_sections'] = self.nav_sections()

        self.registry_path.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False),
            encoding='utf-8',
        )
        return self._data

    def get(self) -> Dict:
        """Return cached registry; re-discover if not loaded."""
        if not self._data and self.registry_path.exists():
            try:
                self._data = json.loads(self.registry_path.read_text(encoding='utf-8'))
            except Exception:
                return self.discover()
        return self._data or self.discover()

    def capabilities(self) -> Dict[str, List[str]]:
        """Return map of capability → list of module slugs that provide it."""
        cap_map: Dict[str, List[str]] = {}
        for slug, m in self.get().get('modules', {}).items():
            for cap in m.get('capabilities', []):
                cap_map.setdefault(cap, []).append(slug)
        return cap_map

    def nav_sections(self) -> List[Dict]:
        """
        Build sidebar nav structure for MasterChief injection.
        Only includes modules that have a launchable entry point.
        """
        sections: Dict[str, Dict] = {}
        for slug, m in self.get().get('modules', {}).items():
            if not m.get('launchable'):
                continue
            cat      = m.get('category', 'uncategorized')
            cat_info = CATEGORIES.get(cat, CATEGORIES['uncategorized'])
            if cat not in sections:
                sections[cat] = {
                    'id':    cat,
                    'label': cat_info['label'],
                    'icon':  cat_info['icon'],
                    'order': cat_info['order'],
                    'items': [],
                }
            # Blueprint modules proxy at /modules/<slug>/, subprocess at /addons/modules/<slug>/app/
            url = (
                f"/modules/{slug}/"
                if m.get('loader_type') == 'blueprint'
                else f"/addons/modules/{slug}/app/"
            )
            sections[cat]['items'].append({
                'slug':        slug,
                'label':       m.get('label', slug),
                'icon':        m.get('icon', '📦'),
                'color':       m.get('color', '#f5a623'),
                'url':         url,
                'loader_type': m.get('loader_type', 'subprocess'),
                'version':     m.get('version', ''),
            })

        result = sorted(sections.values(), key=lambda s: s['order'])
        for s in result:
            s['items'].sort(key=lambda i: i['label'])
        return result

    def live_status(self, slug: str) -> Dict:
        """
        Query MasterChief's /addons/modules/<slug>/status to get live state.
        Falls back gracefully if MasterChief is unreachable.
        Returns: {'status': 'running'|'stopped'|'blueprint'|'unknown', ...}
        """
        try:
            url = f"{self.masterchief_base}/addons/modules/{slug}/status"
            r   = requests.get(url, timeout=2)
            if r.ok:
                return r.json()
        except Exception:
            pass
        return {'status': 'unknown'}

    # ── Private ────────────────────────────────────────────────────────────

    def _read_module(self, module_dir: Path) -> Dict:
        """
        Build a registry entry for a single module directory.

        Priority for enrichment metadata:
          1. manifest.json  (optional — never required)
          2. PLUGIN_META in plugin.py  (optional — never required)
          3. Filesystem inspection  (always runs — determines launchability)
        """
        slug = module_dir.name

        # ── Optional enrichment from manifest.json ─────────────────────────
        manifest: Dict = {}
        manifest_path = module_dir / 'manifest.json'
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            except Exception:
                pass

        # ── Optional enrichment from PLUGIN_META in plugin.py ─────────────
        plugin_meta: Dict = {}
        plugin_path = module_dir / 'plugin.py'
        if plugin_path.exists():
            try:
                src  = plugin_path.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(src)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for t in node.targets:
                            if isinstance(t, ast.Name) and t.id == 'PLUGIN_META':
                                try:
                                    plugin_meta = ast.literal_eval(node.value)
                                except Exception:
                                    pass
            except Exception:
                pass

        # Merge enrichment: manifest wins over plugin_meta for the same key
        meta = {**plugin_meta, **manifest}

        # ── Filesystem inspection (this is what actually matters) ──────────
        blueprint    = _is_blueprint(module_dir)
        ep           = _detect_entry_point(module_dir) if not blueprint else None
        launchable   = blueprint or (ep is not None)
        loader_type  = 'blueprint' if blueprint else ('subprocess' if ep else 'none')
        entry_file   = (
            'addon.py'        if blueprint
            else (ep['file'].name if ep else None)
        )
        entry_handler = (
            'blueprint'       if blueprint
            else (ep['type'] if ep else None)
        )

        # Size (skipping cache/vcs dirs)
        try:
            size_kb = round(
                sum(
                    f.stat().st_size
                    for f in module_dir.rglob('*')
                    if f.is_file() and not any(
                        p in _SKIP_DIRS
                        for p in f.relative_to(module_dir).parts
                    )
                ) / 1024,
                1,
            )
        except Exception:
            size_kb = 0

        # Category — manifest > plugin_meta > KNOWN_CATEGORIES > uncategorized
        cat = meta.get('category') or KNOWN_CATEGORIES.get(slug, 'uncategorized')

        return {
            # ── Identity ──────────────────────────────────────────────────
            'slug':         slug,
            'label':        meta.get('label', slug.replace('-', ' ').replace('_', ' ').title()),
            'icon':         meta.get('icon', '📦'),
            'color':        meta.get('color', '#f5a623'),
            'description':  meta.get('description', ''),
            'version':      meta.get('version', ''),
            'category':     cat,
            'nav_section':  CATEGORIES.get(cat, CATEGORIES['uncategorized'])['label'],

            # ── Capability bus ────────────────────────────────────────────
            'capabilities': meta.get('capabilities', []),
            'requires':     meta.get('requires', []),

            # ── Loader info (mirrors what launch_addon() would do) ─────────
            'loader_type':   loader_type,    # 'blueprint' | 'subprocess' | 'none'
            'entry_file':    entry_file,     # 'app.py' | 'addon.py' | 'main.py' | None
            'entry_handler': entry_handler,  # 'python' | 'php' | 'node' | 'html' | 'blueprint' | None
            'launchable':    launchable,

            # ── Convenience flags ─────────────────────────────────────────
            'has_addon_py':      (module_dir / 'addon.py').exists(),
            'has_plugin_py':     plugin_path.exists(),
            'has_manifest':      manifest_path.exists(),
            'has_requirements':  (module_dir / 'requirements.txt').exists(),

            # ── Filesystem metadata ────────────────────────────────────────
            'path':     str(module_dir),
            'size_kb':  size_kb,
            '_source':  (
                'manifest'    if manifest_path.exists() else
                'plugin_meta' if plugin_meta else
                'filesystem'
            ),
        }
