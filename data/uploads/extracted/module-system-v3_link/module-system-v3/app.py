"""
Module Command Center v3 — MasterChief Addon

Panels:
  MARKETPLACE   Browse + search all installed pip packages
  GENERATE      Pick features, preview, generate addon zip
  INSTALLED     View, launch, restart, remove installed addons
  IMPORT        Install zip from filesystem (generated folder)
  PYPI SEARCH   Search PyPI for new packages
  LOGS          View per-addon logs
"""
import os
import sys
import json
import time
import shutil
import zipfile
import tempfile
import subprocess
from pathlib import Path
from flask import Flask, jsonify, request, Response

BASE_DIR   = Path(__file__).parent
ADDON_NAME = os.environ.get('MC_ADDON_NAME', BASE_DIR.name)
MC_ROOT    = Path(os.environ.get('MC_ROOT', BASE_DIR.parent.parent.parent.parent))
ADDONS_DIR = BASE_DIR.parent.parent        # addons/modules/
OUTPUT_DIR = BASE_DIR / 'generated'
OUTPUT_DIR.mkdir(exist_ok=True)
REGISTRY_PATH = ADDONS_DIR.parent / 'registry.json'
registry = Registry(ADDONS_DIR, REGISTRY_PATH)

sys.path.insert(0, str(BASE_DIR))
from introspector import introspect_package
from generator   import generate_module
from registry    import Registry, CATEGORIES

app = Flask(__name__)

@app.errorhandler(404)
def e404(e): return jsonify({'error': 'Not found'}), 404
@app.errorhandler(500)
def e500(e): return jsonify({'error': str(e)}), 500
@app.errorhandler(Exception)
def eany(e): return jsonify({'error': str(e)}), 500


# ════════════════════════════════════════════════════════════
#  API
# ════════════════════════════════════════════════════════════

@app.route('/api/packages')
def api_packages():
    try:
        r = subprocess.run(
            [sys.executable, '-m', 'pip', 'list', '--format=json'],
            capture_output=True, text=True, timeout=15
        )
        pkgs = json.loads(r.stdout) if r.returncode == 0 else []
        return jsonify({'packages': pkgs, 'count': len(pkgs)})
    except Exception as e:
        return jsonify({'error': str(e), 'packages': []})


@app.route('/api/introspect')
def api_introspect():
    pkg = request.args.get('package', '').strip()
    if not pkg:
        return jsonify({'error': 'package param required'}), 400
    return jsonify(introspect_package(pkg))


@app.route('/api/generate')
def api_generate():
    pkg      = request.args.get('package', '').strip()
    features = [f.strip() for f in request.args.get('features', '').split(',') if f.strip()]
    slug     = request.args.get('slug', '').strip() or pkg.replace('-','_').replace('.','_')
    if not pkg:      return jsonify({'error': 'package required'}), 400
    if not features: return jsonify({'error': 'select at least one feature'}), 400
    try:
        result = generate_module(pip_name=pkg, slug=slug, features=features, output_dir=OUTPUT_DIR)
        if result.get('success'):
            result['zip_name'] = Path(result['zip_path']).name
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<filename>')
def download(filename):
    safe = OUTPUT_DIR / Path(filename).name
    if not safe.exists() or safe.suffix != '.zip':
        return 'Not found', 404
    return Response(
        safe.read_bytes(),
        mimetype='application/zip',
        headers={'Content-Disposition': f'attachment; filename="{safe.name}"'}
    )


@app.route('/api/generated')
def api_generated():
    zips = sorted(OUTPUT_DIR.glob('*.zip'), key=lambda p: p.stat().st_mtime, reverse=True)
    return jsonify([{
        'slug':    z.stem,
        'zip_name': z.name,
        'size':    z.stat().st_size,
        'mtime':   int(z.stat().st_mtime),
    } for z in zips])


@app.route('/api/install')
def api_install():
    """Copy a generated zip into addons/modules/ and extract it."""
    slug = request.args.get('slug', '').strip()
    if not slug:
        return jsonify({'error': 'slug required'}), 400
    zip_path = OUTPUT_DIR / f'{slug}.zip'
    if not zip_path.exists():
        return jsonify({'error': f'{slug}.zip not found in generated/'}), 404
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            tops  = {n.split('/')[0] for n in names if '/' in n}
            if len(tops) != 1:
                return jsonify({'error': 'zip must have one top-level folder'}), 400
            extracted = tops.pop()
            for n in names:
                if '..' in n or n.startswith('/'):
                    return jsonify({'error': f'unsafe path in zip: {n}'}), 400
            dest = ADDONS_DIR / extracted
            if dest.exists():
                shutil.rmtree(dest)
            zf.extractall(str(ADDONS_DIR))
        return jsonify({
            'success':  True,
            'slug':     extracted,
            'path':     str(dest),
            'message':  f'Installed to addons/modules/{extracted}/ — reload addon manager to activate',
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/installed')
def api_installed():
    """List all installed addon modules with status info."""
    modules = []
    if not ADDONS_DIR.exists():
        return jsonify({'modules': [], 'error': f'addons dir not found: {ADDONS_DIR}'})
    for d in sorted(ADDONS_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith('.') or d.name.startswith('_'):
            continue
        has_app     = (d / 'app.py').exists()
        has_plugin  = (d / 'plugin.py').exists()
        has_req     = (d / 'requirements.txt').exists()
        is_generated = has_plugin and has_app
        meta = {}
        if has_plugin:
            try:
                # Read PLUGIN_META from plugin.py without importing it
                src = (d / 'plugin.py').read_text(encoding='utf-8')
                import ast
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
        modules.append({
            'slug':         d.name,
            'has_app':      has_app,
            'has_plugin':   has_plugin,
            'is_generated': is_generated,
            'label':        meta.get('label', d.name),
            'icon':         meta.get('icon', '📦'),
            'color':        meta.get('color', '#f5a623'),
            'package':      meta.get('package', ''),
            'size_kb':      round(sum(f.stat().st_size for f in d.rglob('*') if f.is_file()) / 1024, 1),
            'file_count':   len(list(d.rglob('*'))),
            'has_zip':      (OUTPUT_DIR / f'{d.name}.zip').exists(),
        })
    return jsonify({'modules': modules, 'count': len(modules)})


@app.route('/api/remove')
def api_remove():
    """Delete an installed addon module folder."""
    slug = request.args.get('slug', '').strip()
    if not slug or '/' in slug or '..' in slug:
        return jsonify({'error': 'invalid slug'}), 400
    target = ADDONS_DIR / slug
    if not target.exists():
        return jsonify({'error': f'{slug} not found'}), 404
    try:
        shutil.rmtree(target)
        return jsonify({'success': True, 'message': f'{slug} removed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/module-files')
def api_module_files():
    """Return file list + content for a module."""
    slug = request.args.get('slug', '').strip()
    if not slug or '/' in slug or '..' in slug:
        return jsonify({'error': 'invalid slug'}), 400
    d = ADDONS_DIR / slug
    if not d.exists():
        return jsonify({'error': 'not found'}), 404
    files = []
    for f in sorted(d.rglob('*')):
        if f.is_file() and not any(p in str(f) for p in ['__pycache__', '.pyc']):
            try:
                content = f.read_text(encoding='utf-8')
            except Exception:
                content = '<binary>'
            files.append({
                'name':    f.name,
                'path':    str(f.relative_to(d)),
                'size':    f.stat().st_size,
                'content': content[:8000],
            })
    return jsonify({'slug': slug, 'files': files})


@app.route('/api/pip-install')
def api_pip_install():
    """Install a package via pip."""
    pkg = request.args.get('package', '').strip()
    if not pkg or any(c in pkg for c in [';', '&', '|', '`', '$', '\n']):
        return jsonify({'error': 'invalid package name'}), 400
    try:
        r = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', pkg, '--break-system-packages'],
            capture_output=True, text=True, timeout=120
        )
        return jsonify({
            'success': r.returncode == 0,
            'output':  (r.stdout + r.stderr)[-3000:],
            'package': pkg,
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'pip install timed out after 120s'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pypi-search')
def api_pypi_search():
    """Search PyPI for packages."""
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'results': []})
    try:
        import urllib.request, urllib.parse
        url = f'https://pypi.org/search/?q={urllib.parse.quote(q)}&format=json'
        # Use pip search via subprocess as fallback
        r = subprocess.run(
            [sys.executable, '-m', 'pip', 'index', 'versions', q],
            capture_output=True, text=True, timeout=15
        )
        # Parse simple output
        results = []
        if r.returncode == 0 and r.stdout:
            results.append({'name': q, 'summary': r.stdout.strip()[:200]})
        return jsonify({'results': results, 'query': q})
    except Exception as e:
        return jsonify({'error': str(e), 'results': []})


@app.route('/api/addon-logs')
def api_addon_logs():
    """Read log output for an addon from MC_ROOT log files."""
    slug = request.args.get('slug', '').strip()
    lines = int(request.args.get('lines', 100))
    log_candidates = [
        MC_ROOT / 'logs' / f'{slug}.log',
        MC_ROOT / f'{slug}.log',
        BASE_DIR.parent.parent / f'{slug}.log',
        MC_ROOT / 'debug.log',
        MC_ROOT / 'server_out.txt',
    ]
    for log_path in log_candidates:
        if log_path.exists():
            try:
                content = log_path.read_text(encoding='utf-8', errors='replace')
                all_lines = content.splitlines()
                # Filter for slug if using combined log
                if slug and log_path.name in ('debug.log', 'server_out.txt'):
                    filtered = [l for l in all_lines if slug.lower() in l.lower()]
                    return jsonify({'lines': filtered[-lines:], 'source': str(log_path)})
                return jsonify({'lines': all_lines[-lines:], 'source': str(log_path)})
            except Exception as e:
                continue
    return jsonify({'lines': [], 'source': None, 'note': 'No log file found'})


@app.route('/api/delete-generated')
def api_delete_generated():
    """Delete a generated zip."""
    slug = request.args.get('slug', '').strip()
    if not slug or '/' in slug or '..' in slug:
        return jsonify({'error': 'invalid slug'}), 400
    zip_path = OUTPUT_DIR / f'{slug}.zip'
    if not zip_path.exists():
        return jsonify({'error': 'not found'}), 404
    zip_path.unlink()
    mod_dir = OUTPUT_DIR / slug
    if mod_dir.exists():
        shutil.rmtree(mod_dir)
    return jsonify({'success': True})


# ════════════════════════════════════════════════════════════
#  Registry & Platform API
# ════════════════════════════════════════════════════════════

@app.route('/api/registry')
def api_registry():
    """Full module registry — also written to addons/registry.json for main.py."""
    return jsonify(registry.discover())

@app.route('/api/nav-sections')
def api_nav_sections():
    """Nav sections grouped by category — consumed by main.py sidebar."""
    return jsonify({'sections': registry.nav_sections()})

@app.route('/api/capabilities')
def api_capabilities():
    """Capability map: capability → [modules that provide it]."""
    return jsonify(registry.capabilities())

@app.route('/api/update-manifest')
def api_update_manifest():
    """Update manifest.json for a module (category, label, capabilities etc)."""
    slug = request.args.get('slug','').strip()
    if not slug or '/' in slug:
        return jsonify({'error': 'invalid slug'}), 400
    updates = {}
    for k in ['label','icon','color','category','description','version']:
        v = request.args.get(k)
        if v is not None:
            updates[k] = v
    caps = request.args.get('capabilities')
    if caps is not None:
        updates['capabilities'] = [c.strip() for c in caps.split(',') if c.strip()]
    reqs = request.args.get('requires')
    if reqs is not None:
        updates['requires'] = [r.strip() for r in reqs.split(',') if r.strip()]
    ok = registry.update_manifest(slug, updates)
    if ok:
        return jsonify({'success': True, 'slug': slug, 'updates': updates})
    return jsonify({'error': f'{slug} not found'}), 404

@app.route('/api/write-registry')
def api_write_registry():
    """Force re-discover and write registry.json — call after installs."""
    data = registry.discover()
    return jsonify({'success': True, 'count': data.get('count', 0),
                    'path': str(REGISTRY_PATH)})

# ════════════════════════════════════════════════════════════
#  Main UI
# ════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return _ui_html()

def _ui_html():
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Module Command Center</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Unbounded:wght@400;700;900&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#060809;--panel:#0a0d10;--card:#0e1419;--border:#1a2535;
  --amber:#f5a623;--green:#00ff88;--red:#ff4444;--blue:#58a6ff;--purple:#a78bfa;
  --text:#cdd6e0;--dim:#4a6070;--mid:#7a9ab0;
  --mono:"Space Mono",monospace;--ui:"Unbounded",sans-serif;
}
html,body{min-height:100vh;background:var(--bg);color:var(--text);font-family:var(--mono);font-size:13px}

/* Layout */
.shell{display:flex;flex-direction:column;height:100vh}
header{display:flex;align-items:center;padding:0 20px;height:50px;background:var(--panel);
  border-bottom:1px solid var(--border);flex-shrink:0;gap:0;z-index:100}
.logo{font-family:var(--ui);font-size:10px;font-weight:900;letter-spacing:.35em;
  margin-right:24px;white-space:nowrap}
.logo span{color:var(--amber)}
.tabs{display:flex;height:50px;flex:1;overflow-x:auto}
.tab{padding:0 18px;display:flex;align-items:center;gap:7px;font-size:10px;letter-spacing:.1em;
  color:var(--dim);border-bottom:2px solid transparent;cursor:pointer;white-space:nowrap;
  transition:all .15s;user-select:none}
.tab:hover{color:var(--text)}
.tab.active{color:var(--amber);border-bottom-color:var(--amber)}
.tab .badge{background:var(--amber);color:#000;font-size:8px;font-weight:700;
  padding:1px 5px;border-radius:2px}
.content{flex:1;overflow-y:auto;padding:28px 28px}

/* Cards & Grids */
.pkg-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px;margin-top:20px}
.pkg-card{background:var(--card);border:1px solid var(--border);border-left:3px solid var(--border);
  border-radius:3px;padding:14px;cursor:pointer;transition:border-color .15s}
.pkg-card:hover{border-color:var(--amber);border-left-color:var(--amber)}
.pkg-name{font-family:var(--ui);font-size:11px;font-weight:700;margin-bottom:2px}
.pkg-ver{font-size:10px;color:var(--dim);margin-bottom:8px}
.pkg-hint{font-size:10px;color:var(--mid)}

.mod-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px;margin-top:20px}
.mod-card{background:var(--card);border:1px solid var(--border);border-radius:3px;padding:16px;
  border-left:3px solid var(--border)}
.mod-card-head{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.mod-icon{font-size:22px}
.mod-title{font-family:var(--ui);font-size:11px;font-weight:700}
.mod-slug{font-size:10px;color:var(--dim)}
.mod-actions{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
.mod-meta{font-size:10px;color:var(--mid);margin-bottom:4px}

/* Generate panel */
.gen-layout{display:grid;grid-template-columns:1fr 360px;gap:20px;align-items:start;margin-top:20px}
.feat-panel{background:var(--card);border:1px solid var(--border);border-radius:3px;padding:18px}
.feat-panel h3{font-family:var(--ui);font-size:11px;font-weight:700;margin-bottom:12px}
.feat-list{max-height:400px;overflow-y:auto;margin-bottom:12px}
.feat-row{display:flex;align-items:flex-start;gap:8px;padding:5px 0;
  border-bottom:1px solid rgba(26,37,53,.5);cursor:pointer}
.feat-row:hover{background:rgba(245,166,35,.03)}
.feat-row label{font-size:11px;flex:1;cursor:pointer;line-height:1.4}
.feat-row input[type=checkbox]{accent-color:var(--amber);margin-top:2px;flex-shrink:0}
.feat-type{font-size:8px;color:var(--dim);letter-spacing:.05em}
.slug-row{display:flex;align-items:center;gap:8px;margin-bottom:12px}
.slug-row label{font-size:10px;color:var(--dim);white-space:nowrap}
.slug-row input{flex:1}
.out-panel{background:var(--card);border:1px solid var(--border);border-radius:3px;padding:18px}
.out-panel h3{font-family:var(--ui);font-size:11px;font-weight:700;margin-bottom:12px}

/* Generated list */
.gen-list{margin-top:20px}
.gen-row{display:flex;align-items:center;gap:10px;padding:10px 0;
  border-bottom:1px solid rgba(26,37,53,.5)}
.gen-row-name{font-size:12px;font-weight:600;flex:1}
.gen-row-size{font-size:10px;color:var(--dim);white-space:nowrap}

/* Logs panel */
.log-terminal{background:#000;border:1px solid var(--border);border-radius:3px;
  padding:14px;font-family:var(--mono);font-size:11px;line-height:1.7;
  max-height:500px;overflow-y:auto;color:#aaa}
.log-line{white-space:pre-wrap;word-break:break-all}
.log-err{color:var(--red)}
.log-ok{color:var(--green)}
.log-warn{color:var(--amber)}

/* File viewer */
.file-tree{background:var(--card);border:1px solid var(--border);border-radius:3px;
  padding:12px;max-height:200px;overflow-y:auto;margin-bottom:16px}
.file-item{font-size:11px;color:var(--mid);padding:3px 0;cursor:pointer;border-radius:2px;
  padding-left:8px}
.file-item:hover,.file-item.active{color:var(--amber)}
pre{background:#000;border:1px solid var(--border);border-radius:3px;
  padding:14px;font-size:11px;line-height:1.6;overflow-x:auto;white-space:pre;
  color:#cdd6e0;max-height:400px;overflow-y:auto}

/* Misc */
.page-head{margin-bottom:6px}
.page-title{font-family:var(--ui);font-size:clamp(18px,3vw,32px);font-weight:900;line-height:1}
.page-title em{font-style:normal;-webkit-text-stroke:2px var(--amber);color:transparent}
.page-sub{color:var(--dim);font-size:11px;margin-top:4px;margin-bottom:20px}
.search-row{display:flex;gap:10px;margin-bottom:4px}
.search-row input{flex:1;padding:9px 12px;font-size:12px}
.btn{background:var(--amber);color:#000;font-family:var(--mono);font-size:10px;font-weight:700;
  letter-spacing:.12em;padding:7px 16px;border:none;border-radius:2px;cursor:pointer;
  transition:opacity .15s;white-space:nowrap}
.btn:hover{opacity:.85}
.btn-sm{padding:4px 10px;font-size:9px}
.btn-ghost{background:transparent;color:var(--mid);font-family:var(--mono);font-size:10px;
  letter-spacing:.08em;padding:6px 12px;border:1px solid var(--border);border-radius:2px;
  cursor:pointer;transition:all .15s;white-space:nowrap}
.btn-ghost:hover{border-color:var(--amber);color:var(--amber)}
.btn-danger{background:transparent;color:var(--red);font-family:var(--mono);font-size:10px;
  padding:6px 12px;border:1px solid rgba(255,68,68,.3);border-radius:2px;cursor:pointer}
.btn-danger:hover{background:rgba(255,68,68,.1)}
input,select{background:var(--card);border:1px solid var(--border);color:var(--text);
  font-family:var(--mono);font-size:12px;padding:8px 12px;border-radius:2px;outline:none}
input:focus,select:focus{border-color:var(--amber)}
.tag{display:inline-block;padding:1px 7px;border-radius:2px;font-size:9px;border:1px solid;margin-right:3px}
.tag-blue{background:rgba(88,166,255,.1);color:var(--blue);border-color:rgba(88,166,255,.2)}
.tag-green{background:rgba(0,255,136,.1);color:var(--green);border-color:rgba(0,255,136,.2)}
.tag-amber{background:rgba(245,166,35,.1);color:var(--amber);border-color:rgba(245,166,35,.2)}
.tag-red{background:rgba(255,68,68,.1);color:var(--red);border-color:rgba(255,68,68,.2)}
.err-box{background:rgba(255,68,68,.05);border:1px solid rgba(255,68,68,.2);
  color:var(--red);padding:12px;border-radius:2px;font-size:12px;margin:10px 0}
.ok-box{background:rgba(0,255,136,.05);border:1px solid rgba(0,255,136,.2);
  color:var(--green);padding:12px;border-radius:2px;font-size:12px;margin:10px 0}
.info-box{background:rgba(88,166,255,.05);border:1px solid rgba(88,166,255,.2);
  color:var(--blue);padding:12px;border-radius:2px;font-size:12px;margin:10px 0}
.loading{color:var(--dim);text-align:center;padding:40px;font-size:12px}
.stat-row{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:20px}
.stat{background:var(--card);border:1px solid var(--border);border-left:3px solid var(--amber);
  padding:10px 14px;border-radius:2px;min-width:100px}
.stat-label{font-size:9px;color:var(--dim);letter-spacing:.15em;margin-bottom:3px}
.stat-val{font-size:20px;font-weight:700;color:var(--amber)}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
</style>
</head>
<body>
<div class="shell">

<header>
  <div class="logo"><span>[</span>MODULE CENTER<span>]</span></div>
  <div class="tabs" id="tabs">
    <div class="tab active" data-tab="marketplace">📦 MARKETPLACE</div>
    <div class="tab" data-tab="generate">⚡ GENERATE</div>
    <div class="tab" data-tab="installed">🗂 INSTALLED <span class="badge" id="installed-badge">…</span></div>
    <div class="tab" data-tab="generated-list">📁 GENERATED <span class="badge" id="gen-badge">…</span></div>
    <div class="tab" data-tab="pip-manager">🐍 PIP</div>
    <div class="tab" data-tab="logs">📋 LOGS</div>
    <div class="tab" data-tab="registry">🗺 REGISTRY</div>
    <div class="tab" data-tab="platform">⚡ PLATFORM</div>
  </div>
</header>

<div class="content" id="content">
  <div class="loading">Loading…</div>
</div>

</div>

<script>
// ── PROXY_BASE detection ─────────────────────────────────────────
(function() {
  var m = window.location.pathname.match(/^(\/addons\/modules\/[^/]+\/app)/);
  window.PB = m ? m[1] : '';
})();

async function apiFetch(path, params) {
  var qs = params ? '?' + new URLSearchParams(params) : '';
  var r  = await fetch(window.PB + '/api/' + path + qs);
  var txt = await r.text();
  try { return JSON.parse(txt); }
  catch(e) { throw new Error('Non-JSON: ' + txt.slice(0,200)); }
}

// ── Tab routing ──────────────────────────────────────────────────
var _tab = 'marketplace';
var _generatePkg = null;
var _generateFeats = [];

document.getElementById('tabs').addEventListener('click', function(e) {
  var t = e.target.closest('.tab');
  if (!t) return;
  switchTab(t.dataset.tab);
});

function switchTab(name) {
  _tab = name;
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === name));
  renderTab(name);
}

function renderTab(name) {
  var c = document.getElementById('content');
  c.innerHTML = '<div class="loading">Loading…</div>';
  switch(name) {
    case 'marketplace':    loadMarketplace(); break;
    case 'generate':       loadGenerate(_generatePkg); break;
    case 'installed':      loadInstalled(); break;
    case 'generated-list': loadGeneratedList(); break;
    case 'pip-manager':    loadPip(); break;
    case 'logs':           loadLogs(); break;
    case 'registry':       loadRegistry(); break;
    case 'platform':       loadPlatform(); break;
  }
}

// ════════════════════════════════════════════════════════════════
//  MARKETPLACE
// ════════════════════════════════════════════════════════════════
var _allPkgs = [];

async function loadMarketplace() {
  var c = document.getElementById('content');
  c.innerHTML = `
    <div class="page-head">
      <div class="page-title"><em>MODULE</em> MARKETPLACE</div>
      <div class="page-sub">Browse all installed pip packages — click one to generate a MasterChief module</div>
    </div>
    <div class="search-row">
      <input id="pkg-search" type="text" placeholder="Search ${_allPkgs.length || '…'} packages…" oninput="filterPkgs(this.value)"/>
      <button class="btn-ghost" onclick="switchTab('pip-manager')">+ Install Package</button>
    </div>
    <div class="stat-row" id="mkt-stats"></div>
    <div class="pkg-grid" id="pkg-grid"><div class="loading">Loading packages…</div></div>`;

  try {
    var d = await apiFetch('packages');
    _allPkgs = d.packages || [];
    document.getElementById('pkg-search').placeholder = `Search ${_allPkgs.length} packages…`;
    document.getElementById('mkt-stats').innerHTML = `
      <div class="stat"><div class="stat-label">PACKAGES</div><div class="stat-val">${_allPkgs.length}</div></div>`;
    renderPkgGrid(_allPkgs);
  } catch(e) {
    document.getElementById('pkg-grid').innerHTML = `<div class="err-box">Error: ${e.message}</div>`;
  }
}

const PALETTE = ['#f5a623','#58a6ff','#00ff88','#ff6b6b','#a78bfa','#34d399','#fb7185','#38bdf8'];
const ICONS   = ['📦','🔧','⚡','🌐','🛠','🔌','💡','🚀','🔍','📊','🗄','🔐','☁','🖥','🧩','⚙','🎯','🔬'];

function renderPkgGrid(pkgs) {
  var el = document.getElementById('pkg-grid');
  if (!el) return;
  if (!pkgs.length) { el.innerHTML = '<div class="loading">No packages found</div>'; return; }
  el.innerHTML = pkgs.map((p,i) => {
    var col = PALETTE[i % PALETTE.length];
    var ico = ICONS[i % ICONS.length];
    var tags = inferTags(p.name).map(t => `<span class="tag tag-blue">${t}</span>`).join('');
    return `<div class="pkg-card" onclick="openGenerate('${p.name}')" style="border-left-color:${col}">
      <div class="pkg-name">${ico} ${p.name}</div>
      <div class="pkg-ver">v${p.version}</div>
      <div style="margin-bottom:8px">${tags}</div>
      <div class="pkg-hint">Click to generate module →</div>
    </div>`;
  }).join('');
}

function filterPkgs(q) {
  q = q.toLowerCase();
  renderPkgGrid(q ? _allPkgs.filter(p => p.name.toLowerCase().includes(q)) : _allPkgs);
}

function inferTags(n) {
  n = n.toLowerCase(); var t = [];
  if (n.includes('azure')) t.push('azure');
  if (n.includes('aws') || n.includes('boto')) t.push('aws');
  if (n.includes('kube') || n.includes('docker') || n.includes('container')) t.push('infra');
  if (n.includes('sql') || n.includes('db') || n.includes('mongo') || n.includes('redis')) t.push('data');
  if (n.includes('flask') || n.includes('http') || n.includes('request') || n.includes('api')) t.push('web');
  if (n.includes('auth') || n.includes('jwt') || n.includes('crypt') || n.includes('ssl')) t.push('security');
  if (!t.length) t.push('utility');
  return t.slice(0,3);
}

function openGenerate(pkg) {
  _generatePkg = pkg;
  _generateFeats = [];
  switchTab('generate');
}

// ════════════════════════════════════════════════════════════════
//  GENERATE
// ════════════════════════════════════════════════════════════════
var _feats = [];

async function loadGenerate(pkg) {
  var c = document.getElementById('content');
  if (!pkg) {
    c.innerHTML = `
      <div class="page-head">
        <div class="page-title"><em>GENERATE</em> MODULE</div>
        <div class="page-sub">Select a package from the Marketplace to begin</div>
      </div>
      <button class="btn-ghost" onclick="switchTab('marketplace')">← Back to Marketplace</button>`;
    return;
  }
  var defaultSlug = pkg.replace(/-/g,'_').replace(/\./g,'_');
  c.innerHTML = `
    <div class="page-head">
      <div class="page-title">⚡ <em>${pkg.toUpperCase()}</em></div>
      <div class="page-sub" id="feat-status">Loading features…</div>
    </div>
    <button class="btn-ghost" style="margin-bottom:20px" onclick="switchTab('marketplace')">← Marketplace</button>
    <div class="gen-layout">
      <div class="feat-panel">
        <h3>SELECT FEATURES</h3>
        <div style="display:flex;gap:8px;margin-bottom:12px">
          <button class="btn-ghost" style="flex:1" onclick="selectAll()">SELECT ALL</button>
          <button class="btn-ghost" style="flex:1" onclick="selectNone()">CLEAR</button>
        </div>
        <div class="feat-list" id="feat-list"><div class="loading">Introspecting ${pkg}…</div></div>
        <div class="slug-row">
          <label>SLUG</label>
          <input id="slug-input" type="text" value="${defaultSlug}"/>
        </div>
        <button class="btn" style="width:100%" onclick="doGenerate('${pkg}')">⚡ GENERATE MODULE</button>
      </div>
      <div class="out-panel" id="out-panel">
        <h3>OUTPUT</h3>
        <div style="color:var(--dim);font-size:11px;text-align:center;padding:40px 0">
          Configure features then click Generate
        </div>
      </div>
    </div>`;

  try {
    var d = await apiFetch('introspect', {package: pkg});
    _feats = d.features || [];
    var status = `${_feats.length} features found`;
    if (d.capped) status += ` (capped at ${_feats.length})`;
    document.getElementById('feat-status').textContent = status;
    renderFeatList(_feats);
  } catch(e) {
    document.getElementById('feat-status').textContent = 'Error: ' + e.message;
    document.getElementById('feat-list').innerHTML = `<div class="err-box">${e.message}</div>`;
  }
}

function renderFeatList(feats) {
  var el = document.getElementById('feat-list');
  if (!el) return;
  if (!feats.length) { el.innerHTML = '<div class="loading">No features found</div>'; return; }
  el.innerHTML = feats.map(f => {
    var typeBadge = `<span class="feat-type">[${f.type}]</span>`;
    return `<div class="feat-row" onclick="this.querySelector('input').click()">
      <input type="checkbox" name="feat" value="${f.name}" checked/>
      <label>${f.name} ${typeBadge}
        ${f.label ? `<br><span style="color:var(--dim);font-size:10px">${f.label.slice(0,70)}</span>` : ''}
      </label>
    </div>`;
  }).join('');
}

function selectAll()  { document.querySelectorAll('input[name=feat]').forEach(c => c.checked=true); }
function selectNone() { document.querySelectorAll('input[name=feat]').forEach(c => c.checked=false); }

async function doGenerate(pkg) {
  var checked = [...document.querySelectorAll('input[name=feat]:checked')].map(c => c.value);
  if (!checked.length) { alert('Select at least one feature'); return; }
  var slug = document.getElementById('slug-input').value.trim() || pkg.replace(/-/g,'_');
  var out  = document.getElementById('out-panel');
  out.innerHTML = '<h3>OUTPUT</h3><div class="loading">Generating…</div>';
  try {
    var d = await apiFetch('generate', {package: pkg, features: checked.join(','), slug});
    if (d.error) { out.innerHTML = `<h3>OUTPUT</h3><div class="err-box">${d.error}</div>`; return; }
    out.innerHTML = `
      <h3>OUTPUT</h3>
      <div class="ok-box">✅ ${d.slug} generated — ${d.file_count} files</div>
      <div style="margin:12px 0">
        ${(d.files_created||[]).map(f=>`<div style="font-size:11px;color:var(--green);padding:2px 0">✓ ${f}</div>`).join('')}
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <a class="btn" href="${window.PB}/download/${d.zip_name}" download="${d.zip_name}">⬇ DOWNLOAD ZIP</a>
        <button class="btn-ghost" onclick="quickInstall('${d.slug}')">⚡ INSTALL NOW</button>
        <button class="btn-ghost" onclick="switchTab('generated-list')">📁 View Generated</button>
      </div>
      <div class="info-box" style="margin-top:12px;font-size:11px">
        💡 Download the zip and upload it to your MasterChief addon manager,<br/>
        or click <strong>INSTALL NOW</strong> to copy it directly to addons/modules/.
      </div>`;
    refreshBadges();
  } catch(e) {
    out.innerHTML = `<h3>OUTPUT</h3><div class="err-box">Error: ${e.message}</div>`;
  }
}

async function quickInstall(slug) {
  var btn = event.target;
  btn.textContent = 'Installing…';
  btn.disabled = true;
  try {
    var d = await apiFetch('install', {slug});
    if (d.success) {
      btn.textContent = '✅ Installed';
      showToast(d.message, 'ok');
      refreshBadges();
    } else {
      btn.textContent = '❌ Failed';
      showToast(d.error, 'err');
    }
  } catch(e) {
    btn.textContent = '❌ Error';
    showToast(e.message, 'err');
  }
  setTimeout(() => { btn.disabled=false; }, 2000);
}

// ════════════════════════════════════════════════════════════════
//  INSTALLED
// ════════════════════════════════════════════════════════════════
var _installedMods = [];

async function loadInstalled() {
  var c = document.getElementById('content');
  c.innerHTML = `
    <div class="page-head">
      <div class="page-title">🗂 <em>INSTALLED</em> MODULES</div>
      <div class="page-sub">All addon modules in addons/modules/</div>
    </div>
    <div class="search-row">
      <input id="mod-search" type="text" placeholder="Search modules…" oninput="filterMods(this.value)"/>
      <button class="btn-ghost" onclick="loadInstalled()">↺ Refresh</button>
    </div>
    <div class="stat-row" id="mod-stats"></div>
    <div class="mod-grid" id="mod-grid"><div class="loading">Loading…</div></div>
    <div id="file-viewer" style="margin-top:24px;display:none">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
        <div style="font-family:var(--ui);font-size:11px;font-weight:700" id="fv-title">FILES</div>
        <button class="btn-ghost" style="margin-left:auto;padding:3px 10px;font-size:9px" onclick="closeFileViewer()">✕ Close</button>
      </div>
      <div class="file-tree" id="fv-tree"></div>
      <pre id="fv-code"></pre>
    </div>`;

  try {
    var d = await apiFetch('installed');
    _installedMods = d.modules || [];
    document.getElementById('installed-badge').textContent = _installedMods.length;
    document.getElementById('mod-stats').innerHTML = `
      <div class="stat"><div class="stat-label">MODULES</div><div class="stat-val">${_installedMods.length}</div></div>
      <div class="stat" style="border-left-color:var(--green)"><div class="stat-label">GENERATED</div>
        <div class="stat-val" style="color:var(--green)">${_installedMods.filter(m=>m.is_generated).length}</div></div>`;
    renderModGrid(_installedMods);
  } catch(e) {
    document.getElementById('mod-grid').innerHTML = `<div class="err-box">Error: ${e.message}</div>`;
  }
}

function renderModGrid(mods) {
  var el = document.getElementById('mod-grid');
  if (!el) return;
  if (!mods.length) { el.innerHTML = '<div class="loading">No modules found</div>'; return; }
  el.innerHTML = mods.map(m => {
    var badge = m.is_generated
      ? `<span class="tag tag-green">generated</span>`
      : `<span class="tag tag-blue">manual</span>`;
    var hasZip = m.has_zip ? `<span class="tag tag-amber">zip ready</span>` : '';
    return `<div class="mod-card" style="border-left-color:${m.color||'#f5a623'}">
      <div class="mod-card-head">
        <div class="mod-icon">${m.icon||'📦'}</div>
        <div>
          <div class="mod-title">${m.label||m.slug}</div>
          <div class="mod-slug">${m.slug}</div>
        </div>
      </div>
      <div class="mod-meta">${badge} ${hasZip}</div>
      <div class="mod-meta">${m.file_count} files · ${m.size_kb}KB ${m.package ? '· '+m.package : ''}</div>
      <div class="mod-actions">
        <button class="btn btn-sm" onclick="viewFiles('${m.slug}')">📄 Files</button>
        ${m.has_app ? `<button class="btn-ghost" style="padding:4px 10px;font-size:9px"
          onclick="window.open(window.PB.replace(/\\/addons\\/modules\\/[^/]+\\/app/,'/addons/modules/${m.slug}/app'),'_blank')">🔗 Open</button>` : ''}
        ${m.has_zip ? `<button class="btn-ghost" style="padding:4px 10px;font-size:9px"
          onclick="downloadZip('${m.slug}')">⬇ ZIP</button>` : ''}
        <button class="btn-danger" style="padding:4px 10px;font-size:9px" onclick="removeModule('${m.slug}')">🗑 Remove</button>
      </div>
    </div>`;
  }).join('');
}

function filterMods(q) {
  q = q.toLowerCase();
  renderModGrid(q ? _installedMods.filter(m => m.slug.toLowerCase().includes(q) || (m.label||'').toLowerCase().includes(q)) : _installedMods);
}

async function viewFiles(slug) {
  var fv = document.getElementById('file-viewer');
  fv.style.display = 'block';
  document.getElementById('fv-title').textContent = `📄 ${slug}`;
  document.getElementById('fv-tree').innerHTML = '<div class="loading">Loading…</div>';
  document.getElementById('fv-code').textContent = '';
  try {
    var d = await apiFetch('module-files', {slug});
    var tree = document.getElementById('fv-tree');
    tree.innerHTML = d.files.map((f,i) =>
      `<div class="file-item" onclick="showFile(${i},'${slug}')">${f.path}</div>`
    ).join('');
    _currentFiles = d.files;
    if (d.files.length) showFileContent(d.files[0]);
  } catch(e) {
    document.getElementById('fv-tree').innerHTML = `<div class="err-box">${e.message}</div>`;
  }
}
var _currentFiles = [];
function showFile(i, slug) {
  document.querySelectorAll('.file-item').forEach((el,j) => el.classList.toggle('active', i===j));
  showFileContent(_currentFiles[i]);
}
function showFileContent(f) {
  document.getElementById('fv-code').textContent = f.content;
}
function closeFileViewer() {
  document.getElementById('file-viewer').style.display = 'none';
}
function downloadZip(slug) {
  window.location.href = window.PB + '/download/' + slug + '.zip';
}

async function removeModule(slug) {
  if (!confirm(`Remove module "${slug}"? This deletes the folder from addons/modules/.`)) return;
  try {
    var d = await apiFetch('remove', {slug});
    if (d.success) { showToast(d.message, 'ok'); loadInstalled(); }
    else showToast(d.error, 'err');
  } catch(e) { showToast(e.message, 'err'); }
}

// ════════════════════════════════════════════════════════════════
//  GENERATED LIST
// ════════════════════════════════════════════════════════════════
var _genList = [];

async function loadGeneratedList() {
  var c = document.getElementById('content');
  c.innerHTML = `
    <div class="page-head">
      <div class="page-title">📁 <em>GENERATED</em> MODULES</div>
      <div class="page-sub">Zips created by this module system — ready to install or download</div>
    </div>
    <div class="gen-list" id="gen-list"><div class="loading">Loading…</div></div>`;

  try {
    var d = await apiFetch('generated');
    _genList = d || [];
    document.getElementById('gen-badge').textContent = _genList.length;
    var el = document.getElementById('gen-list');
    if (!_genList.length) {
      el.innerHTML = `<div class="info-box">No generated modules yet — go to Marketplace to create one.</div>`;
      return;
    }
    el.innerHTML = `
      <div style="display:flex;gap:8px;align-items:center;padding:8px 0;border-bottom:1px solid var(--border);
        font-size:9px;color:var(--dim);letter-spacing:.15em">
        <span style="flex:1">MODULE</span><span style="width:70px">SIZE</span>
        <span style="width:100px">GENERATED</span><span style="width:200px">ACTIONS</span>
      </div>
      ${_genList.map(z => `
      <div class="gen-row">
        <div class="gen-row-name">📦 ${z.slug}</div>
        <div class="gen-row-size">${(z.size/1024).toFixed(1)} KB</div>
        <div class="gen-row-size">${timeAgo(z.mtime)}</div>
        <div style="display:flex;gap:6px">
          <button class="btn btn-sm" onclick="installGen('${z.slug}',this)">⚡ INSTALL</button>
          <a class="btn-ghost" style="padding:4px 10px;font-size:9px"
             href="${window.PB}/download/${z.zip_name}" download="${z.zip_name}">⬇ ZIP</a>
          <button class="btn-danger" style="padding:4px 10px;font-size:9px"
                  onclick="deleteGen('${z.slug}',this)">🗑</button>
        </div>
      </div>`).join('')}`;
  } catch(e) {
    document.getElementById('gen-list').innerHTML = `<div class="err-box">${e.message}</div>`;
  }
}

async function installGen(slug, btn) {
  btn.textContent = '…';
  btn.disabled = true;
  try {
    var d = await apiFetch('install', {slug});
    if (d.success) { showToast(d.message, 'ok'); refreshBadges(); btn.textContent = '✅'; }
    else { showToast(d.error, 'err'); btn.textContent = '❌'; }
  } catch(e) { showToast(e.message,'err'); btn.textContent = '❌'; }
  setTimeout(() => { btn.disabled=false; btn.textContent='⚡ INSTALL'; }, 3000);
}

async function deleteGen(slug, btn) {
  if (!confirm(`Delete generated zip for "${slug}"?`)) return;
  try {
    var d = await apiFetch('delete-generated', {slug});
    if (d.success) { showToast('Deleted', 'ok'); loadGeneratedList(); }
    else showToast(d.error, 'err');
  } catch(e) { showToast(e.message,'err'); }
}

// ════════════════════════════════════════════════════════════════
//  PIP MANAGER
// ════════════════════════════════════════════════════════════════
async function loadPip() {
  var c = document.getElementById('content');
  c.innerHTML = `
    <div class="page-head">
      <div class="page-title">🐍 <em>PIP</em> MANAGER</div>
      <div class="page-sub">Install new packages to make them available in the Marketplace</div>
    </div>
    <div style="max-width:600px">
      <div style="font-size:10px;color:var(--dim);letter-spacing:.1em;margin-bottom:8px">INSTALL PACKAGE</div>
      <div style="display:flex;gap:8px;margin-bottom:8px">
        <input id="pip-input" type="text" placeholder="e.g. kubernetes, docker, boto3, psutil"
               style="flex:1" onkeydown="if(event.key==='Enter')doPipInstall()"/>
        <button class="btn" onclick="doPipInstall()">INSTALL</button>
      </div>
      <div class="info-box" style="font-size:11px">
        After installing, the package will appear in the Marketplace and you can generate a module from it.
      </div>
      <div id="pip-output" style="margin-top:16px"></div>
    </div>
    <div style="margin-top:32px">
      <div style="font-size:10px;color:var(--dim);letter-spacing:.1em;margin-bottom:8px">QUICK INSTALL</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        ${['kubernetes','docker','boto3','psutil','redis','paramiko','celery','requests','pandas','sqlalchemy']
          .map(p => `<button class="btn-ghost" onclick="pipInstallQuick('${p}')">${p}</button>`).join('')}
      </div>
    </div>`;
}

async function doPipInstall() {
  var pkg = document.getElementById('pip-input').value.trim();
  if (!pkg) return;
  runPipInstall(pkg);
}

function pipInstallQuick(pkg) {
  document.getElementById('pip-input').value = pkg;
  runPipInstall(pkg);
}

async function runPipInstall(pkg) {
  var out = document.getElementById('pip-output');
  out.innerHTML = `<div class="info-box">Installing ${pkg}…</div>`;
  try {
    var d = await apiFetch('pip-install', {package: pkg});
    if (d.success) {
      out.innerHTML = `
        <div class="ok-box">✅ ${pkg} installed successfully</div>
        <div class="log-terminal">${(d.output||'').split('\n').map(l=>`<div class="log-line">${l}</div>`).join('')}</div>
        <div style="margin-top:12px;display:flex;gap:8px">
          <button class="btn" onclick="openGenerate('${pkg}');switchTab('generate')">⚡ Generate Module Now</button>
          <button class="btn-ghost" onclick="switchTab('marketplace')">View in Marketplace</button>
        </div>`;
      refreshBadges();
    } else {
      out.innerHTML = `
        <div class="err-box">❌ Install failed</div>
        <div class="log-terminal">${(d.output||d.error||'').split('\n').map(l=>`<div class="log-line log-err">${l}</div>`).join('')}</div>`;
    }
  } catch(e) {
    out.innerHTML = `<div class="err-box">Error: ${e.message}</div>`;
  }
}

// ════════════════════════════════════════════════════════════════
//  LOGS
// ════════════════════════════════════════════════════════════════
async function loadLogs() {
  var c = document.getElementById('content');
  c.innerHTML = `
    <div class="page-head">
      <div class="page-title">📋 <em>ADDON</em> LOGS</div>
      <div class="page-sub">View log output from installed addon modules</div>
    </div>
    <div style="display:flex;gap:8px;margin-bottom:16px">
      <input id="log-slug" type="text" placeholder="module slug (leave blank for main log)"/>
      <input id="log-lines" type="number" value="100" style="width:80px" placeholder="lines"/>
      <button class="btn" onclick="fetchLogs()">VIEW LOGS</button>
    </div>
    <div id="log-out"></div>`;
}

async function fetchLogs() {
  var slug  = document.getElementById('log-slug').value.trim();
  var lines = document.getElementById('log-lines').value || 100;
  var out   = document.getElementById('log-out');
  out.innerHTML = '<div class="loading">Loading logs…</div>';
  try {
    var d = await apiFetch('addon-logs', {slug, lines});
    var src = d.source ? `<div style="font-size:10px;color:var(--dim);margin-bottom:8px">Source: ${d.source}</div>` : '';
    var logHtml = (d.lines||[]).map(l => {
      var cls = l.toLowerCase().includes('error') || l.toLowerCase().includes('exception') ? 'log-err'
              : l.toLowerCase().includes('warn') ? 'log-warn'
              : l.toLowerCase().includes('start') || l.toLowerCase().includes('success') ? 'log-ok'
              : '';
      return `<div class="log-line ${cls}">${escHtml(l)}</div>`;
    }).join('');
    out.innerHTML = src + (logHtml
      ? `<div class="log-terminal">${logHtml}</div>`
      : `<div class="info-box">${d.note || 'No log lines found'}</div>`);
  } catch(e) {
    out.innerHTML = `<div class="err-box">Error: ${e.message}</div>`;
  }
}

// ════════════════════════════════════════════════════════════════
//  Utilities
// ════════════════════════════════════════════════════════════════
function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
function timeAgo(ts) {
  var s = Math.floor(Date.now()/1000) - ts;
  if (s < 60) return s+'s ago';
  if (s < 3600) return Math.floor(s/60)+'m ago';
  if (s < 86400) return Math.floor(s/3600)+'h ago';
  return Math.floor(s/86400)+'d ago';
}

var _toast = null;
function showToast(msg, type) {
  if (_toast) clearTimeout(_toast);
  var t = document.getElementById('toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'toast';
    t.style = 'position:fixed;bottom:24px;right:24px;padding:12px 20px;border-radius:3px;font-size:12px;z-index:999;max-width:400px';
    document.body.appendChild(t);
  }
  t.style.background = type==='ok' ? 'rgba(0,255,136,.15)' : 'rgba(255,68,68,.15)';
  t.style.border     = `1px solid ${type==='ok' ? 'var(--green)' : 'var(--red)'}`;
  t.style.color      = type==='ok' ? 'var(--green)' : 'var(--red)';
  t.textContent = msg;
  t.style.display = 'block';
  _toast = setTimeout(() => { t.style.display='none'; }, 4000);
}

async function refreshBadges() {
  try {
    var [inst, gen] = await Promise.all([apiFetch('installed'), apiFetch('generated')]);
    var ib = document.getElementById('installed-badge');
    var gb = document.getElementById('gen-badge');
    if (ib) ib.textContent = (inst.modules||[]).length;
    if (gb) gb.textContent = (gen||[]).length;
  } catch(e) {}
}

// ════════════════════════════════════════════════════════════════
//  REGISTRY
// ════════════════════════════════════════════════════════════════
var _registry = null;
const CAT_COLORS = {
  admin_ops:'#f5a623', addons:'#58a6ff', sys_modules:'#a78bfa',
  integrations:'#00ff88', devtools:'#38bdf8', data:'#fb7185',
  security:'#ff4444', cloud:'#34d399', uncategorized:'#4a6070'
};

async function loadRegistry() {
  var c = document.getElementById('content');
  c.innerHTML = `
    <div class="page-head">
      <div class="page-title">🗺 <em>MODULE</em> REGISTRY</div>
      <div class="page-sub">All installed addons — categories, capabilities, dependency status</div>
    </div>
    <div style="display:flex;gap:8px;margin-bottom:20px">
      <button class="btn" onclick="doDiscover()">↺ Re-discover All</button>
      <button class="btn-ghost" onclick="copyNavSnippet()">📋 Copy main.py Hook</button>
      <button class="btn-ghost" onclick="switchTab('platform')">⚡ Platform View</button>
    </div>
    <div id="reg-stats" class="stat-row"></div>
    <div id="reg-cats"></div>`;

  try {
    var d = await apiFetch('registry');
    _registry = d;
    var mods = d.modules || {};
    var count = Object.keys(mods).length;
    var genCount = Object.values(mods).filter(m=>m.is_generated).length;
    var okCount  = Object.values(mods).filter(m=>m.deps_ok!==false).length;

    document.getElementById('reg-stats').innerHTML = `
      <div class="stat"><div class="stat-label">TOTAL</div><div class="stat-val">${count}</div></div>
      <div class="stat" style="border-left-color:var(--green)">
        <div class="stat-label">GENERATED</div><div class="stat-val" style="color:var(--green)">${genCount}</div></div>
      <div class="stat" style="border-left-color:var(--blue)">
        <div class="stat-label">DEPS OK</div><div class="stat-val" style="color:var(--blue)">${okCount}/${count}</div></div>
      <div class="stat" style="border-left-color:var(--dim)">
        <div class="stat-label">REGISTRY</div><div class="stat-val" style="font-size:10px;color:var(--dim)">registry.json</div></div>`;

    // Group by category
    var cats = {};
    for (var [slug, m] of Object.entries(mods)) {
      var cat = m.category || 'uncategorized';
      if (!cats[cat]) cats[cat] = {label: m.nav_section||cat, items: [], color: CAT_COLORS[cat]||'#4a6070'};
      cats[cat].items.push({slug, ...m});
    }

    var html = Object.entries(cats).map(([catId, cat]) => `
      <div style="margin-bottom:24px">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;
          padding-bottom:8px;border-bottom:1px solid var(--border)">
          <div style="font-family:var(--ui);font-size:11px;font-weight:700;
            color:${cat.color}">${cat.label.toUpperCase()}</div>
          <span class="tag" style="background:rgba(255,255,255,.05);color:var(--dim);
            border-color:var(--border)">${cat.items.length} module${cat.items.length!==1?'s':''}</span>
          <button class="btn-ghost" style="padding:2px 8px;font-size:9px;margin-left:auto"
            onclick="editCategory('${catId}')">✏ Edit Category</button>
        </div>
        <div class="mod-grid">
          ${cat.items.map(m => renderRegCard(m, cat.color)).join('')}
        </div>
      </div>`).join('');

    document.getElementById('reg-cats').innerHTML = html || '<div class="loading">No modules found</div>';
  } catch(e) {
    document.getElementById('reg-cats').innerHTML = `<div class="err-box">${e.message}</div>`;
  }
}

function renderRegCard(m, catColor) {
  var srcBadge = m._source === 'manifest'
    ? '<span class="tag tag-green">manifest</span>'
    : m._source === 'plugin_meta'
    ? '<span class="tag tag-blue">plugin_meta</span>'
    : '<span class="tag" style="background:rgba(255,255,255,.04);color:var(--dim);border-color:var(--border)">filesystem</span>';
  var depBadge = m.broken_deps && m.broken_deps.length
    ? `<span class="tag tag-red" title="Missing: ${m.broken_deps.join(', ')}">⚠ deps</span>`
    : '';
  var caps = (m.capabilities||[]).map(c =>
    `<span class="tag tag-amber" style="margin-bottom:3px">${c}</span>`).join(' ');
  var reqs = (m.requires||[]).map(r =>
    `<span class="tag" style="background:rgba(88,166,255,.08);color:var(--blue);
      border-color:rgba(88,166,255,.2);margin-bottom:3px">${r}</span>`).join(' ');

  return `<div class="mod-card" style="border-left-color:${m.color||catColor}">
    <div class="mod-card-head">
      <div class="mod-icon">${m.icon||'📦'}</div>
      <div style="flex:1">
        <div class="mod-title">${m.label||m.slug}</div>
        <div class="mod-slug">${m.slug} ${m.version?'v'+m.version:''}</div>
      </div>
    </div>
    <div style="margin-bottom:8px">${srcBadge} ${depBadge}</div>
    ${m.description ? `<div class="mod-meta" style="margin-bottom:8px;line-height:1.5">${m.description.slice(0,100)}</div>` : ''}
    ${caps ? `<div style="margin-bottom:6px"><div style="font-size:9px;color:var(--dim);letter-spacing:.1em;margin-bottom:4px">PROVIDES</div>${caps}</div>` : ''}
    ${reqs ? `<div style="margin-bottom:8px"><div style="font-size:9px;color:var(--dim);letter-spacing:.1em;margin-bottom:4px">REQUIRES</div>${reqs}</div>` : ''}
    <div class="mod-actions">
      <button class="btn btn-sm" onclick="editManifest('${m.slug}')">✏ Edit</button>
      ${m.has_app ? `<button class="btn-ghost" style="padding:4px 10px;font-size:9px"
        onclick="window.open('/addons/modules/${m.slug}/app','_blank')">🔗 Open</button>` : ''}
    </div>
  </div>`;
}

async function doDiscover() {
  showToast('Discovering…', 'ok');
  try {
    var d = await apiFetch('write-registry');
    showToast(`Registry updated — ${d.count} modules`, 'ok');
    loadRegistry();
  } catch(e) { showToast(e.message, 'err'); }
}

function copyNavSnippet() {
  var snippet = `# Add to main.py after app = Flask(__name__)
import json as _json
from pathlib import Path as _Path

_REGISTRY_PATH = _Path(__file__).parent / 'addons' / 'registry.json'

@app.route('/api/registry')
def api_module_registry():
    try:
        if _REGISTRY_PATH.exists():
            return jsonify(_json.loads(_REGISTRY_PATH.read_text()))
    except Exception as e:
        return jsonify({'error': str(e)})
    return jsonify({'modules': {}})

@app.route('/api/nav-sections')
def api_nav_sections():
    try:
        if _REGISTRY_PATH.exists():
            data = _json.loads(_REGISTRY_PATH.read_text())
            return jsonify({'sections': data.get('_nav_sections', [])})
    except Exception as e:
        return jsonify({'error': str(e)})
    return jsonify({'sections': []})`;
  navigator.clipboard.writeText(snippet).then(
    () => showToast('Copied to clipboard', 'ok'),
    () => showToast('Copy failed — check console', 'err')
  );
}

var _editSlug = null;
function editManifest(slug) {
  _editSlug = slug;
  var m = _registry && _registry.modules ? _registry.modules[slug] : {};
  var cats = Object.entries({
    admin_ops:'Admin Ops', addons:'Add Ons', sys_modules:'Systems Modules',
    integrations:'Integrations', devtools:'Dev Tools', data:'Data & Analytics',
    security:'Security', cloud:'Cloud & Infra', uncategorized:'Other'
  }).map(([v,l]) => `<option value="${v}" ${m.category===v?'selected':''}>${l}</option>`).join('');

  showModal(`
    <div style="font-family:var(--ui);font-size:12px;font-weight:700;margin-bottom:16px">
      EDIT MANIFEST — ${slug}
    </div>
    <div style="display:grid;gap:10px">
      <div><div style="font-size:9px;color:var(--dim);letter-spacing:.1em;margin-bottom:4px">LABEL</div>
        <input id="ef-label" value="${m.label||slug}" style="width:100%"/></div>
      <div><div style="font-size:9px;color:var(--dim);letter-spacing:.1em;margin-bottom:4px">ICON</div>
        <input id="ef-icon" value="${m.icon||'📦'}" style="width:80px"/></div>
      <div><div style="font-size:9px;color:var(--dim);letter-spacing:.1em;margin-bottom:4px">CATEGORY</div>
        <select id="ef-cat" style="width:100%">${cats}</select></div>
      <div><div style="font-size:9px;color:var(--dim);letter-spacing:.1em;margin-bottom:4px">DESCRIPTION</div>
        <input id="ef-desc" value="${(m.description||'').replace(/"/g,'&quot;')}" style="width:100%"/></div>
      <div><div style="font-size:9px;color:var(--dim);letter-spacing:.1em;margin-bottom:4px">CAPABILITIES (comma-separated)</div>
        <input id="ef-caps" value="${(m.capabilities||[]).join(', ')}" style="width:100%"/></div>
      <div><div style="font-size:9px;color:var(--dim);letter-spacing:.1em;margin-bottom:4px">REQUIRES (comma-separated)</div>
        <input id="ef-reqs" value="${(m.requires||[]).join(', ')}" style="width:100%"/></div>
      <div style="display:flex;gap:8px;margin-top:8px">
        <button class="btn" style="flex:1" onclick="saveManifest()">SAVE MANIFEST</button>
        <button class="btn-ghost" onclick="closeModal()">Cancel</button>
      </div>
    </div>`);
}

async function saveManifest() {
  var params = {
    slug:         _editSlug,
    label:        document.getElementById('ef-label').value,
    icon:         document.getElementById('ef-icon').value,
    category:     document.getElementById('ef-cat').value,
    description:  document.getElementById('ef-desc').value,
    capabilities: document.getElementById('ef-caps').value,
    requires:     document.getElementById('ef-reqs').value,
  };
  try {
    var d = await apiFetch('update-manifest', params);
    if (d.success) {
      showToast('Manifest saved — re-discovering…', 'ok');
      closeModal();
      setTimeout(() => { doDiscover(); }, 500);
    } else { showToast(d.error, 'err'); }
  } catch(e) { showToast(e.message, 'err'); }
}

function editCategory(catId) {
  // Bulk re-categorize all modules in a category
  showToast('Select a module and use Edit Manifest to change its category', 'ok');
}

// ════════════════════════════════════════════════════════════════
//  PLATFORM
// ════════════════════════════════════════════════════════════════
async function loadPlatform() {
  var c = document.getElementById('content');
  c.innerHTML = `
    <div class="page-head">
      <div class="page-title">⚡ <em>PLATFORM</em></div>
      <div class="page-sub">Capability bus, module links, and MasterChief integration</div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:8px">
      <div>
        <div style="font-family:var(--ui);font-size:11px;font-weight:700;margin-bottom:12px;color:var(--amber)">
          CAPABILITY BUS
        </div>
        <div id="cap-bus"><div class="loading">Loading…</div></div>
      </div>
      <div>
        <div style="font-family:var(--ui);font-size:11px;font-weight:700;margin-bottom:12px;color:var(--blue)">
          MAIN.PY INTEGRATION
        </div>
        <div id="integration-panel"></div>
      </div>
    </div>
    <div style="margin-top:24px">
      <div style="font-family:var(--ui);font-size:11px;font-weight:700;margin-bottom:12px;color:var(--green)">
        PLATFORM API ENDPOINTS
      </div>
      <div id="api-panel"></div>
    </div>`;

  try {
    var [caps, nav] = await Promise.all([apiFetch('capabilities'), apiFetch('nav-sections')]);

    // Capability bus
    var capHtml = Object.entries(caps).length
      ? Object.entries(caps).sort().map(([cap, providers]) => `
          <div style="display:flex;align-items:center;gap:8px;padding:8px 0;
            border-bottom:1px solid rgba(26,37,53,.5)">
            <div style="flex:1;font-size:11px;color:var(--amber)">${cap}</div>
            <div style="font-size:10px;color:var(--dim)">→</div>
            <div>${providers.map(p=>`<span class="tag tag-blue">${p}</span>`).join(' ')}</div>
          </div>`).join('')
      : '<div class="info-box">No capabilities declared yet. Edit module manifests to add them.</div>';
    document.getElementById('cap-bus').innerHTML = capHtml;

    // Integration panel
    var sections = nav.sections || [];
    var totalMods = sections.reduce((sum,s) => sum + s.items.length, 0);
    document.getElementById('integration-panel').innerHTML = `
      <div class="ok-box" style="margin-bottom:12px">
        ${sections.length} nav sections · ${totalMods} modules ready to inject
      </div>
      <div style="font-size:11px;color:var(--mid);margin-bottom:12px;line-height:1.7">
        Add this one block to <code style="color:var(--amber)">main.py</code> to auto-register all modules into the MasterChief nav:
      </div>
      <div style="background:#000;border:1px solid var(--border);border-radius:3px;padding:12px;
        font-size:10px;color:#aaa;font-family:var(--mono);line-height:1.8;margin-bottom:10px">
        <span style="color:var(--dim)"># Paste after app = Flask(__name__)</span><br/>
        <span style="color:#58a6ff">import</span> json <span style="color:#58a6ff">as</span> _json<br/>
        <span style="color:#58a6ff">from</span> pathlib <span style="color:#58a6ff">import</span> Path <span style="color:#58a6ff">as</span> _Path<br/>
        <span style="color:var(--dim)"># ... (see mc_register.py for full snippet)</span>
      </div>
      <div style="display:flex;gap:8px">
        <button class="btn" onclick="copyNavSnippet()">📋 Copy Full Snippet</button>
        <button class="btn-ghost" onclick="doDiscover()">↺ Refresh Registry</button>
      </div>
      <div style="margin-top:16px">
        <div style="font-size:10px;color:var(--dim);letter-spacing:.1em;margin-bottom:8px">NAV PREVIEW</div>
        ${sections.map(s => `
          <div style="margin-bottom:8px;padding:8px;background:var(--card);border:1px solid var(--border);border-radius:2px">
            <div style="font-size:10px;font-weight:700;color:var(--amber);margin-bottom:4px">
              ${s.icon} ${s.label}
            </div>
            ${s.items.map(i=>`<div style="font-size:11px;color:var(--mid);padding:2px 0 2px 12px">
              ${i.icon} ${i.label}
            </div>`).join('')}
          </div>`).join('')}
      </div>`;

    // API endpoints panel
    document.getElementById('api-panel').innerHTML = `
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:8px">
        ${[
          ['/api/registry',         'Full module registry JSON — consumed by main.py'],
          ['/api/nav-sections',     'Grouped nav for sidebar injection'],
          ['/api/capabilities',     'Capability bus — who provides what'],
          ['/api/discover',         'Re-scan addons folder, refresh registry'],
          ['/api/write-registry',   'Force-write registry.json'],
          ['/api/update-manifest',  'Edit a module manifest (slug, label, caps, category)'],
          ['/api/installed',        'All installed module metadata'],
          ['/api/packages',         'All pip packages'],
          ['/api/introspect',       'Introspect a package API surface'],
          ['/api/generate',         'Generate an addon zip'],
          ['/api/install',          'Install a generated zip'],
          ['/api/remove',           'Remove an installed module'],
          ['/api/pip-install',      'Install a pip package'],
          ['/api/addon-logs',       'Read addon log output'],
        ].map(([ep, desc]) => `
          <div style="background:var(--card);border:1px solid var(--border);border-radius:2px;
            padding:10px 12px;border-left:3px solid var(--green)">
            <div style="font-size:11px;color:var(--green);margin-bottom:3px;font-weight:700">${ep}</div>
            <div style="font-size:10px;color:var(--dim)">${desc}</div>
          </div>`).join('')}
      </div>`;

  } catch(e) {
    c.innerHTML += `<div class="err-box">${e.message}</div>`;
  }
}

// ════════════════════════════════════════════════════════════════
//  Modal
// ════════════════════════════════════════════════════════════════
function showModal(html) {
  var overlay = document.createElement('div');
  overlay.id = 'modal-overlay';
  overlay.style = 'position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:999;display:flex;align-items:center;justify-content:center';
  overlay.innerHTML = `<div style="background:var(--panel);border:1px solid var(--border);border-radius:4px;
    padding:24px;max-width:520px;width:90%;max-height:80vh;overflow-y:auto">${html}</div>`;
  overlay.addEventListener('click', e => { if (e.target===overlay) closeModal(); });
  document.body.appendChild(overlay);
}
function closeModal() {
  var el = document.getElementById('modal-overlay');
  if (el) el.remove();
}

// ── Boot ─────────────────────────────────────────────────────────
window.addEventListener('load', function() {
  renderTab('marketplace');
  refreshBadges();
});
</script>
</body></html>"""


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9100))
    print(f'[Module Center] Starting on http://localhost:{port}', flush=True)
    app.run(host='0.0.0.0', port=port, debug=False)
