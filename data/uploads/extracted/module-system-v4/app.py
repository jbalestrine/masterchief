"""
Module Command Center v4 — MasterChief Addon
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Panels:
  DASHBOARD    Live health overview, system stats, activity feed, quick actions
  MARKETPLACE  Browse pip packages with real PyPI metadata — click to generate
  GENERATE     Pick features, preview generated code, download or install
  MODULES      Merged installed+registry — live status badges, batch ops, notes
  GENERATED    Manage generated zips — install, download, delete
  PIP          Install packages with live streaming output + PyPI search
  LOGS         Live log viewer with filtering, search, auto-refresh
  NETWORK      D3 force-directed capability graph
  PLATFORM     Nav sections, capability bus, integration snippets, export

New in v4:
  ✦ Live dashboard with real-time module health
  ✦ Command palette (Ctrl+K) — fuzzy-search every action
  ✦ Keyboard shortcuts with help overlay (?)
  ✦ D3.js capability / dependency graph
  ✦ Real PyPI metadata (description, author, downloads)
  ✦ Code preview in generator — see files before downloading
  ✦ Syntax highlighting via highlight.js
  ✦ Module notes — sticky annotations on any module
  ✦ Batch operations — multi-select, bulk actions
  ✦ Auto-refresh toggle on dashboard
  ✦ Toast notification stack (up to 5 simultaneous)
  ✦ Export full registry as JSON
  ✦ Live status polling via MC /addons/modules/<slug>/status
  ✦ Animated live status indicators
"""
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import threading
import zipfile
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, request, Response

BASE_DIR   = Path(__file__).parent
ADDON_NAME = os.environ.get('MC_ADDON_NAME', BASE_DIR.name)
MC_ROOT    = Path(os.environ.get('MC_ROOT', BASE_DIR.parent.parent.parent.parent))

UPLOAD_FOLDER = MC_ROOT / 'uploads'
EXTRACTED_DIR = UPLOAD_FOLDER / 'extracted'
ADDONS_DIR    = MC_ROOT / 'addons' / 'modules'
OUTPUT_DIR    = BASE_DIR / 'generated'
REGISTRY_PATH = BASE_DIR / 'registry.json'
NOTES_PATH    = BASE_DIR / 'notes.json'
OUTPUT_DIR.mkdir(exist_ok=True)

MC_BASE = os.environ.get('MC_BASE_URL', 'http://127.0.0.1:8080')

sys.path.insert(0, str(BASE_DIR))
from introspector import introspect_package
from generator   import generate_module
from registry    import Registry, CATEGORIES

registry = Registry(EXTRACTED_DIR, REGISTRY_PATH, masterchief_base=MC_BASE)

app = Flask(__name__)

@app.errorhandler(404)
def e404(e): return jsonify({'error': 'Not found'}), 404
@app.errorhandler(500)
def e500(e): return jsonify({'error': str(e)}), 500
@app.errorhandler(Exception)
def eany(e): return jsonify({'error': str(e)}), 500


# ════════════════════════════════════════════════════════════
#  EXISTING API (v3 compatible)
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
            dest = EXTRACTED_DIR / extracted
            EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                shutil.rmtree(dest)
            zf.extractall(str(EXTRACTED_DIR))
        return jsonify({
            'success': True,
            'slug':    extracted,
            'path':    str(dest),
            'message': f'Installed to uploads/extracted/{extracted}/ — reload addon manager to activate',
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/installed')
def api_installed():
    modules = []
    scan_dirs = []
    if EXTRACTED_DIR.exists(): scan_dirs.append(('extracted', EXTRACTED_DIR))
    if ADDONS_DIR.exists():    scan_dirs.append(('addons',    ADDONS_DIR))
    seen = set()
    for src, base in scan_dirs:
        for d in sorted(base.iterdir()):
            if not d.is_dir() or d.name.startswith('.') or d.name.startswith('_') or d.name in seen:
                continue
            seen.add(d.name)
            has_app    = (d / 'app.py').exists()
            has_plugin = (d / 'plugin.py').exists()
            has_addon  = (d / 'addon.py').exists()
            has_req    = (d / 'requirements.txt').exists()
            meta = {}
            for meta_file in ['plugin.py', 'addon.py']:
                mf = d / meta_file
                if mf.exists():
                    try:
                        src_txt = mf.read_text(encoding='utf-8')
                        tree = ast.parse(src_txt)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Assign):
                                for t in node.targets:
                                    if isinstance(t, ast.Name) and t.id == 'PLUGIN_META':
                                        try: meta = ast.literal_eval(node.value)
                                        except Exception: pass
                    except Exception:
                        pass
                    if meta: break
            modules.append({
                'slug':         d.name,
                'source':       src,
                'has_app':      has_app,
                'has_plugin':   has_plugin,
                'has_addon':    has_addon,
                'is_blueprint': has_addon,
                'is_generated': has_plugin and has_app,
                'label':        meta.get('label', d.name),
                'icon':         meta.get('icon', '📦'),
                'color':        meta.get('color', '#f5a623'),
                'package':      meta.get('package', ''),
                'version':      meta.get('version', ''),
                'description':  meta.get('description', ''),
                'size_kb':      round(sum(f.stat().st_size for f in d.rglob('*') if f.is_file()) / 1024, 1),
                'file_count':   len(list(d.rglob('*'))),
                'has_zip':      (OUTPUT_DIR / f'{d.name}.zip').exists(),
                'mtime':        int(d.stat().st_mtime),
            })
    return jsonify({'modules': modules, 'count': len(modules)})


@app.route('/api/remove')
def api_remove():
    slug = request.args.get('slug', '').strip()
    if not slug or '/' in slug or '..' in slug:
        return jsonify({'error': 'invalid slug'}), 400
    removed = False
    for base in [EXTRACTED_DIR, ADDONS_DIR]:
        target = base / slug
        if target.exists():
            shutil.rmtree(target)
            removed = True
    if removed:
        return jsonify({'success': True, 'message': f'{slug} removed'})
    return jsonify({'error': f'{slug} not found'}), 404


@app.route('/api/module-files')
def api_module_files():
    slug = request.args.get('slug', '').strip()
    if not slug or '/' in slug or '..' in slug:
        return jsonify({'error': 'invalid slug'}), 400
    d = None
    for base in [EXTRACTED_DIR, ADDONS_DIR]:
        candidate = base / slug
        if candidate.exists():
            d = candidate
            break
    if not d:
        return jsonify({'error': 'not found'}), 404
    files = []
    for f in sorted(d.rglob('*')):
        if f.is_file() and not any(p in str(f) for p in ['__pycache__', '.pyc']):
            try:    content = f.read_text(encoding='utf-8')
            except: content = '<binary>'
            files.append({
                'name':    f.name,
                'path':    str(f.relative_to(d)),
                'size':    f.stat().st_size,
                'ext':     f.suffix.lstrip('.'),
                'content': content[:12000],
            })
    return jsonify({'slug': slug, 'files': files})


@app.route('/api/pip-install')
def api_pip_install():
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
            'output':  (r.stdout + r.stderr)[-4000:],
            'package': pkg,
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'pip install timed out after 120s'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/addon-logs')
def api_addon_logs():
    slug  = request.args.get('slug', '').strip()
    lines = int(request.args.get('lines', 200))
    log_candidates = [
        MC_ROOT / 'logs' / f'{slug}.log',
        MC_ROOT / f'{slug}.log',
        MC_ROOT / 'debug.log',
        MC_ROOT / 'server_out.txt',
        MC_ROOT / 'app.log',
    ]
    for log_path in log_candidates:
        if log_path.exists():
            try:
                content    = log_path.read_text(encoding='utf-8', errors='replace')
                all_lines  = content.splitlines()
                if slug and log_path.name in ('debug.log', 'server_out.txt', 'app.log'):
                    filtered = [l for l in all_lines if slug.lower() in l.lower()]
                    return jsonify({'lines': filtered[-lines:], 'source': str(log_path), 'total': len(filtered)})
                return jsonify({'lines': all_lines[-lines:], 'source': str(log_path), 'total': len(all_lines)})
            except Exception:
                continue
    return jsonify({'lines': [], 'source': None, 'note': 'No log file found', 'total': 0})


@app.route('/api/delete-generated')
def api_delete_generated():
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


@app.route('/api/registry')
def api_registry():
    return jsonify(registry.discover())


@app.route('/api/nav-sections')
def api_nav_sections():
    return jsonify({'sections': registry.nav_sections()})


@app.route('/api/capabilities')
def api_capabilities():
    return jsonify(registry.capabilities())


@app.route('/api/update-manifest')
def api_update_manifest():
    slug = request.args.get('slug','').strip()
    if not slug or '/' in slug:
        return jsonify({'error': 'invalid slug'}), 400
    updates = {}
    for k in ['label','icon','color','category','description','version']:
        v = request.args.get(k)
        if v is not None: updates[k] = v
    caps = request.args.get('capabilities')
    if caps is not None:
        updates['capabilities'] = [c.strip() for c in caps.split(',') if c.strip()]
    reqs = request.args.get('requires')
    if reqs is not None:
        updates['requires'] = [r.strip() for r in reqs.split(',') if r.strip()]
    ok = registry.update_manifest(slug, updates)
    if ok: return jsonify({'success': True, 'slug': slug, 'updates': updates})
    return jsonify({'error': f'{slug} not found'}), 404


@app.route('/api/write-registry')
def api_write_registry():
    data = registry.discover()
    return jsonify({'success': True, 'count': data.get('count', 0), 'path': str(REGISTRY_PATH)})


# ════════════════════════════════════════════════════════════
#  NEW v4 API ROUTES
# ════════════════════════════════════════════════════════════

@app.route('/api/status-all')
def api_status_all():
    """Query MC status for every module in uploads/extracted."""
    results = {}
    try:
        import urllib.request
        scan_dirs = []
        if EXTRACTED_DIR.exists(): scan_dirs.append(EXTRACTED_DIR)
        if ADDONS_DIR.exists():    scan_dirs.append(ADDONS_DIR)
        slugs = set()
        for d in scan_dirs:
            for item in d.iterdir():
                if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('_'):
                    slugs.add(item.name)
        for slug in slugs:
            try:
                url = f'{MC_BASE}/addons/modules/{slug}/status'
                req = urllib.request.Request(url, headers={'Accept': 'application/json'})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    results[slug] = json.loads(resp.read().decode())
            except Exception as e:
                results[slug] = {'status': 'unknown', 'error': str(e)}
    except Exception as e:
        return jsonify({'error': str(e), 'statuses': {}})
    return jsonify({'statuses': results})


@app.route('/api/module-status/<slug>')
def api_module_status(slug):
    """Proxy single module status from MasterChief."""
    if not slug or '/' in slug or '..' in slug:
        return jsonify({'error': 'invalid slug'}), 400
    try:
        import urllib.request
        url = f'{MC_BASE}/addons/modules/{slug}/status'
        req = urllib.request.Request(url, headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=4) as resp:
            return jsonify(json.loads(resp.read().decode()))
    except Exception as e:
        return jsonify({'status': 'unknown', 'error': str(e)})


@app.route('/api/pypi-info')
def api_pypi_info():
    """Fetch real package metadata from PyPI JSON API."""
    pkg = request.args.get('package', '').strip()
    if not pkg:
        return jsonify({'error': 'package required'}), 400
    try:
        import urllib.request
        url = f'https://pypi.org/pypi/{urllib.parse.quote(pkg)}/json'
        req = urllib.request.Request(url, headers={'Accept': 'application/json', 'User-Agent': 'ModuleCenterV4/1.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
        info = data.get('info', {})
        releases = data.get('releases', {})
        version  = info.get('version', '')
        total_releases = len(releases)
        release_files  = releases.get(version, [])
        downloads = sum(f.get('downloads', 0) for f in release_files)
        return jsonify({
            'name':        info.get('name',''),
            'version':     version,
            'summary':     info.get('summary',''),
            'author':      info.get('author',''),
            'license':     info.get('license',''),
            'home_page':   info.get('home_page','') or info.get('project_url',''),
            'requires_python': info.get('requires_python',''),
            'classifiers': info.get('classifiers', [])[:8],
            'requires_dist': (info.get('requires_dist') or [])[:10],
            'keywords':    info.get('keywords',''),
            'releases':    total_releases,
            'downloads':   downloads,
        })
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/api/pypi-search')
def api_pypi_search():
    """Search PyPI via pip index or simple API."""
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'results': []})
    try:
        r = subprocess.run(
            [sys.executable, '-m', 'pip', 'index', 'versions', q],
            capture_output=True, text=True, timeout=15
        )
        results = []
        if r.returncode == 0 and r.stdout:
            results.append({'name': q, 'summary': r.stdout.strip()[:300]})
        return jsonify({'results': results, 'query': q})
    except Exception as e:
        return jsonify({'error': str(e), 'results': []})


@app.route('/api/preview')
def api_preview():
    """Preview generated addon files without writing to disk."""
    pkg      = request.args.get('package', '').strip()
    features = [f.strip() for f in request.args.get('features', '').split(',') if f.strip()]
    slug     = request.args.get('slug', '').strip() or (pkg.replace('-','_').replace('.','_') if pkg else '')
    if not pkg:      return jsonify({'error': 'package required'}), 400
    if not features: return jsonify({'error': 'select at least one feature'}), 400
    try:
        with tempfile.TemporaryDirectory() as tmp:
            result = generate_module(pip_name=pkg, slug=slug, features=features, output_dir=Path(tmp))
            if not result.get('success'):
                return jsonify(result)
            zip_path = Path(result['zip_path'])
            preview_files = []
            with zipfile.ZipFile(zip_path, 'r') as zf:
                for name in zf.namelist():
                    try:
                        content = zf.read(name).decode('utf-8', errors='replace')
                        parts = name.split('/')
                        preview_files.append({
                            'path':    name,
                            'name':    parts[-1] if parts else name,
                            'ext':     Path(name).suffix.lstrip('.'),
                            'content': content[:8000],
                            'size':    len(content),
                        })
                    except Exception:
                        pass
            return jsonify({
                'success':     True,
                'slug':        slug,
                'files':       preview_files,
                'file_count':  len(preview_files),
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notes', methods=['GET', 'POST'])
def api_notes():
    """Per-module notes — stored in notes.json."""
    if request.method == 'GET':
        try:
            if NOTES_PATH.exists():
                return jsonify(json.loads(NOTES_PATH.read_text()))
        except Exception:
            pass
        return jsonify({})
    # POST
    try:
        body = request.get_json(force=True) or {}
        slug = body.get('slug','').strip()
        note = body.get('note','').strip()
        if not slug or '/' in slug:
            return jsonify({'error': 'invalid slug'}), 400
        notes = {}
        if NOTES_PATH.exists():
            try: notes = json.loads(NOTES_PATH.read_text())
            except: pass
        if note:
            notes[slug] = {'text': note, 'updated': datetime.utcnow().isoformat()}
        elif slug in notes:
            del notes[slug]
        NOTES_PATH.write_text(json.dumps(notes, indent=2))
        return jsonify({'success': True, 'slug': slug})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export-registry')
def api_export_registry():
    """Export full registry as a downloadable JSON file."""
    data = registry.discover()
    data['_exported_at'] = datetime.utcnow().isoformat()
    data['_exported_by'] = 'module-command-center-v4'
    body = json.dumps(data, indent=2, default=str)
    return Response(
        body,
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename="registry-export.json"'}
    )


@app.route('/api/system-stats')
def api_system_stats():
    """Quick system stats for the dashboard."""
    import urllib.request
    stats = {
        'python':  sys.version.split()[0],
        'mc_root': str(MC_ROOT),
        'mc_base': MC_BASE,
        'generated_count': len(list(OUTPUT_DIR.glob('*.zip'))),
        'generated_size_kb': round(sum(f.stat().st_size for f in OUTPUT_DIR.glob('*.zip')) / 1024, 1),
        'mc_reachable': False,
        'timestamp': int(time.time()),
    }
    try:
        req = urllib.request.Request(MC_BASE + '/api/stats',
                                     headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            stats['mc_reachable'] = True
            try: stats['mc_stats'] = json.loads(resp.read().decode())
            except: pass
    except Exception:
        pass
    return jsonify(stats)


# ════════════════════════════════════════════════════════════
#  MAIN UI
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
<title>Module Command Center v4</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Unbounded:wght@400;700;900&display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/base16/monokai.min.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#060809;--panel:#0a0d10;--card:#0d1117;--card2:#111820;--border:#1a2535;
  --amber:#f5a623;--green:#00e676;--red:#ff4444;--blue:#58a6ff;--purple:#a78bfa;
  --cyan:#00b8d9;--pink:#ff79c6;
  --text:#cdd6e0;--dim:#4a6070;--mid:#7a9ab0;
  --mono:"Space Mono",monospace;--ui:"Unbounded",sans-serif;
  --r:3px;
}
html,body{height:100%;background:var(--bg);color:var(--text);font-family:var(--mono);font-size:13px;overflow:hidden}

/* ── Layout ── */
.shell{display:flex;flex-direction:column;height:100vh}
.header{display:flex;align-items:center;padding:0 16px;height:48px;background:var(--panel);
  border-bottom:1px solid var(--border);flex-shrink:0;gap:0;z-index:200;position:relative}
.logo{font-family:var(--ui);font-size:9px;font-weight:900;letter-spacing:.3em;
  margin-right:16px;white-space:nowrap;cursor:pointer;user-select:none}
.logo em{color:var(--amber);font-style:normal}
.logo sub{font-size:6px;color:var(--dim);vertical-align:super}
.tabs{display:flex;height:48px;flex:1;overflow-x:auto;scrollbar-width:none}
.tabs::-webkit-scrollbar{display:none}
.tab{padding:0 14px;display:flex;align-items:center;gap:6px;font-size:9px;letter-spacing:.12em;
  color:var(--dim);border-bottom:2px solid transparent;cursor:pointer;white-space:nowrap;
  transition:all .12s;user-select:none;border-top:2px solid transparent}
.tab:hover{color:var(--text)}
.tab.active{color:var(--amber);border-bottom-color:var(--amber);background:rgba(245,166,35,.04)}
.tab .badge{background:var(--amber);color:#000;font-size:7px;font-weight:700;
  padding:1px 5px;border-radius:2px;margin-left:2px}
.tab .dot{width:6px;height:6px;border-radius:50%;display:inline-block;flex-shrink:0}
.hdr-right{display:flex;align-items:center;gap:10px;margin-left:12px;flex-shrink:0}
.clock{font-size:10px;color:var(--dim);letter-spacing:.1em;font-family:var(--mono)}
.mc-ping{width:8px;height:8px;border-radius:50%;background:var(--dim);flex-shrink:0;cursor:default}
.mc-ping.ok{background:var(--green);box-shadow:0 0 6px var(--green)}
.mc-ping.err{background:var(--red)}
.kbd-hint{font-size:9px;color:var(--dim);cursor:pointer;padding:3px 7px;
  border:1px solid var(--border);border-radius:var(--r)}
.kbd-hint:hover{border-color:var(--amber);color:var(--amber)}

.content{flex:1;overflow-y:auto;padding:24px 28px;position:relative}
.content::-webkit-scrollbar{width:4px}
.content::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}

/* ── Page headers ── */
.page-head{margin-bottom:20px}
.page-title{font-family:var(--ui);font-size:clamp(16px,2.5vw,28px);font-weight:900;line-height:1.1}
.page-title em{font-style:normal;-webkit-text-stroke:1.5px var(--amber);color:transparent}
.page-sub{color:var(--dim);font-size:10px;margin-top:5px;letter-spacing:.04em}

/* ── Stats row ── */
.stat-row{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px}
.stat{background:var(--card);border:1px solid var(--border);border-left:3px solid var(--amber);
  padding:10px 14px;border-radius:var(--r);min-width:90px;transition:border-color .2s}
.stat:hover{border-color:var(--amber)}
.stat-label{font-size:8px;color:var(--dim);letter-spacing:.18em;margin-bottom:4px;text-transform:uppercase}
.stat-val{font-size:18px;font-weight:700;color:var(--amber);line-height:1}
.stat-sub{font-size:9px;color:var(--dim);margin-top:3px}

/* ── Grids & Cards ── */
.pkg-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px;margin-top:16px}
.pkg-card{background:var(--card);border:1px solid var(--border);border-left:3px solid var(--border);
  border-radius:var(--r);padding:13px;cursor:pointer;transition:all .15s;position:relative}
.pkg-card:hover{border-color:var(--amber);border-left-color:var(--amber);transform:translateY(-1px);
  box-shadow:0 4px 20px rgba(0,0,0,.4)}
.pkg-name{font-family:var(--ui);font-size:10px;font-weight:700;margin-bottom:2px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pkg-ver{font-size:9px;color:var(--dim);margin-bottom:8px}
.pkg-hint{font-size:9px;color:var(--mid)}

.mod-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px;margin-top:16px}
.mod-card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);
  padding:15px;border-left:3px solid var(--border);transition:all .15s;position:relative}
.mod-card:hover{border-color:rgba(245,166,35,.4);box-shadow:0 2px 12px rgba(0,0,0,.3)}
.mod-card.selected{border-color:var(--amber);background:rgba(245,166,35,.06)}
.mod-card-head{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.mod-icon{font-size:20px;flex-shrink:0}
.mod-title{font-family:var(--ui);font-size:10px;font-weight:700;line-height:1.3}
.mod-slug{font-size:9px;color:var(--dim);margin-top:1px}
.mod-actions{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
.mod-meta{font-size:9px;color:var(--mid);margin-bottom:4px;line-height:1.5}
.mod-check{position:absolute;top:10px;right:10px;width:16px;height:16px;cursor:pointer}

/* Status dot */
.status-dot{width:8px;height:8px;border-radius:50%;display:inline-block;flex-shrink:0;margin-right:4px}
.status-dot.running{background:var(--green);box-shadow:0 0 6px var(--green);animation:pulse 2s infinite}
.status-dot.blueprint{background:var(--blue);box-shadow:0 0 4px var(--blue)}
.status-dot.stopped{background:var(--dim)}
.status-dot.unknown{background:var(--amber);opacity:.5}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}

/* ── Generate panel ── */
.gen-layout{display:grid;grid-template-columns:1fr 1fr;gap:18px;align-items:start;margin-top:16px}
@media(max-width:900px){.gen-layout{grid-template-columns:1fr}}
.feat-panel{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:16px}
.feat-panel h3{font-family:var(--ui);font-size:10px;font-weight:700;margin-bottom:12px;letter-spacing:.1em}
.feat-list{max-height:360px;overflow-y:auto;margin-bottom:12px}
.feat-row{display:flex;align-items:flex-start;gap:8px;padding:5px 0;
  border-bottom:1px solid rgba(26,37,53,.4);cursor:pointer}
.feat-row:hover{background:rgba(245,166,35,.03)}
.feat-row label{font-size:10px;flex:1;cursor:pointer;line-height:1.4}
.feat-row input[type=checkbox]{accent-color:var(--amber);margin-top:2px;flex-shrink:0}
.feat-type{font-size:7px;color:var(--dim);letter-spacing:.05em;text-transform:uppercase}
.out-panel{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:16px;
  min-height:300px}
.out-panel h3{font-family:var(--ui);font-size:10px;font-weight:700;margin-bottom:12px;letter-spacing:.1em}

/* Preview file list */
.preview-files{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px}
.preview-tab{font-size:9px;color:var(--mid);padding:4px 10px;border:1px solid var(--border);
  border-radius:2px;cursor:pointer;transition:all .12s}
.preview-tab.active{color:var(--amber);border-color:var(--amber)}
.preview-tab:hover{border-color:var(--mid)}

/* ── Generated list ── */
.gen-list{margin-top:16px}
.gen-row{display:flex;align-items:center;gap:10px;padding:10px 0;
  border-bottom:1px solid rgba(26,37,53,.5)}
.gen-row-name{font-size:11px;font-weight:600;flex:1}
.gen-row-size{font-size:9px;color:var(--dim);white-space:nowrap}

/* ── Code / Log ── */
.code-wrap{position:relative;margin:0}
.code-wrap pre.hljs{background:#000;border:1px solid var(--border);border-radius:var(--r);
  padding:14px;font-size:10.5px;line-height:1.65;overflow:auto;max-height:480px;
  margin:0;font-family:var(--mono)}
.code-copy{position:absolute;top:8px;right:8px;background:var(--card2);border:1px solid var(--border);
  color:var(--dim);font-size:8px;padding:3px 8px;border-radius:2px;cursor:pointer;
  font-family:var(--mono);letter-spacing:.06em;transition:all .12s}
.code-copy:hover{color:var(--amber);border-color:var(--amber)}
.log-terminal{background:#000;border:1px solid var(--border);border-radius:var(--r);
  padding:14px;font-family:var(--mono);font-size:10.5px;line-height:1.7;
  max-height:500px;overflow-y:auto;color:#aaa;white-space:pre-wrap;word-break:break-all}
.log-line{}
.log-err{color:#ff6b6b}
.log-ok{color:var(--green)}
.log-warn{color:var(--amber)}
.log-dim{color:var(--dim)}

/* ── File tree ── */
.file-tree-panel{display:flex;gap:14px;margin-top:16px}
.file-tree{width:200px;flex-shrink:0;background:var(--card);border:1px solid var(--border);
  border-radius:var(--r);padding:10px;max-height:480px;overflow-y:auto}
.file-item{font-size:10px;color:var(--mid);padding:4px 6px;cursor:pointer;border-radius:2px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:flex;align-items:center;gap:5px}
.file-item:hover,.file-item.active{color:var(--amber);background:rgba(245,166,35,.06)}
.file-ext{font-size:8px;color:var(--dim);background:rgba(255,255,255,.05);
  padding:1px 4px;border-radius:2px;flex-shrink:0}
.file-code-wrap{flex:1;min-width:0}

/* ── Search ── */
.search-row{display:flex;gap:8px;margin-bottom:12px;align-items:center}
.search-row input{flex:1;padding:8px 12px;font-size:11px}
.search-row select{padding:8px 10px;font-size:10px}

/* ── Tags ── */
.tag{display:inline-block;padding:1px 7px;border-radius:2px;font-size:8px;border:1px solid;
  margin-right:3px;margin-bottom:2px;white-space:nowrap;letter-spacing:.04em}
.tag-blue{background:rgba(88,166,255,.1);color:var(--blue);border-color:rgba(88,166,255,.2)}
.tag-green{background:rgba(0,230,118,.1);color:var(--green);border-color:rgba(0,230,118,.2)}
.tag-amber{background:rgba(245,166,35,.1);color:var(--amber);border-color:rgba(245,166,35,.2)}
.tag-red{background:rgba(255,68,68,.1);color:var(--red);border-color:rgba(255,68,68,.2)}
.tag-purple{background:rgba(167,139,250,.1);color:var(--purple);border-color:rgba(167,139,250,.2)}
.tag-cyan{background:rgba(0,184,217,.1);color:var(--cyan);border-color:rgba(0,184,217,.2)}

/* ── Buttons ── */
.btn{background:var(--amber);color:#000;font-family:var(--mono);font-size:9px;font-weight:700;
  letter-spacing:.14em;padding:7px 14px;border:none;border-radius:var(--r);cursor:pointer;
  transition:opacity .12s;white-space:nowrap}
.btn:hover{opacity:.85}
.btn:disabled{opacity:.4;cursor:not-allowed}
.btn-sm{padding:4px 10px;font-size:8px}
.btn-ghost{background:transparent;color:var(--mid);font-family:var(--mono);font-size:9px;
  letter-spacing:.1em;padding:6px 12px;border:1px solid var(--border);border-radius:var(--r);
  cursor:pointer;transition:all .12s;white-space:nowrap}
.btn-ghost:hover{border-color:var(--amber);color:var(--amber)}
.btn-ghost:disabled{opacity:.4;cursor:not-allowed}
.btn-danger{background:transparent;color:var(--red);font-family:var(--mono);font-size:9px;
  padding:6px 12px;border:1px solid rgba(255,68,68,.3);border-radius:var(--r);cursor:pointer;
  transition:all .12s}
.btn-danger:hover{background:rgba(255,68,68,.1);border-color:var(--red)}
.btn-blue{background:var(--blue);color:#000;font-family:var(--mono);font-size:9px;font-weight:700;
  letter-spacing:.12em;padding:7px 14px;border:none;border-radius:var(--r);cursor:pointer}
.btn-blue:hover{opacity:.85}

/* ── Inputs ── */
input,select,textarea{background:var(--card);border:1px solid var(--border);color:var(--text);
  font-family:var(--mono);font-size:11px;padding:8px 12px;border-radius:var(--r);outline:none;
  transition:border-color .12s}
input:focus,select:focus,textarea:focus{border-color:var(--amber)}
textarea{resize:vertical;line-height:1.6}

/* ── Alerts ── */
.err-box{background:rgba(255,68,68,.06);border:1px solid rgba(255,68,68,.25);
  color:#ff8080;padding:12px;border-radius:var(--r);font-size:11px;margin:10px 0}
.ok-box{background:rgba(0,230,118,.06);border:1px solid rgba(0,230,118,.25);
  color:var(--green);padding:12px;border-radius:var(--r);font-size:11px;margin:10px 0}
.info-box{background:rgba(88,166,255,.06);border:1px solid rgba(88,166,255,.25);
  color:var(--blue);padding:12px;border-radius:var(--r);font-size:11px;margin:10px 0}
.loading{color:var(--dim);text-align:center;padding:40px;font-size:11px}

/* ── Batch bar ── */
.batch-bar{position:sticky;top:0;z-index:50;background:rgba(10,13,16,.95);
  backdrop-filter:blur(8px);border-bottom:1px solid var(--border);
  padding:10px 16px;display:flex;align-items:center;gap:10px;margin:-24px -28px 20px;
  padding-left:28px;padding-right:28px;transition:all .2s}
.batch-bar.hidden{display:none}
.batch-count{font-size:10px;font-weight:700;color:var(--amber)}

/* ── Dashboard ── */
.dash-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px}
@media(max-width:800px){.dash-grid{grid-template-columns:1fr}}
.dash-card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:16px}
.dash-card h3{font-family:var(--ui);font-size:9px;font-weight:700;letter-spacing:.15em;
  color:var(--dim);margin-bottom:12px;text-transform:uppercase;border-bottom:1px solid var(--border);
  padding-bottom:8px}
.activity-item{display:flex;align-items:flex-start;gap:10px;padding:6px 0;
  border-bottom:1px solid rgba(26,37,53,.5);font-size:10px}
.activity-icon{flex-shrink:0;width:20px;text-align:center}
.activity-text{flex:1;color:var(--mid);line-height:1.5}
.activity-time{font-size:9px;color:var(--dim);flex-shrink:0}
.health-row{display:flex;align-items:center;gap:8px;padding:7px 0;
  border-bottom:1px solid rgba(26,37,53,.4)}
.health-slug{flex:1;font-size:10px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.health-info{font-size:9px;color:var(--dim);white-space:nowrap}
.quick-actions{display:grid;grid-template-columns:1fr 1fr;gap:8px}

/* ── Network graph ── */
#graph-svg{width:100%;height:500px;background:var(--card);border:1px solid var(--border);
  border-radius:var(--r);display:block}
.graph-node{cursor:pointer}
.graph-node circle{stroke-width:2;transition:r .2s}
.graph-node text{font-family:var(--mono);font-size:10px;fill:var(--text);pointer-events:none}
.graph-link{stroke:rgba(255,255,255,.1);stroke-width:1.5}
.graph-tooltip{position:fixed;background:var(--panel);border:1px solid var(--border);
  padding:10px 14px;border-radius:var(--r);font-size:10px;pointer-events:none;
  z-index:1000;max-width:200px;line-height:1.7}

/* ── Platform ── */
.platform-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px}
@media(max-width:900px){.platform-grid{grid-template-columns:1fr}}
.snippet-box{background:#000;border:1px solid var(--border);border-radius:var(--r);
  padding:12px;font-size:9px;color:#aaa;font-family:var(--mono);line-height:1.8;
  overflow:auto;max-height:180px;white-space:pre}
.kw{color:var(--blue)}
.cm{color:var(--dim)}
.str{color:var(--green)}

/* ── Modal ── */
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:900;
  display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px)}
.modal-box{background:var(--panel);border:1px solid var(--border);border-radius:5px;
  padding:24px;max-width:540px;width:95%;max-height:85vh;overflow-y:auto}
.modal-title{font-family:var(--ui);font-size:12px;font-weight:700;margin-bottom:16px;
  letter-spacing:.1em}
.modal-grid{display:grid;gap:10px}
.field-label{font-size:8px;color:var(--dim);letter-spacing:.15em;margin-bottom:4px;text-transform:uppercase}

/* ── Command palette ── */
.cp-overlay{position:fixed;inset:0;background:rgba(0,0,0,.8);z-index:950;
  display:flex;align-items:flex-start;justify-content:center;padding-top:15vh;
  backdrop-filter:blur(6px)}
.cp-box{background:var(--panel);border:1px solid var(--border);border-radius:6px;
  width:min(560px,90vw);max-height:420px;display:flex;flex-direction:column;
  overflow:hidden;box-shadow:0 24px 80px rgba(0,0,0,.8)}
.cp-input-row{display:flex;align-items:center;padding:12px 16px;border-bottom:1px solid var(--border);gap:10px}
.cp-input-row .cp-icon{color:var(--dim);font-size:14px}
.cp-input{background:transparent;border:none;color:var(--text);font-size:14px;
  font-family:var(--mono);flex:1;outline:none}
.cp-results{flex:1;overflow-y:auto;padding:6px}
.cp-item{display:flex;align-items:center;gap:10px;padding:9px 12px;cursor:pointer;
  border-radius:var(--r);transition:background .1s}
.cp-item:hover,.cp-item.active{background:rgba(245,166,35,.1)}
.cp-item-icon{font-size:14px;flex-shrink:0;width:22px;text-align:center}
.cp-item-label{font-size:12px;flex:1}
.cp-item-hint{font-size:9px;color:var(--dim)}
.cp-section{font-size:8px;color:var(--dim);letter-spacing:.18em;padding:8px 12px 4px;
  text-transform:uppercase}

/* ── Keyboard shortcut help ── */
.kbd-overlay{position:fixed;inset:0;background:rgba(0,0,0,.8);z-index:950;
  display:flex;align-items:center;justify-content:center;backdrop-filter:blur(6px)}
.kbd-box{background:var(--panel);border:1px solid var(--border);border-radius:6px;
  padding:28px;max-width:500px;width:90%}
.kbd-title{font-family:var(--ui);font-size:12px;font-weight:700;margin-bottom:18px;letter-spacing:.1em}
.kbd-row{display:flex;align-items:center;justify-content:space-between;padding:6px 0;
  border-bottom:1px solid rgba(26,37,53,.4)}
.kbd-row kbd{background:var(--card);border:1px solid var(--border);border-bottom-width:2px;
  border-radius:3px;padding:2px 8px;font-family:var(--mono);font-size:10px;color:var(--text)}
.kbd-row .kdesc{font-size:10px;color:var(--mid)}

/* ── Toast stack ── */
#toasts{position:fixed;bottom:20px;right:20px;z-index:9999;display:flex;flex-direction:column;
  gap:6px;pointer-events:none;max-width:360px}
.toast{padding:10px 16px;border-radius:var(--r);font-size:11px;pointer-events:all;
  animation:slideIn .2s ease-out;border-left:3px solid transparent;background:var(--panel);
  border:1px solid var(--border)}
.toast.ok{border-left-color:var(--green);color:var(--green);background:rgba(0,230,118,.08)}
.toast.err{border-left-color:var(--red);color:#ff8080;background:rgba(255,68,68,.08)}
.toast.info{border-left-color:var(--blue);color:var(--blue);background:rgba(88,166,255,.08)}
.toast.warn{border-left-color:var(--amber);color:var(--amber);background:rgba(245,166,35,.08)}
@keyframes slideIn{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}
@keyframes fadeOut{to{transform:translateX(100%);opacity:0}}

/* ── Notes ── */
.note-badge{position:absolute;top:8px;right:8px;font-size:10px;cursor:pointer;opacity:.6}
.note-badge:hover{opacity:1}
.note-text{background:rgba(245,166,35,.06);border:1px solid rgba(245,166,35,.2);
  color:var(--amber);font-size:10px;padding:8px;border-radius:var(--r);margin-top:8px;
  font-family:var(--mono);line-height:1.6;white-space:pre-wrap}

/* ── PyPI info panel ── */
.pypi-panel{background:var(--card2);border:1px solid var(--border);border-radius:var(--r);
  padding:14px;margin-top:12px;font-size:10px}
.pypi-panel .pypi-name{font-family:var(--ui);font-size:12px;font-weight:700;margin-bottom:4px}
.pypi-panel .pypi-summary{color:var(--mid);margin-bottom:10px;line-height:1.6}
.pypi-meta-grid{display:grid;grid-template-columns:auto 1fr;gap:4px 12px}
.pypi-meta-key{color:var(--dim);font-size:9px;letter-spacing:.1em;text-transform:uppercase;
  align-self:start;padding-top:1px}
.pypi-meta-val{color:var(--text);font-size:10px;word-break:break-word}

/* ── Category filter ── */
.cat-filters{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}
.cat-filter{font-size:8px;letter-spacing:.1em;padding:4px 10px;border:1px solid var(--border);
  border-radius:20px;cursor:pointer;transition:all .12s;color:var(--dim);text-transform:uppercase}
.cat-filter:hover{border-color:var(--mid);color:var(--mid)}
.cat-filter.active{border-color:var(--amber);color:var(--amber);background:rgba(245,166,35,.08)}

/* ── Auto-refresh toggle ── */
.refresh-toggle{display:flex;align-items:center;gap:7px;font-size:9px;color:var(--dim);cursor:pointer}
.toggle-pill{width:32px;height:16px;background:var(--border);border-radius:8px;position:relative;
  transition:background .2s;flex-shrink:0}
.toggle-pill.on{background:var(--amber)}
.toggle-pill::after{content:'';position:absolute;width:12px;height:12px;background:#fff;
  border-radius:50%;top:2px;left:2px;transition:left .2s}
.toggle-pill.on::after{left:18px}

/* ── Progress bar ── */
.progress-wrap{background:var(--border);border-radius:2px;height:3px;margin:8px 0}
.progress-bar{height:3px;border-radius:2px;background:var(--amber);transition:width .3s ease}

::-webkit-scrollbar{width:4px;height:4px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}
</style>
</head>
<body>
<div class="shell">

<header class="header">
  <div class="logo" onclick="switchTab('dashboard')">
    <em>[</em>MODULE CENTER<em>]</em><sub>v4</sub>
  </div>
  <div class="tabs" id="tabs">
    <div class="tab active" data-tab="dashboard">⬛ DASHBOARD</div>
    <div class="tab" data-tab="marketplace">📦 MARKET <span class="badge" id="pkg-badge">…</span></div>
    <div class="tab" data-tab="generate">⚡ GENERATE</div>
    <div class="tab" data-tab="modules">🗂 MODULES <span class="badge" id="installed-badge">…</span></div>
    <div class="tab" data-tab="generated-list">📁 GENERATED <span class="badge" id="gen-badge">…</span></div>
    <div class="tab" data-tab="pip-manager">🐍 PIP</div>
    <div class="tab" data-tab="logs">📋 LOGS</div>
    <div class="tab" data-tab="network">🕸 NETWORK</div>
    <div class="tab" data-tab="platform">⚙ PLATFORM</div>
  </div>
  <div class="hdr-right">
    <div id="mc-ping" class="mc-ping" title="MasterChief connection status"></div>
    <div class="clock" id="clock"></div>
    <div class="kbd-hint" onclick="showKbdHelp()">? HELP</div>
    <div class="kbd-hint" onclick="showCommandPalette()">⌘K</div>
  </div>
</header>

<div class="content" id="content">
  <div class="loading">Loading…</div>
</div>
</div>

<!-- Toast container -->
<div id="toasts"></div>

<script>
// ══════════════════════════════════════════════════════════════
//  CORE — proxy detection, fetch, tab routing
// ══════════════════════════════════════════════════════════════
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

async function apiPost(path, body) {
  var r = await fetch(window.PB + '/api/' + path, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(body),
  });
  var txt = await r.text();
  try { return JSON.parse(txt); }
  catch(e) { throw new Error('Non-JSON: ' + txt.slice(0,200)); }
}

// ── Tab routing ────────────────────────────────────────────────
var _tab = 'dashboard';
var _generatePkg = null;
var _prevTab = null;

document.getElementById('tabs').addEventListener('click', function(e) {
  var t = e.target.closest('.tab');
  if (!t) return;
  switchTab(t.dataset.tab);
});

function switchTab(name, skipHistory) {
  if (!skipHistory) _prevTab = _tab;
  _tab = name;
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === name));
  renderTab(name);
}

function renderTab(name) {
  var c = document.getElementById('content');
  c.innerHTML = '<div class="loading">Loading…</div>';
  switch(name) {
    case 'dashboard':      loadDashboard(); break;
    case 'marketplace':    loadMarketplace(); break;
    case 'generate':       loadGenerate(_generatePkg); break;
    case 'modules':        loadModules(); break;
    case 'generated-list': loadGeneratedList(); break;
    case 'pip-manager':    loadPip(); break;
    case 'logs':           loadLogs(); break;
    case 'network':        loadNetwork(); break;
    case 'platform':       loadPlatform(); break;
  }
}

// ── Clock ──────────────────────────────────────────────────────
function tickClock() {
  var d = new Date();
  var h = String(d.getHours()).padStart(2,'0');
  var m = String(d.getMinutes()).padStart(2,'0');
  var s = String(d.getSeconds()).padStart(2,'0');
  var el = document.getElementById('clock');
  if (el) el.textContent = h + ':' + m + ':' + s;
}
setInterval(tickClock, 1000);
tickClock();

// ── MC ping ────────────────────────────────────────────────────
async function pingMC() {
  var el = document.getElementById('mc-ping');
  if (!el) return;
  try {
    var d = await apiFetch('system-stats');
    el.className = 'mc-ping ' + (d.mc_reachable ? 'ok' : 'err');
    el.title = d.mc_reachable ? 'MasterChief: Online' : 'MasterChief: Unreachable';
  } catch(e) {
    el.className = 'mc-ping err';
  }
}
pingMC();
setInterval(pingMC, 30000);

// ══════════════════════════════════════════════════════════════
//  TOAST STACK
// ══════════════════════════════════════════════════════════════
var _toastId = 0;
function showToast(msg, type='info', duration=4000) {
  var container = document.getElementById('toasts');
  if (!container) return;
  var id = ++_toastId;
  var el = document.createElement('div');
  el.className = 'toast ' + type;
  el.id = 'toast-' + id;
  el.textContent = msg;
  el.onclick = () => el.remove();
  container.appendChild(el);
  // keep max 5
  var all = container.children;
  while (all.length > 5) all[0].remove();
  setTimeout(() => {
    if (document.getElementById('toast-'+id)) {
      el.style.animation = 'fadeOut .25s forwards';
      setTimeout(() => el.remove(), 250);
    }
  }, duration);
}

// ══════════════════════════════════════════════════════════════
//  COMMAND PALETTE
// ══════════════════════════════════════════════════════════════
var _cp_active = -1;

var CP_COMMANDS = [
  {icon:'⬛', label:'Dashboard',       hint:'G D', action:()=>switchTab('dashboard')},
  {icon:'📦', label:'Marketplace',     hint:'G M', action:()=>switchTab('marketplace')},
  {icon:'⚡', label:'Generate Module', hint:'G G', action:()=>switchTab('generate')},
  {icon:'🗂', label:'Modules',         hint:'G I', action:()=>switchTab('modules')},
  {icon:'📁', label:'Generated',       hint:'G F', action:()=>switchTab('generated-list')},
  {icon:'🐍', label:'PIP Manager',     hint:'G P', action:()=>switchTab('pip-manager')},
  {icon:'📋', label:'Logs',            hint:'G L', action:()=>switchTab('logs')},
  {icon:'🕸', label:'Network Graph',   hint:'G N', action:()=>switchTab('network')},
  {icon:'⚙', label:'Platform',        hint:'G X', action:()=>switchTab('platform')},
  {icon:'↺', label:'Re-discover Registry', action:()=>doDiscover()},
  {icon:'📋', label:'Copy main.py Hook',   action:()=>copyNavSnippet()},
  {icon:'⬇', label:'Export Registry',     action:()=>exportRegistry()},
  {icon:'?', label:'Keyboard Shortcuts',   hint:'?',  action:()=>showKbdHelp()},
];

function showCommandPalette() {
  if (document.getElementById('cp-overlay')) return;
  var overlay = document.createElement('div');
  overlay.className = 'cp-overlay';
  overlay.id = 'cp-overlay';
  overlay.innerHTML = `
    <div class="cp-box" id="cp-box">
      <div class="cp-input-row">
        <span class="cp-icon">⌘</span>
        <input class="cp-input" id="cp-input" placeholder="Type a command…" autocomplete="off"/>
        <span style="font-size:9px;color:var(--dim)">ESC</span>
      </div>
      <div class="cp-results" id="cp-results"></div>
    </div>`;
  overlay.addEventListener('click', e => { if (e.target===overlay) closeCommandPalette(); });
  document.body.appendChild(overlay);
  var input = document.getElementById('cp-input');
  renderCpResults('');
  input.focus();
  input.addEventListener('input', () => renderCpResults(input.value));
  input.addEventListener('keydown', cpKeydown);
}

function renderCpResults(q) {
  q = q.toLowerCase();
  var items = q ? CP_COMMANDS.filter(c => c.label.toLowerCase().includes(q)) : CP_COMMANDS;
  _cp_active = items.length ? 0 : -1;
  var el = document.getElementById('cp-results');
  if (!el) return;
  if (!items.length) {
    el.innerHTML = '<div style="padding:20px;text-align:center;font-size:10px;color:var(--dim)">No commands found</div>';
    return;
  }
  el.innerHTML = '<div class="cp-section">Commands</div>' + items.map((c,i) =>
    `<div class="cp-item ${i===0?'active':''}" data-i="${i}" onclick="runCpCmd(${CP_COMMANDS.indexOf(c)})">
      <span class="cp-item-icon">${c.icon}</span>
      <span class="cp-item-label">${c.label}</span>
      ${c.hint ? `<span class="cp-item-hint">${c.hint}</span>` : ''}
    </div>`
  ).join('');
}

function cpKeydown(e) {
  var items = document.querySelectorAll('.cp-item');
  if (e.key === 'ArrowDown') {
    e.preventDefault();
    _cp_active = Math.min(_cp_active+1, items.length-1);
    items.forEach((el,i) => el.classList.toggle('active', i===_cp_active));
    items[_cp_active]?.scrollIntoView({block:'nearest'});
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    _cp_active = Math.max(_cp_active-1, 0);
    items.forEach((el,i) => el.classList.toggle('active', i===_cp_active));
    items[_cp_active]?.scrollIntoView({block:'nearest'});
  } else if (e.key === 'Enter') {
    var active = items[_cp_active];
    if (active) active.click();
  } else if (e.key === 'Escape') {
    closeCommandPalette();
  }
}

function runCpCmd(i) {
  closeCommandPalette();
  setTimeout(() => CP_COMMANDS[i]?.action(), 100);
}

function closeCommandPalette() {
  var el = document.getElementById('cp-overlay');
  if (el) el.remove();
}

// ══════════════════════════════════════════════════════════════
//  KEYBOARD SHORTCUTS
// ══════════════════════════════════════════════════════════════
var _gMode = false;
document.addEventListener('keydown', function(e) {
  var tag = document.activeElement.tagName.toLowerCase();
  if (['input','textarea','select'].includes(tag)) return;
  if (e.ctrlKey || e.metaKey) {
    if (e.key === 'k') { e.preventDefault(); showCommandPalette(); }
    return;
  }
  if (e.key === 'Escape') {
    closeCommandPalette(); closeModal(); closeKbdHelp(); _gMode = false; return;
  }
  if (e.key === '?') { showKbdHelp(); return; }
  if (e.key === '/') { focusSearch(); return; }
  if (_gMode) {
    _gMode = false;
    var map = {d:'dashboard',m:'marketplace',g:'generate',i:'modules',
               f:'generated-list',p:'pip-manager',l:'logs',n:'network',x:'platform'};
    if (map[e.key]) switchTab(map[e.key]);
  } else if (e.key === 'g') {
    _gMode = true;
    setTimeout(()=>{ _gMode=false; }, 1200);
  } else if (e.key === 'r') {
    renderTab(_tab);
  } else if (e.key === '[') {
    if (_prevTab) switchTab(_prevTab);
  }
});

function focusSearch() {
  var s = document.querySelector('.search-row input') || document.getElementById('cp-input');
  if (s) { s.focus(); } else { showCommandPalette(); }
}

function showKbdHelp() {
  if (document.getElementById('kbd-overlay')) return;
  var overlay = document.createElement('div');
  overlay.className = 'kbd-overlay';
  overlay.id = 'kbd-overlay';
  overlay.innerHTML = `
    <div class="kbd-box">
      <div class="kbd-title">KEYBOARD SHORTCUTS</div>
      ${[
        ['Ctrl/⌘ + K','Open command palette'],
        ['?','Show this help'],
        ['/','Focus search'],
        ['r','Refresh current panel'],
        ['[ ','Go back'],
        ['g d','Dashboard'],
        ['g m','Marketplace'],
        ['g g','Generate'],
        ['g i','Modules'],
        ['g f','Generated'],
        ['g p','PIP Manager'],
        ['g l','Logs'],
        ['g n','Network graph'],
        ['g x','Platform'],
        ['Esc','Close dialogs'],
      ].map(([k,d]) => `
        <div class="kbd-row">
          <span class="kdesc">${d}</span>
          <kbd>${k}</kbd>
        </div>`).join('')}
      <div style="text-align:center;margin-top:16px">
        <button class="btn-ghost" onclick="closeKbdHelp()">CLOSE</button>
      </div>
    </div>`;
  overlay.addEventListener('click', e => { if (e.target===overlay) closeKbdHelp(); });
  document.body.appendChild(overlay);
}
function closeKbdHelp() {
  var el = document.getElementById('kbd-overlay');
  if (el) el.remove();
}

// ══════════════════════════════════════════════════════════════
//  DASHBOARD
// ══════════════════════════════════════════════════════════════
var _autoRefresh = false;
var _arTimer = null;
var _dashStatuses = {};

async function loadDashboard() {
  var c = document.getElementById('content');
  c.innerHTML = `
    <div class="page-head">
      <div class="page-title"><em>COMMAND</em> CENTER</div>
      <div class="page-sub">Live system overview — MasterChief Module Health & Activity</div>
    </div>
    <div class="stat-row" id="dash-stats">
      <div class="loading">Loading stats…</div>
    </div>
    <div style="display:flex;gap:10px;align-items:center;margin-bottom:16px">
      <button class="btn" onclick="refreshDashAll()">↺ Refresh</button>
      <button class="btn-ghost" onclick="switchTab('modules')">🗂 All Modules</button>
      <button class="btn-ghost" onclick="switchTab('marketplace')">📦 Marketplace</button>
      <label class="refresh-toggle" onclick="toggleAutoRefresh()">
        <div class="toggle-pill" id="ar-pill"></div>
        Auto-refresh
      </label>
    </div>
    <div class="dash-grid">
      <div class="dash-card">
        <h3>🔴 Live Module Health</h3>
        <div id="health-list"><div class="loading">Checking status…</div></div>
      </div>
      <div class="dash-card">
        <h3>⚡ Quick Actions</h3>
        <div class="quick-actions">
          <button class="btn-ghost" style="font-size:10px" onclick="switchTab('marketplace')">📦 Browse Packages</button>
          <button class="btn-ghost" style="font-size:10px" onclick="switchTab('generate')">⚡ Generate Module</button>
          <button class="btn-ghost" style="font-size:10px" onclick="doDiscover()">↺ Sync Registry</button>
          <button class="btn-ghost" style="font-size:10px" onclick="exportRegistry()">⬇ Export Registry</button>
          <button class="btn-ghost" style="font-size:10px" onclick="switchTab('pip-manager')">🐍 Install Package</button>
          <button class="btn-ghost" style="font-size:10px" onclick="switchTab('network')">🕸 Capability Graph</button>
        </div>
        <div style="margin-top:16px">
          <h3 style="margin-bottom:10px">⚙ System</h3>
          <div id="sys-info"><div class="loading">Loading…</div></div>
        </div>
      </div>
      <div class="dash-card" style="grid-column:1/-1">
        <h3>📊 Module Breakdown</h3>
        <div id="dash-breakdown"><div class="loading">Loading…</div></div>
      </div>
    </div>`;

  refreshDashAll();
}

async function refreshDashAll() {
  try {
    var [statuses, installed, sys] = await Promise.all([
      apiFetch('status-all'),
      apiFetch('installed'),
      apiFetch('system-stats'),
    ]);
    _dashStatuses = statuses.statuses || {};

    // Stats row
    var mods = installed.modules || [];
    var running = Object.values(_dashStatuses).filter(s => s.status === 'running').length;
    var blueprint = Object.values(_dashStatuses).filter(s => s.status === 'blueprint').length;
    document.getElementById('dash-stats').innerHTML = `
      <div class="stat"><div class="stat-label">Total Modules</div><div class="stat-val">${mods.length}</div></div>
      <div class="stat" style="border-left-color:var(--green)">
        <div class="stat-label">Running</div><div class="stat-val" style="color:var(--green)">${running}</div></div>
      <div class="stat" style="border-left-color:var(--blue)">
        <div class="stat-label">Blueprint</div><div class="stat-val" style="color:var(--blue)">${blueprint}</div></div>
      <div class="stat" style="border-left-color:var(--purple)">
        <div class="stat-label">Generated Zips</div><div class="stat-val" style="color:var(--purple)">${sys.generated_count||0}</div>
        <div class="stat-sub">${sys.generated_size_kb||0} KB</div>
      </div>
      <div class="stat" style="border-left-color:var(--cyan)">
        <div class="stat-label">MC Platform</div>
        <div class="stat-val" style="font-size:11px;color:${sys.mc_reachable?'var(--green)':'var(--red)'}">
          ${sys.mc_reachable ? '● ONLINE' : '● OFFLINE'}
        </div>
      </div>`;

    // Health list
    var healthHtml = mods.length === 0
      ? '<div class="info-box">No modules found</div>'
      : mods.map(m => {
          var st = _dashStatuses[m.slug] || {};
          var cls = st.status==='running' ? 'running' : st.status==='blueprint' ? 'blueprint' : st.status==='stopped' ? 'stopped' : 'unknown';
          var info = '';
          if (st.port) info = `port ${st.port}`;
          else if (st.pid) info = `pid ${st.pid}`;
          else if (st.status==='blueprint') info = 'blueprint';
          return `<div class="health-row">
            <span class="status-dot ${cls}"></span>
            <span class="health-slug" title="${m.slug}">${m.icon||'📦'} ${m.label||m.slug}</span>
            <span class="health-info">${info}</span>
            ${st.proxy_url ? `<a href="${st.proxy_url}" target="_blank" style="font-size:9px;color:var(--blue);text-decoration:none">↗</a>` : ''}
          </div>`;
        }).join('');
    var hl = document.getElementById('health-list');
    if (hl) hl.innerHTML = healthHtml;

    // Sys info
    var si = document.getElementById('sys-info');
    if (si) si.innerHTML = `
      <div class="mod-meta">Python ${sys.python}</div>
      <div class="mod-meta">MC Root: <span style="color:var(--amber)">${sys.mc_root}</span></div>
      <div class="mod-meta">MC Base: <span style="color:var(--amber)">${sys.mc_base}</span></div>`;

    // Breakdown by source
    var extracted = mods.filter(m=>m.source==='extracted').length;
    var addons    = mods.filter(m=>m.source==='addons').length;
    var generated = mods.filter(m=>m.is_generated).length;
    var blueprints= mods.filter(m=>m.is_blueprint).length;
    var db = document.getElementById('dash-breakdown');
    if (db) db.innerHTML = `
      <div style="display:flex;gap:16px;flex-wrap:wrap">
        ${[
          ['uploads/extracted/', extracted, 'var(--amber)'],
          ['addons/modules/', addons, 'var(--blue)'],
          ['Generated by MCC', generated, 'var(--green)'],
          ['Blueprint style', blueprints, 'var(--purple)'],
        ].map(([l,v,c]) => `
          <div style="flex:1;min-width:160px;background:var(--card2);border:1px solid var(--border);
            border-left:3px solid ${c};border-radius:var(--r);padding:12px 14px">
            <div style="font-size:9px;color:var(--dim);letter-spacing:.12em;margin-bottom:6px">${l}</div>
            <div style="font-size:24px;font-weight:700;color:${c}">${v}</div>
          </div>`).join('')}
      </div>`;

    refreshBadges();
  } catch(e) {
    showToast('Dashboard error: ' + e.message, 'err');
  }
}

function toggleAutoRefresh() {
  _autoRefresh = !_autoRefresh;
  var pill = document.getElementById('ar-pill');
  if (pill) pill.classList.toggle('on', _autoRefresh);
  if (_autoRefresh) {
    showToast('Auto-refresh ON (10s)', 'info');
    _arTimer = setInterval(() => { if (_tab==='dashboard') refreshDashAll(); }, 10000);
  } else {
    clearInterval(_arTimer);
    showToast('Auto-refresh OFF', 'info');
  }
}

// ══════════════════════════════════════════════════════════════
//  MARKETPLACE
// ══════════════════════════════════════════════════════════════
var _allPkgs = [];
var _pkgFilter = 'all';

const PALETTE = ['#f5a623','#58a6ff','#00e676','#ff6b6b','#a78bfa','#34d399','#fb7185','#38bdf8','#00b8d9','#ff79c6'];
const ICONS   = ['📦','🔧','⚡','🌐','🛠','🔌','💡','🚀','🔍','📊','🗄','🔐','☁','🖥','🧩','⚙','🎯','🔬'];

async function loadMarketplace() {
  var c = document.getElementById('content');
  c.innerHTML = `
    <div class="page-head">
      <div class="page-title"><em>MODULE</em> MARKETPLACE</div>
      <div class="page-sub">Browse all installed pip packages — click to generate a MasterChief module</div>
    </div>
    <div class="search-row">
      <input id="pkg-search" type="text" placeholder="Search packages…" oninput="filterPkgs(this.value)"/>
      <button class="btn-ghost" onclick="switchTab('pip-manager')">+ Install Package</button>
    </div>
    <div class="cat-filters" id="cat-filters">
      ${['all','web','data','security','infra','cloud','aws','azure','utility'].map(c =>
        `<div class="cat-filter ${c==='all'?'active':''}" onclick="setCatFilter('${c}')">${c}</div>`
      ).join('')}
    </div>
    <div class="stat-row" id="mkt-stats"></div>
    <div id="pypi-panel"></div>
    <div class="pkg-grid" id="pkg-grid"><div class="loading">Loading packages…</div></div>`;

  try {
    var d = await apiFetch('packages');
    _allPkgs = d.packages || [];
    document.getElementById('pkg-search').placeholder = `Search ${_allPkgs.length} packages…`;
    document.getElementById('mkt-stats').innerHTML = `
      <div class="stat"><div class="stat-label">Packages</div><div class="stat-val">${_allPkgs.length}</div></div>
      <div class="stat" style="border-left-color:var(--blue)">
        <div class="stat-label">Web</div><div class="stat-val" style="color:var(--blue)">${_allPkgs.filter(p=>inferCat(p.name)==='web').length}</div></div>
      <div class="stat" style="border-left-color:var(--cyan)">
        <div class="stat-label">Data</div><div class="stat-val" style="color:var(--cyan)">${_allPkgs.filter(p=>inferCat(p.name)==='data').length}</div></div>
      <div class="stat" style="border-left-color:var(--red)">
        <div class="stat-label">Security</div><div class="stat-val" style="color:var(--red)">${_allPkgs.filter(p=>inferCat(p.name)==='security').length}</div></div>`;
    document.getElementById('pkg-badge').textContent = _allPkgs.length;
    renderPkgGrid(_allPkgs);
  } catch(e) {
    document.getElementById('pkg-grid').innerHTML = `<div class="err-box">Error: ${e.message}</div>`;
  }
}

function inferCat(n) {
  n = n.toLowerCase();
  if (n.includes('flask') || n.includes('http') || n.includes('request') || n.includes('api') || n.includes('django') || n.includes('fastapi')) return 'web';
  if (n.includes('sql') || n.includes('db') || n.includes('mongo') || n.includes('redis') || n.includes('pandas') || n.includes('numpy')) return 'data';
  if (n.includes('auth') || n.includes('jwt') || n.includes('crypt') || n.includes('ssl') || n.includes('vault')) return 'security';
  if (n.includes('kube') || n.includes('docker') || n.includes('container') || n.includes('ansible')) return 'infra';
  if (n.includes('aws') || n.includes('boto') || n.includes('s3')) return 'aws';
  if (n.includes('azure')) return 'azure';
  if (n.includes('cloud') || n.includes('gcp') || n.includes('terraform')) return 'cloud';
  return 'utility';
}

function inferTags(n) {
  var cat = inferCat(n);
  var tags = [cat];
  n = n.toLowerCase();
  if (n.includes('async')) tags.push('async');
  if (n.includes('cli')) tags.push('cli');
  return tags.slice(0,3);
}

function setCatFilter(cat) {
  _pkgFilter = cat;
  document.querySelectorAll('.cat-filter').forEach(el => el.classList.toggle('active', el.textContent===cat));
  var filtered = cat === 'all' ? _allPkgs : _allPkgs.filter(p => inferCat(p.name) === cat);
  renderPkgGrid(filtered);
}

function renderPkgGrid(pkgs) {
  var el = document.getElementById('pkg-grid');
  if (!el) return;
  if (!pkgs.length) { el.innerHTML = '<div class="loading">No packages match</div>'; return; }
  el.innerHTML = pkgs.map((p,i) => {
    var col  = PALETTE[i % PALETTE.length];
    var ico  = ICONS[i % ICONS.length];
    var tags = inferTags(p.name).map(t => `<span class="tag tag-blue">${t}</span>`).join('');
    return `<div class="pkg-card" style="border-left-color:${col}" onclick="openGenerate('${p.name}')"
      oncontextmenu="event.preventDefault();fetchPypiInfo('${p.name}')">
      <div class="pkg-name">${ico} ${p.name}</div>
      <div class="pkg-ver">v${p.version}</div>
      <div style="margin-bottom:8px">${tags}</div>
      <div class="pkg-hint">Click to generate  ·  Right-click for PyPI info</div>
    </div>`;
  }).join('');
}

function filterPkgs(q) {
  q = q.toLowerCase();
  var base = _pkgFilter === 'all' ? _allPkgs : _allPkgs.filter(p => inferCat(p.name) === _pkgFilter);
  renderPkgGrid(q ? base.filter(p => p.name.toLowerCase().includes(q)) : base);
}

async function fetchPypiInfo(pkg) {
  var panel = document.getElementById('pypi-panel');
  if (!panel) return;
  panel.innerHTML = '<div class="loading">Fetching PyPI info…</div>';
  try {
    var d = await apiFetch('pypi-info', {package: pkg});
    if (d.error) { panel.innerHTML = `<div class="err-box">${d.error}</div>`; return; }
    var deps = (d.requires_dist||[]).map(r=>`<span class="tag tag-blue">${r.split(' ')[0]}</span>`).join(' ');
    var classes = (d.classifiers||[]).filter(c=>c.startsWith('Topic')).map(c=>
      `<span class="tag tag-purple">${c.split('::').pop().trim()}</span>`).join(' ');
    panel.innerHTML = `
      <div class="pypi-panel">
        <div class="pypi-name">📦 ${d.name} <span style="color:var(--dim);font-size:10px">v${d.version}</span></div>
        <div class="pypi-summary">${d.summary||'No description'}</div>
        <div class="pypi-meta-grid">
          ${d.author ? `<div class="pypi-meta-key">Author</div><div class="pypi-meta-val">${d.author}</div>` : ''}
          ${d.license ? `<div class="pypi-meta-key">License</div><div class="pypi-meta-val">${d.license}</div>` : ''}
          ${d.requires_python ? `<div class="pypi-meta-key">Python</div><div class="pypi-meta-val">${d.requires_python}</div>` : ''}
          ${d.releases ? `<div class="pypi-meta-key">Releases</div><div class="pypi-meta-val">${d.releases}</div>` : ''}
          ${d.home_page ? `<div class="pypi-meta-key">Home</div><div class="pypi-meta-val"><a href="${d.home_page}" target="_blank" style="color:var(--blue)">${d.home_page.slice(0,60)}</a></div>` : ''}
        </div>
        ${deps ? `<div style="margin-top:10px"><div class="field-label">Dependencies</div>${deps}</div>` : ''}
        ${classes ? `<div style="margin-top:8px">${classes}</div>` : ''}
        <div style="display:flex;gap:8px;margin-top:12px">
          <button class="btn btn-sm" onclick="openGenerate('${pkg}')">⚡ Generate Module</button>
          <button class="btn-ghost" style="padding:4px 10px;font-size:8px" onclick="document.getElementById('pypi-panel').innerHTML=''">✕ Close</button>
        </div>
      </div>`;
  } catch(e) {
    panel.innerHTML = `<div class="err-box">${e.message}</div>`;
  }
}

function openGenerate(pkg) {
  _generatePkg = pkg;
  switchTab('generate');
}

// ══════════════════════════════════════════════════════════════
//  GENERATE
// ══════════════════════════════════════════════════════════════
var _feats = [];
var _previewFiles = [];
var _previewIdx = 0;

async function loadGenerate(pkg) {
  var c = document.getElementById('content');
  if (!pkg) {
    c.innerHTML = `
      <div class="page-head">
        <div class="page-title"><em>GENERATE</em> MODULE</div>
        <div class="page-sub">Select a package from the Marketplace to begin</div>
      </div>
      <button class="btn-ghost" onclick="switchTab('marketplace')">← Back to Marketplace</button>
      <div style="margin-top:20px">
        <div class="field-label">Or enter a package name directly</div>
        <div style="display:flex;gap:8px;margin-top:8px">
          <input id="direct-pkg" type="text" placeholder="e.g. requests, boto3, kubernetes" style="flex:1"/>
          <button class="btn" onclick="openGenerate(document.getElementById('direct-pkg').value.trim())">GO</button>
        </div>
      </div>`;
    return;
  }
  var defaultSlug = pkg.replace(/-/g,'_').replace(/\./g,'_');
  c.innerHTML = `
    <div class="page-head">
      <div class="page-title">⚡ <em>${pkg.toUpperCase()}</em></div>
      <div class="page-sub" id="feat-status">Introspecting package…</div>
    </div>
    <button class="btn-ghost" style="margin-bottom:16px" onclick="switchTab('marketplace')">← Marketplace</button>
    <div class="gen-layout">
      <div class="feat-panel">
        <h3>SELECT FEATURES</h3>
        <div style="display:flex;gap:6px;margin-bottom:10px">
          <button class="btn-ghost" style="flex:1;padding:5px" onclick="selectAll()">ALL</button>
          <button class="btn-ghost" style="flex:1;padding:5px" onclick="selectNone()">NONE</button>
          <button class="btn-ghost" style="flex:1;padding:5px" onclick="selectByType('function')">FUNCS</button>
          <button class="btn-ghost" style="flex:1;padding:5px" onclick="selectByType('class')">CLASSES</button>
        </div>
        <div class="feat-list" id="feat-list"><div class="loading">Introspecting ${pkg}…</div></div>
        <div style="display:grid;gap:8px;margin-top:10px">
          <div>
            <div class="field-label">Slug</div>
            <input id="slug-input" type="text" value="${defaultSlug}" style="width:100%"/>
          </div>
          <div style="display:flex;gap:6px">
            <button class="btn" style="flex:1" onclick="doGenerate('${pkg}')">⚡ GENERATE</button>
            <button class="btn-ghost" style="flex:1" onclick="doPreview('${pkg}')">👁 PREVIEW</button>
          </div>
        </div>
      </div>
      <div class="out-panel" id="out-panel">
        <h3>OUTPUT</h3>
        <div style="color:var(--dim);font-size:11px;text-align:center;padding:40px 0;line-height:2">
          Configure features then click<br>
          <strong style="color:var(--amber)">GENERATE</strong> to create &amp; download  ·
          <strong style="color:var(--blue)">PREVIEW</strong> to inspect first
        </div>
      </div>
    </div>`;

  try {
    var d = await apiFetch('introspect', {package: pkg});
    _feats = d.features || [];
    document.getElementById('feat-status').textContent = `${_feats.length} features found`;
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
  el.innerHTML = feats.map(f => `
    <div class="feat-row" onclick="this.querySelector('input').click()">
      <input type="checkbox" name="feat" value="${f.name}" checked/>
      <label>${f.name}
        <span class="feat-type">[${f.type}]</span>
        ${f.label ? `<br><span style="color:var(--dim);font-size:9px">${f.label.slice(0,70)}</span>` : ''}
      </label>
    </div>`).join('');
}

function selectAll()  { document.querySelectorAll('input[name=feat]').forEach(c => c.checked=true); }
function selectNone() { document.querySelectorAll('input[name=feat]').forEach(c => c.checked=false); }
function selectByType(type) {
  document.querySelectorAll('input[name=feat]').forEach(c => {
    var row = c.closest('.feat-row');
    var typeSpan = row?.querySelector('.feat-type');
    c.checked = typeSpan && typeSpan.textContent.includes(type);
  });
}

function getSelectedFeatures() {
  return [...document.querySelectorAll('input[name=feat]:checked')].map(c => c.value);
}

async function doPreview(pkg) {
  var checked = getSelectedFeatures();
  if (!checked.length) { showToast('Select at least one feature', 'warn'); return; }
  var slug = document.getElementById('slug-input')?.value.trim() || pkg.replace(/-/g,'_');
  var out  = document.getElementById('out-panel');
  out.innerHTML = '<h3>PREVIEW</h3><div class="loading">Generating preview…</div>';
  try {
    var d = await apiFetch('preview', {package: pkg, features: checked.join(','), slug});
    if (d.error) { out.innerHTML = `<h3>PREVIEW</h3><div class="err-box">${d.error}</div>`; return; }
    _previewFiles = d.files || [];
    _previewIdx = 0;
    renderPreview(out);
  } catch(e) {
    out.innerHTML = `<h3>PREVIEW</h3><div class="err-box">Error: ${e.message}</div>`;
  }
}

function renderPreview(out) {
  if (!out) out = document.getElementById('out-panel');
  if (!out) return;
  var f = _previewFiles[_previewIdx];
  var tabs = _previewFiles.map((pf,i) =>
    `<div class="preview-tab ${i===_previewIdx?'active':''}" onclick="switchPreview(${i})">${pf.name}</div>`
  ).join('');
  out.innerHTML = `
    <h3>PREVIEW — ${_previewFiles.length} files</h3>
    <div class="preview-files">${tabs}</div>
    <div class="code-wrap">
      <pre class="hljs"><code id="preview-code" class="${langClass(f?.ext)}">${escHtml(f?.content||'')}</code></pre>
      <button class="code-copy" onclick="copyCode('preview-code')">COPY</button>
    </div>
    <div style="display:flex;gap:8px;margin-top:12px">
      <button class="btn btn-sm" onclick="doGenerate('${_generatePkg}')">⚡ GENERATE ZIP</button>
      <button class="btn-ghost" style="padding:4px 10px;font-size:8px" onclick="doPreview('${_generatePkg}')">↺ Refresh Preview</button>
    </div>`;
  if (window.hljs) try { hljs.highlightElement(document.getElementById('preview-code')); } catch(e) {}
}

function switchPreview(i) {
  _previewIdx = i;
  renderPreview();
}

async function doGenerate(pkg) {
  var checked = getSelectedFeatures();
  if (!checked.length) { showToast('Select at least one feature', 'warn'); return; }
  var slug = document.getElementById('slug-input')?.value.trim() || pkg.replace(/-/g,'_');
  var out  = document.getElementById('out-panel');
  out.innerHTML = `<h3>OUTPUT</h3>
    <div class="loading">Generating…</div>
    <div class="progress-wrap"><div class="progress-bar" id="gen-pb" style="width:30%"></div></div>`;
  var pb = document.getElementById('gen-pb');
  var pbInterval = setInterval(() => {
    if (pb) { var w = parseInt(pb.style.width); pb.style.width = Math.min(w+10,90)+'%'; }
  }, 300);
  try {
    var d = await apiFetch('generate', {package: pkg, features: checked.join(','), slug});
    clearInterval(pbInterval);
    if (d.error) { out.innerHTML = `<h3>OUTPUT</h3><div class="err-box">${d.error}</div>`; return; }
    out.innerHTML = `
      <h3>OUTPUT</h3>
      <div class="ok-box">✅ ${d.slug} — ${d.file_count} files generated</div>
      <div style="margin:12px 0">
        ${(d.files_created||[]).map(f=>`<div style="font-size:10px;color:var(--green);padding:2px 0">✓ ${f}</div>`).join('')}
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <a class="btn" href="${window.PB}/download/${d.zip_name}" download="${d.zip_name}">⬇ DOWNLOAD ZIP</a>
        <button class="btn-ghost" onclick="quickInstall('${d.slug}',this)">⚡ INSTALL NOW</button>
        <button class="btn-ghost" onclick="doPreview('${pkg}')">👁 Preview Code</button>
        <button class="btn-ghost" onclick="switchTab('generated-list')">📁 Generated List</button>
      </div>
      <div class="info-box" style="margin-top:12px;font-size:10px">
        💡 Upload the zip to MasterChief's addon manager, or <strong>INSTALL NOW</strong> to copy directly.
      </div>`;
    refreshBadges();
    showToast(`✅ ${d.slug} generated`, 'ok');
  } catch(e) {
    clearInterval(pbInterval);
    out.innerHTML = `<h3>OUTPUT</h3><div class="err-box">Error: ${e.message}</div>`;
    showToast('Generate failed: ' + e.message, 'err');
  }
}

async function quickInstall(slug, btn) {
  if (btn) { btn.textContent='Installing…'; btn.disabled=true; }
  try {
    var d = await apiFetch('install', {slug});
    if (d.success) {
      if (btn) btn.textContent='✅ Installed';
      showToast(d.message, 'ok');
      refreshBadges();
    } else {
      if (btn) btn.textContent='❌ Failed';
      showToast(d.error, 'err');
    }
  } catch(e) {
    if (btn) btn.textContent='❌ Error';
    showToast(e.message, 'err');
  }
  if (btn) setTimeout(() => { btn.disabled=false; btn.textContent='⚡ INSTALL NOW'; }, 3000);
}

// ══════════════════════════════════════════════════════════════
//  MODULES (merged installed + registry + live status + notes)
// ══════════════════════════════════════════════════════════════
var _modData   = [];
var _modNotes  = {};
var _modStatus = {};
var _selected  = new Set();
var _modFilter = '';

async function loadModules() {
  var c = document.getElementById('content');
  c.innerHTML = `
    <div class="batch-bar hidden" id="batch-bar">
      <span class="batch-count" id="batch-count">0 selected</span>
      <button class="btn btn-sm" onclick="batchRemove()">🗑 Remove Selected</button>
      <button class="btn-ghost" style="padding:4px 10px;font-size:8px" onclick="clearSelection()">✕ Deselect All</button>
    </div>
    <div class="page-head">
      <div class="page-title">🗂 <em>MODULES</em></div>
      <div class="page-sub">All installed addons — live status, notes, batch operations</div>
    </div>
    <div class="search-row">
      <input id="mod-search" type="text" placeholder="Search modules…" oninput="filterMods(this.value)"/>
      <button class="btn-ghost" onclick="loadModules()">↺ Refresh</button>
      <button class="btn-ghost" onclick="doDiscover()">Sync Registry</button>
    </div>
    <div class="stat-row" id="mod-stats"></div>
    <div class="mod-grid" id="mod-grid"><div class="loading">Loading…</div></div>
    <div id="file-viewer" style="margin-top:24px;display:none">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
        <div style="font-family:var(--ui);font-size:10px;font-weight:700" id="fv-title">FILES</div>
        <button class="btn-ghost" style="margin-left:auto;padding:3px 10px;font-size:8px" onclick="closeFileViewer()">✕ Close</button>
      </div>
      <div class="file-tree-panel">
        <div class="file-tree" id="fv-tree"></div>
        <div class="file-code-wrap">
          <div class="code-wrap">
            <pre class="hljs"><code id="fv-code" class="plaintext"></code></pre>
            <button class="code-copy" onclick="copyCode('fv-code')">COPY</button>
          </div>
        </div>
      </div>
    </div>`;

  try {
    var [inst, statuses, notes] = await Promise.all([
      apiFetch('installed'),
      apiFetch('status-all'),
      apiFetch('notes'),
    ]);
    _modData   = inst.modules || [];
    _modStatus = statuses.statuses || {};
    _modNotes  = notes || {};
    _selected  = new Set();

    document.getElementById('installed-badge').textContent = _modData.length;
    document.getElementById('mod-stats').innerHTML = `
      <div class="stat"><div class="stat-label">Total</div><div class="stat-val">${_modData.length}</div></div>
      <div class="stat" style="border-left-color:var(--green)">
        <div class="stat-label">Running</div>
        <div class="stat-val" style="color:var(--green)">${Object.values(_modStatus).filter(s=>s.status==='running').length}</div></div>
      <div class="stat" style="border-left-color:var(--blue)">
        <div class="stat-label">Blueprint</div>
        <div class="stat-val" style="color:var(--blue)">${Object.values(_modStatus).filter(s=>s.status==='blueprint').length}</div></div>
      <div class="stat" style="border-left-color:var(--purple)">
        <div class="stat-label">Generated</div>
        <div class="stat-val" style="color:var(--purple)">${_modData.filter(m=>m.is_generated).length}</div></div>`;

    renderModGrid(_modData);
  } catch(e) {
    document.getElementById('mod-grid').innerHTML = `<div class="err-box">Error: ${e.message}</div>`;
  }
}

function renderModGrid(mods) {
  var el = document.getElementById('mod-grid');
  if (!el) return;
  if (!mods.length) { el.innerHTML = '<div class="loading">No modules found</div>'; return; }
  el.innerHTML = mods.map(m => {
    var st   = _modStatus[m.slug] || {};
    var sCls = st.status==='running'?'running':st.status==='blueprint'?'blueprint':st.status==='stopped'?'stopped':'unknown';
    var note = _modNotes[m.slug];
    var srcBadge = m.source==='extracted'
      ? '<span class="tag tag-amber">extracted</span>'
      : '<span class="tag tag-blue">addons</span>';
    var typeBadge = m.is_blueprint
      ? '<span class="tag tag-blue">blueprint</span>'
      : m.is_generated
      ? '<span class="tag tag-green">generated</span>'
      : '<span class="tag" style="border-color:var(--border);color:var(--dim)">manual</span>';
    var proxyLink = st.proxy_url
      ? `<a href="${st.proxy_url}" target="_blank" class="btn-ghost" style="padding:4px 10px;font-size:8px;text-decoration:none">↗ Open</a>`
      : m.has_app || m.has_addon
      ? `<button class="btn-ghost" style="padding:4px 10px;font-size:8px" onclick="openModuleApp('${m.slug}','${m.is_blueprint?'blueprint':'subprocess'}')">↗ Open</button>`
      : '';
    return `<div class="mod-card ${_selected.has(m.slug)?'selected':''}" id="mc-${m.slug}" style="border-left-color:${m.color||'#f5a623'}">
      <input type="checkbox" class="mod-check" ${_selected.has(m.slug)?'checked':''} onchange="toggleSelect('${m.slug}',this.checked)"/>
      <div class="mod-card-head">
        <div class="mod-icon">${m.icon||'📦'}</div>
        <div style="flex:1;min-width:0">
          <div class="mod-title">${m.label||m.slug}</div>
          <div class="mod-slug">${m.slug} ${m.version?'v'+m.version:''}</div>
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:6px;margin-bottom:8px;flex-wrap:wrap">
        <span class="status-dot ${sCls}"></span>
        <span style="font-size:9px;color:var(--dim)">${st.status||'unknown'}${st.port?' :'+st.port:''}</span>
        ${srcBadge} ${typeBadge}
      </div>
      <div class="mod-meta">${m.file_count} files · ${m.size_kb}KB ${m.package?'· '+m.package:''}</div>
      ${note ? `<div class="note-text">📝 ${note.text}</div>` : ''}
      <div class="mod-actions">
        <button class="btn btn-sm" onclick="viewFiles('${m.slug}')">📄 Files</button>
        ${proxyLink}
        <button class="btn-ghost" style="padding:4px 10px;font-size:8px" onclick="openNoteModal('${m.slug}')">📝</button>
        <button class="btn-ghost" style="padding:4px 10px;font-size:8px" onclick="openEditModal('${m.slug}')">✏</button>
        <button class="btn-danger" style="padding:4px 10px;font-size:8px" onclick="removeModule('${m.slug}')">🗑</button>
      </div>
    </div>`;
  }).join('');
}

function openModuleApp(slug, type) {
  var url = type === 'blueprint'
    ? `/modules/${slug}/`
    : `/addons/modules/${slug}/app/`;
  window.open(url, '_blank');
}

function filterMods(q) {
  _modFilter = q.toLowerCase();
  renderModGrid(_modFilter ? _modData.filter(m =>
    m.slug.toLowerCase().includes(_modFilter) ||
    (m.label||'').toLowerCase().includes(_modFilter) ||
    (m.package||'').toLowerCase().includes(_modFilter)
  ) : _modData);
}

function toggleSelect(slug, checked) {
  if (checked) _selected.add(slug); else _selected.delete(slug);
  var card = document.getElementById('mc-'+slug);
  if (card) card.classList.toggle('selected', checked);
  var bar = document.getElementById('batch-bar');
  var cnt = document.getElementById('batch-count');
  if (bar) bar.classList.toggle('hidden', _selected.size === 0);
  if (cnt) cnt.textContent = `${_selected.size} selected`;
}

function clearSelection() {
  _selected.clear();
  document.querySelectorAll('.mod-check').forEach(cb => cb.checked = false);
  document.querySelectorAll('.mod-card').forEach(el => el.classList.remove('selected'));
  var bar = document.getElementById('batch-bar');
  if (bar) bar.classList.add('hidden');
}

async function batchRemove() {
  if (!_selected.size) return;
  if (!confirm(`Remove ${_selected.size} module(s)? This cannot be undone.`)) return;
  var slugs = [..._selected];
  var results = await Promise.allSettled(slugs.map(s => apiFetch('remove', {slug:s})));
  var ok = results.filter(r => r.status==='fulfilled' && r.value?.success).length;
  showToast(`Removed ${ok}/${slugs.length} modules`, ok===slugs.length ? 'ok' : 'warn');
  loadModules();
}

var _currentFiles = [];
async function viewFiles(slug) {
  var fv = document.getElementById('file-viewer');
  fv.style.display = 'block';
  document.getElementById('fv-title').textContent = `📄 ${slug}`;
  var tree = document.getElementById('fv-tree');
  tree.innerHTML = '<div class="loading">Loading…</div>';
  document.getElementById('fv-code').textContent = '';
  fv.scrollIntoView({behavior:'smooth'});
  try {
    var d = await apiFetch('module-files', {slug});
    _currentFiles = d.files;
    tree.innerHTML = d.files.map((f,i) => `
      <div class="file-item ${i===0?'active':''}" onclick="showFile(${i})">
        <span class="file-ext">.${f.ext||'?'}</span>
        <span>${f.path}</span>
      </div>`).join('');
    if (d.files.length) showFileContent(d.files[0]);
  } catch(e) {
    tree.innerHTML = `<div class="err-box">${e.message}</div>`;
  }
}

function showFile(i) {
  document.querySelectorAll('.file-item').forEach((el,j) => el.classList.toggle('active', i===j));
  showFileContent(_currentFiles[i]);
}

function showFileContent(f) {
  var el = document.getElementById('fv-code');
  el.className = langClass(f.ext);
  el.textContent = f.content;
  if (window.hljs) try { hljs.highlightElement(el); } catch(e) {}
}

function closeFileViewer() {
  document.getElementById('file-viewer').style.display = 'none';
}

async function removeModule(slug) {
  if (!confirm(`Remove "${slug}"? This deletes the folder.`)) return;
  try {
    var d = await apiFetch('remove', {slug});
    if (d.success) { showToast(d.message, 'ok'); loadModules(); }
    else showToast(d.error, 'err');
  } catch(e) { showToast(e.message, 'err'); }
}

// Note modal
var _noteSlug = null;
function openNoteModal(slug) {
  _noteSlug = slug;
  var existing = _modNotes[slug]?.text || '';
  showModal(`
    <div class="modal-title">📝 NOTE — ${slug}</div>
    <div class="modal-grid">
      <div>
        <div class="field-label">Note</div>
        <textarea id="note-text" rows="5" style="width:100%">${existing}</textarea>
      </div>
      <div style="display:flex;gap:8px">
        <button class="btn" style="flex:1" onclick="saveNote()">SAVE NOTE</button>
        <button class="btn-danger" style="flex:1" onclick="clearNote()">CLEAR</button>
        <button class="btn-ghost" onclick="closeModal()">Cancel</button>
      </div>
    </div>`);
}

async function saveNote() {
  var text = document.getElementById('note-text')?.value.trim();
  try {
    var d = await apiPost('notes', {slug: _noteSlug, note: text});
    if (d.success) { showToast('Note saved', 'ok'); closeModal(); loadModules(); }
    else showToast(d.error, 'err');
  } catch(e) { showToast(e.message, 'err'); }
}

async function clearNote() {
  try {
    var d = await apiPost('notes', {slug: _noteSlug, note: ''});
    if (d.success) { showToast('Note cleared', 'ok'); closeModal(); loadModules(); }
  } catch(e) { showToast(e.message, 'err'); }
}

// Edit manifest modal (reused from registry)
var _editSlug = null;
function openEditModal(slug) {
  _editSlug = slug;
  var m = _modData.find(x => x.slug===slug) || {};
  var cats = Object.entries({
    admin_ops:'Admin Ops', addons:'Add Ons', sys_modules:'System Modules',
    integrations:'Integrations', devtools:'Dev Tools', data:'Data & Analytics',
    security:'Security', cloud:'Cloud & Infra', uncategorized:'Other'
  }).map(([v,l]) => `<option value="${v}" ${m.category===v?'selected':''}>${l}</option>`).join('');
  showModal(`
    <div class="modal-title">✏ EDIT MANIFEST — ${slug}</div>
    <div class="modal-grid">
      <div><div class="field-label">Label</div><input id="ef-label" value="${m.label||slug}" style="width:100%"/></div>
      <div><div class="field-label">Icon</div><input id="ef-icon" value="${m.icon||'📦'}" style="width:80px"/></div>
      <div><div class="field-label">Color</div><input id="ef-color" type="color" value="${m.color||'#f5a623'}"/></div>
      <div><div class="field-label">Category</div><select id="ef-cat" style="width:100%">${cats}</select></div>
      <div><div class="field-label">Description</div><input id="ef-desc" value="${(m.description||'').replace(/"/g,'&quot;')}" style="width:100%"/></div>
      <div><div class="field-label">Capabilities (comma-sep)</div><input id="ef-caps" value="" style="width:100%"/></div>
      <div><div class="field-label">Requires (comma-sep)</div><input id="ef-reqs" value="" style="width:100%"/></div>
      <div style="display:flex;gap:8px;margin-top:4px">
        <button class="btn" style="flex:1" onclick="saveManifest()">SAVE</button>
        <button class="btn-ghost" onclick="closeModal()">Cancel</button>
      </div>
    </div>`);
}

async function saveManifest() {
  var params = {
    slug:         _editSlug,
    label:        document.getElementById('ef-label')?.value,
    icon:         document.getElementById('ef-icon')?.value,
    color:        document.getElementById('ef-color')?.value,
    category:     document.getElementById('ef-cat')?.value,
    description:  document.getElementById('ef-desc')?.value,
    capabilities: document.getElementById('ef-caps')?.value,
    requires:     document.getElementById('ef-reqs')?.value,
  };
  try {
    var d = await apiFetch('update-manifest', params);
    if (d.success) { showToast('Manifest saved', 'ok'); closeModal(); loadModules(); }
    else showToast(d.error, 'err');
  } catch(e) { showToast(e.message, 'err'); }
}

// ══════════════════════════════════════════════════════════════
//  GENERATED LIST
// ══════════════════════════════════════════════════════════════
var _genList = [];

async function loadGeneratedList() {
  var c = document.getElementById('content');
  c.innerHTML = `
    <div class="page-head">
      <div class="page-title">📁 <em>GENERATED</em></div>
      <div class="page-sub">Zips created by this Module Command Center — install or download</div>
    </div>
    <div class="gen-list" id="gen-list"><div class="loading">Loading…</div></div>`;
  try {
    var d = await apiFetch('generated');
    _genList = d || [];
    document.getElementById('gen-badge').textContent = _genList.length;
    var el = document.getElementById('gen-list');
    if (!_genList.length) {
      el.innerHTML = '<div class="info-box">No generated modules yet — go to Marketplace to create one.</div>';
      return;
    }
    el.innerHTML = `
      <div style="display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid var(--border);
        font-size:8px;color:var(--dim);letter-spacing:.18em">
        <span style="flex:1">MODULE</span><span style="width:70px">SIZE</span>
        <span style="width:80px">AGE</span><span style="width:220px">ACTIONS</span>
      </div>
      ${_genList.map(z => `
      <div class="gen-row">
        <div class="gen-row-name">📦 ${z.slug}</div>
        <div class="gen-row-size">${(z.size/1024).toFixed(1)} KB</div>
        <div class="gen-row-size">${timeAgo(z.mtime)}</div>
        <div style="display:flex;gap:6px">
          <button class="btn btn-sm" onclick="installGen('${z.slug}',this)">⚡ INSTALL</button>
          <a class="btn-ghost" style="padding:4px 10px;font-size:8px;text-decoration:none"
             href="${window.PB}/download/${z.zip_name}" download="${z.zip_name}">⬇ ZIP</a>
          <button class="btn-danger" style="padding:4px 10px;font-size:8px"
                  onclick="deleteGen('${z.slug}',this)">🗑</button>
        </div>
      </div>`).join('')}`;
  } catch(e) {
    document.getElementById('gen-list').innerHTML = `<div class="err-box">${e.message}</div>`;
  }
}

async function installGen(slug, btn) {
  btn.textContent='…'; btn.disabled=true;
  try {
    var d = await apiFetch('install', {slug});
    if (d.success) { showToast(d.message, 'ok'); refreshBadges(); btn.textContent='✅'; }
    else { showToast(d.error, 'err'); btn.textContent='❌'; }
  } catch(e) { showToast(e.message,'err'); btn.textContent='❌'; }
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

// ══════════════════════════════════════════════════════════════
//  PIP MANAGER
// ══════════════════════════════════════════════════════════════
async function loadPip() {
  var c = document.getElementById('content');
  c.innerHTML = `
    <div class="page-head">
      <div class="page-title">🐍 <em>PIP</em> MANAGER</div>
      <div class="page-sub">Install new packages — they'll appear in the Marketplace for module generation</div>
    </div>
    <div style="max-width:700px">
      <div class="field-label" style="margin-bottom:6px">INSTALL PACKAGE</div>
      <div style="display:flex;gap:8px;margin-bottom:12px">
        <input id="pip-input" type="text" placeholder="e.g. kubernetes, docker, boto3, psutil"
               style="flex:1" onkeydown="if(event.key==='Enter')doPipInstall()"/>
        <button class="btn" onclick="doPipInstall()">INSTALL</button>
        <button class="btn-ghost" onclick="doPypiSearch()">🔍 SEARCH</button>
      </div>
      <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:20px">
        ${['kubernetes','docker','boto3','psutil','redis','paramiko','celery','requests','pandas','sqlalchemy','fastapi','pydantic','httpx','rich','typer']
          .map(p => `<button class="btn-ghost" style="padding:4px 10px;font-size:8px" onclick="pipInstallQuick('${p}')">${p}</button>`).join('')}
      </div>
      <div id="pip-output"></div>
      <div id="pypi-search-results" style="margin-top:16px"></div>
    </div>`;
}

async function doPipInstall() {
  var pkg = document.getElementById('pip-input')?.value.trim();
  if (!pkg) return;
  var out = document.getElementById('pip-output');
  out.innerHTML = `
    <div class="info-box">Installing ${pkg}…</div>
    <div class="progress-wrap"><div class="progress-bar" id="pip-pb" style="width:15%"></div></div>`;
  var pb = document.getElementById('pip-pb');
  var pbI = setInterval(() => { if (pb) { var w=parseInt(pb.style.width); pb.style.width=Math.min(w+8,90)+'%'; }}, 400);
  try {
    var d = await apiFetch('pip-install', {package: pkg});
    clearInterval(pbI);
    if (d.success) {
      out.innerHTML = `
        <div class="ok-box">✅ ${pkg} installed successfully</div>
        <div class="log-terminal">${(d.output||'').split('\n').map(l=>`<div class="log-line ${logClass(l)}">${escHtml(l)}</div>`).join('')}</div>
        <div style="display:flex;gap:8px;margin-top:12px">
          <button class="btn" onclick="openGenerate('${pkg}')">⚡ Generate Module</button>
          <button class="btn-ghost" onclick="switchTab('marketplace')">View in Marketplace</button>
        </div>`;
      showToast(`✅ ${pkg} installed`, 'ok');
      refreshBadges();
    } else {
      out.innerHTML = `
        <div class="err-box">❌ Install failed</div>
        <div class="log-terminal">${(d.output||d.error||'').split('\n').map(l=>`<div class="log-line log-err">${escHtml(l)}</div>`).join('')}</div>`;
      showToast(`Install failed: ${pkg}`, 'err');
    }
  } catch(e) {
    clearInterval(pbI);
    out.innerHTML = `<div class="err-box">Error: ${e.message}</div>`;
  }
}

function pipInstallQuick(pkg) {
  document.getElementById('pip-input').value = pkg;
  doPipInstall();
}

async function doPypiSearch() {
  var q = document.getElementById('pip-input')?.value.trim();
  if (!q) return;
  var el = document.getElementById('pypi-search-results');
  el.innerHTML = '<div class="loading">Searching PyPI…</div>';
  try {
    var [pypiInfo] = await Promise.all([apiFetch('pypi-info', {package: q})]);
    if (pypiInfo.error) {
      el.innerHTML = `<div class="err-box">${pypiInfo.error}</div>`;
      return;
    }
    el.innerHTML = `
      <div class="pypi-panel">
        <div class="pypi-name">📦 ${pypiInfo.name} <span style="color:var(--dim)">v${pypiInfo.version}</span></div>
        <div class="pypi-summary">${pypiInfo.summary||'No description'}</div>
        <div class="pypi-meta-grid">
          ${pypiInfo.author ? `<div class="pypi-meta-key">Author</div><div class="pypi-meta-val">${pypiInfo.author}</div>` : ''}
          ${pypiInfo.license ? `<div class="pypi-meta-key">License</div><div class="pypi-meta-val">${pypiInfo.license}</div>` : ''}
          ${pypiInfo.requires_python ? `<div class="pypi-meta-key">Requires Python</div><div class="pypi-meta-val">${pypiInfo.requires_python}</div>` : ''}
          ${pypiInfo.releases ? `<div class="pypi-meta-key">Releases</div><div class="pypi-meta-val">${pypiInfo.releases}</div>` : ''}
        </div>
        <div style="display:flex;gap:8px;margin-top:12px">
          <button class="btn btn-sm" onclick="doPipInstall()">⬇ Install Now</button>
          <button class="btn-ghost" style="padding:4px 10px;font-size:8px" onclick="openGenerate('${q}')">⚡ Generate Module</button>
        </div>
      </div>`;
  } catch(e) {
    el.innerHTML = `<div class="err-box">${e.message}</div>`;
  }
}

// ══════════════════════════════════════════════════════════════
//  LOGS
// ══════════════════════════════════════════════════════════════
var _logAutoRefresh = false;
var _logTimer = null;

async function loadLogs() {
  var c = document.getElementById('content');
  c.innerHTML = `
    <div class="page-head">
      <div class="page-title">📋 <em>ADDON</em> LOGS</div>
      <div class="page-sub">View and search log output from installed addon modules</div>
    </div>
    <div style="display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap;align-items:center">
      <input id="log-slug" type="text" placeholder="module slug (leave blank for main log)" style="flex:1;min-width:200px"/>
      <input id="log-lines" type="number" value="200" style="width:70px"/>
      <button class="btn" onclick="fetchLogs()">VIEW LOGS</button>
      <label class="refresh-toggle" onclick="toggleLogRefresh()">
        <div class="toggle-pill" id="log-pill"></div> Auto-refresh
      </label>
    </div>
    <div style="display:flex;gap:8px;margin-bottom:12px">
      <input id="log-filter" type="text" placeholder="Filter log lines…" oninput="applyLogFilter(this.value)" style="flex:1"/>
      <button class="btn-ghost" onclick="clearLogFilter()">Clear</button>
    </div>
    <div id="log-meta" style="font-size:9px;color:var(--dim);margin-bottom:8px"></div>
    <div id="log-out"></div>`;
}

var _rawLogLines = [];
async function fetchLogs() {
  var slug  = document.getElementById('log-slug')?.value.trim();
  var lines = document.getElementById('log-lines')?.value || 200;
  var out   = document.getElementById('log-out');
  out.innerHTML = '<div class="loading">Loading logs…</div>';
  try {
    var d = await apiFetch('addon-logs', {slug, lines});
    _rawLogLines = d.lines || [];
    var meta = document.getElementById('log-meta');
    if (meta) meta.textContent = `Source: ${d.source||'n/a'}  ·  ${_rawLogLines.length} lines (of ${d.total||0} total)`;
    renderLogLines(_rawLogLines);
  } catch(e) {
    out.innerHTML = `<div class="err-box">Error: ${e.message}</div>`;
  }
}

function renderLogLines(lines) {
  var out = document.getElementById('log-out');
  if (!out) return;
  var html = lines.map(l => `<div class="log-line ${logClass(l)}">${escHtml(l)}</div>`).join('');
  out.innerHTML = html
    ? `<div class="log-terminal" id="log-terminal">${html}</div>`
    : '<div class="info-box">No log lines</div>';
  // Scroll to bottom
  var t = document.getElementById('log-terminal');
  if (t) t.scrollTop = t.scrollHeight;
}

function applyLogFilter(q) {
  if (!q) { renderLogLines(_rawLogLines); return; }
  q = q.toLowerCase();
  renderLogLines(_rawLogLines.filter(l => l.toLowerCase().includes(q)));
}

function clearLogFilter() {
  var el = document.getElementById('log-filter');
  if (el) { el.value=''; applyLogFilter(''); }
}

function toggleLogRefresh() {
  _logAutoRefresh = !_logAutoRefresh;
  var pill = document.getElementById('log-pill');
  if (pill) pill.classList.toggle('on', _logAutoRefresh);
  if (_logAutoRefresh) {
    showToast('Log auto-refresh ON (5s)', 'info');
    _logTimer = setInterval(fetchLogs, 5000);
  } else {
    clearInterval(_logTimer);
    showToast('Log auto-refresh OFF', 'info');
  }
}

// ══════════════════════════════════════════════════════════════
//  NETWORK GRAPH (D3)
// ══════════════════════════════════════════════════════════════
async function loadNetwork() {
  var c = document.getElementById('content');
  c.innerHTML = `
    <div class="page-head">
      <div class="page-title">🕸 <em>CAPABILITY</em> NETWORK</div>
      <div class="page-sub">Force-directed graph of module capabilities and dependencies</div>
    </div>
    <div style="display:flex;gap:8px;margin-bottom:14px">
      <button class="btn-ghost" onclick="loadNetwork()">↺ Refresh</button>
      <div style="font-size:9px;color:var(--dim);align-self:center;margin-left:8px">
        <span style="color:var(--amber)">●</span> Module  
        <span style="color:var(--green)">●</span> Capability  
        <span style="color:var(--blue)">─</span> Provides  
        <span style="color:var(--red)">─</span> Requires
      </div>
    </div>
    <svg id="graph-svg"></svg>
    <div id="graph-legend" style="margin-top:12px;font-size:9px;color:var(--dim)">
      Drag nodes to rearrange · Scroll to zoom · Click to highlight
    </div>`;

  try {
    var reg = await apiFetch('registry');
    buildGraph(reg);
  } catch(e) {
    document.getElementById('graph-svg').outerHTML = `<div class="err-box">${e.message}</div>`;
  }
}

function buildGraph(reg) {
  var mods = reg.modules || {};
  var nodes = [], links = [];
  var nodeMap = {};

  // Module nodes
  for (var [slug, m] of Object.entries(mods)) {
    var n = {id:'mod:'+slug, label:m.label||slug, type:'module', color:m.color||'#f5a623', icon:m.icon||'📦'};
    nodes.push(n);
    nodeMap['mod:'+slug] = n;
  }

  // Capability nodes + links
  for (var [slug, m] of Object.entries(mods)) {
    for (var cap of (m.capabilities||[])) {
      var cid = 'cap:'+cap;
      if (!nodeMap[cid]) {
        var cn = {id:cid, label:cap, type:'capability', color:'#00e676'};
        nodes.push(cn); nodeMap[cid] = cn;
      }
      links.push({source:'mod:'+slug, target:cid, type:'provides'});
    }
    for (var req of (m.requires||[])) {
      var rid = 'cap:'+req;
      if (!nodeMap[rid]) {
        var rn = {id:rid, label:req, type:'capability', color:'#00e676'};
        nodes.push(rn); nodeMap[rid] = rn;
      }
      links.push({source:'mod:'+slug, target:rid, type:'requires'});
    }
  }

  if (!nodes.length) {
    document.getElementById('graph-legend').innerHTML = '<div class="info-box">No modules or capabilities found. Add capabilities via the Modules panel.</div>';
    return;
  }

  var svg    = d3.select('#graph-svg');
  var width  = svg.node().getBoundingClientRect().width || 800;
  var height = 500;

  svg.attr('viewBox', `0 0 ${width} ${height}`);

  var g = svg.append('g');

  // Zoom
  svg.call(d3.zoom().scaleExtent([0.3, 3]).on('zoom', e => g.attr('transform', e.transform)));

  var sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(100))
    .force('charge', d3.forceManyBody().strength(-200))
    .force('center', d3.forceCenter(width/2, height/2))
    .force('collision', d3.forceCollide(30));

  var link = g.append('g').selectAll('line').data(links).join('line')
    .attr('class', 'graph-link')
    .attr('stroke', d => d.type==='provides' ? '#58a6ff' : '#ff4444')
    .attr('stroke-dasharray', d => d.type==='requires' ? '4,2' : null);

  var node = g.append('g').selectAll('.graph-node').data(nodes).join('g')
    .attr('class', 'graph-node')
    .call(d3.drag()
      .on('start', (e,d) => { if (!e.active) sim.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; })
      .on('drag',  (e,d) => { d.fx=e.x; d.fy=e.y; })
      .on('end',   (e,d) => { if (!e.active) sim.alphaTarget(0); d.fx=null; d.fy=null; })
    )
    .on('click', (e,d) => highlightNode(d, link, node));

  node.append('circle')
    .attr('r', d => d.type==='module' ? 18 : 12)
    .attr('fill', d => d.color + '22')
    .attr('stroke', d => d.color)
    .attr('stroke-width', 2);

  node.append('text')
    .attr('text-anchor', 'middle').attr('dy', d => d.type==='module' ? 4 : 4)
    .attr('font-size', d => d.type==='module' ? 12 : 8)
    .text(d => d.type==='module' ? (d.icon||'📦') : '◉');

  node.append('text')
    .attr('text-anchor', 'middle').attr('dy', d => d.type==='module' ? 30 : 24)
    .attr('font-size', 9).attr('fill', '#7a9ab0')
    .text(d => d.label.slice(0,14));

  // Tooltip
  var tooltip = d3.select('body').append('div').attr('class', 'graph-tooltip').style('display','none');
  node.on('mouseover', (e,d) => {
    tooltip.style('display','block')
      .style('left', e.clientX+12+'px').style('top', e.clientY-10+'px')
      .html(`<strong>${d.label}</strong><br><span style="color:var(--dim)">${d.type}</span>${d.color?`<br><span style="color:${d.color}">●</span>`:''}`)
  }).on('mousemove', e => {
    tooltip.style('left', e.clientX+12+'px').style('top', e.clientY-10+'px');
  }).on('mouseout', () => tooltip.style('display','none'));

  sim.on('tick', () => {
    link.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y)
        .attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);
    node.attr('transform', d => `translate(${d.x},${d.y})`);
  });

  // cleanup tooltip on tab switch
  window._graphTooltip = tooltip;
}

function highlightNode(d, link, node) {
  node.selectAll('circle').attr('opacity', n =>
    n.id===d.id ? 1 : 0.3);
  link.attr('opacity', l =>
    l.source.id===d.id || l.target.id===d.id ? 1 : 0.1);
  setTimeout(() => {
    node.selectAll('circle').attr('opacity', 1);
    link.attr('opacity', 1);
  }, 2500);
}

// ══════════════════════════════════════════════════════════════
//  PLATFORM
// ══════════════════════════════════════════════════════════════
var _registry = null;

async function loadPlatform() {
  var c = document.getElementById('content');
  c.innerHTML = `
    <div class="page-head">
      <div class="page-title">⚙ <em>PLATFORM</em></div>
      <div class="page-sub">Capability bus, nav injection, registry management, export</div>
    </div>
    <div style="display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap">
      <button class="btn" onclick="doDiscover()">↺ Re-discover All</button>
      <button class="btn-ghost" onclick="copyNavSnippet()">📋 Copy main.py Hook</button>
      <button class="btn-ghost" onclick="exportRegistry()">⬇ Export Registry JSON</button>
      <button class="btn-ghost" onclick="switchTab('network')">🕸 Capability Graph</button>
    </div>
    <div id="reg-stats" class="stat-row"></div>
    <div class="platform-grid">
      <div>
        <div class="dash-card">
          <h3>⚡ Capability Bus</h3>
          <div id="cap-bus"><div class="loading">Loading…</div></div>
        </div>
      </div>
      <div>
        <div class="dash-card">
          <h3>🧩 Nav Sections Preview</h3>
          <div id="nav-preview"><div class="loading">Loading…</div></div>
        </div>
      </div>
    </div>
    <div style="margin-top:16px" class="dash-card">
      <h3>📋 main.py Integration Snippet</h3>
      <div class="snippet-box" id="snippet-box"></div>
      <div style="display:flex;gap:8px;margin-top:10px">
        <button class="btn" onclick="copyNavSnippet()">📋 Copy Snippet</button>
      </div>
    </div>
    <div style="margin-top:16px">
      <div class="field-label" style="margin-bottom:8px">ALL REGISTERED MODULES</div>
      <div id="reg-cats"></div>
    </div>`;

  try {
    var [reg, caps, nav] = await Promise.all([
      apiFetch('registry'),
      apiFetch('capabilities'),
      apiFetch('nav-sections'),
    ]);
    _registry = reg;
    var mods = reg.modules || {};
    var count = Object.keys(mods).length;

    document.getElementById('reg-stats').innerHTML = `
      <div class="stat"><div class="stat-label">Modules</div><div class="stat-val">${count}</div></div>
      <div class="stat" style="border-left-color:var(--green)">
        <div class="stat-label">Deps OK</div>
        <div class="stat-val" style="color:var(--green)">${Object.values(mods).filter(m=>m.deps_ok!==false).length}</div></div>
      <div class="stat" style="border-left-color:var(--amber)">
        <div class="stat-label">Launchable</div>
        <div class="stat-val" style="color:var(--amber)">${Object.values(mods).filter(m=>m.launchable).length}</div></div>
      <div class="stat" style="border-left-color:var(--blue)">
        <div class="stat-label">Nav Sections</div>
        <div class="stat-val" style="color:var(--blue)">${(nav.sections||[]).length}</div></div>`;

    // Cap bus
    var capHtml = Object.entries(caps).length
      ? Object.entries(caps).sort().map(([cap, providers]) => `
          <div style="display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:1px solid rgba(26,37,53,.5)">
            <div style="flex:1;font-size:10px;color:var(--amber)">⚡ ${cap}</div>
            <div>${providers.map(p=>`<span class="tag tag-blue">${p}</span>`).join(' ')}</div>
          </div>`).join('')
      : '<div class="info-box">No capabilities declared. Edit modules to add capabilities.</div>';
    document.getElementById('cap-bus').innerHTML = capHtml;

    // Nav preview
    var sections = nav.sections || [];
    document.getElementById('nav-preview').innerHTML = sections.length
      ? sections.map(s => `
          <div style="margin-bottom:8px;padding:8px;background:var(--card2);border:1px solid var(--border);border-radius:var(--r)">
            <div style="font-size:10px;font-weight:700;color:var(--amber);margin-bottom:4px">${s.icon} ${s.label}</div>
            ${s.items.map(i=>`<div style="font-size:10px;color:var(--mid);padding:2px 0 2px 12px">${i.icon} ${i.label}
              <span style="font-size:8px;color:var(--dim)"> — ${i.url}</span>
            </div>`).join('')}
          </div>`).join('')
      : '<div class="info-box">No nav sections yet</div>';

    // Snippet
    document.getElementById('snippet-box').innerHTML =
      `<span class="cm"># Paste after: app = Flask(__name__)</span>\n` +
      `<span class="kw">import</span> json <span class="kw">as</span> _json\n` +
      `<span class="kw">from</span> pathlib <span class="kw">import</span> Path <span class="kw">as</span> _Path\n\n` +
      `_REGISTRY_PATH = _Path(__file__).parent / <span class="str">'addons'</span> / <span class="str">'registry.json'</span>\n\n` +
      `<span class="kw">@app</span>.route(<span class="str">'/api/registry'</span>)\n` +
      `<span class="kw">def</span> api_module_registry():\n` +
      `    <span class="kw">if</span> _REGISTRY_PATH.exists():\n` +
      `        <span class="kw">return</span> jsonify(_json.loads(_REGISTRY_PATH.read_text()))\n` +
      `    <span class="kw">return</span> jsonify({<span class="str">'modules'</span>: {}})\n\n` +
      `<span class="kw">@app</span>.route(<span class="str">'/api/nav-sections'</span>)\n` +
      `<span class="kw">def</span> api_nav_sections():\n` +
      `    <span class="kw">if</span> _REGISTRY_PATH.exists():\n` +
      `        data = _json.loads(_REGISTRY_PATH.read_text())\n` +
      `        <span class="kw">return</span> jsonify({<span class="str">'sections'</span>: data.get(<span class="str">'_nav_sections'</span>, [])})\n` +
      `    <span class="kw">return</span> jsonify({<span class="str">'sections'</span>: []})`;

    // Modules by category
    var cats = {};
    for (var [slug, m] of Object.entries(mods)) {
      var cat = m.category||'uncategorized';
      if (!cats[cat]) cats[cat] = [];
      cats[cat].push({slug, ...m});
    }
    var CAT_COLORS = {
      admin_ops:'#f5a623', addons:'#58a6ff', sys_modules:'#a78bfa',
      integrations:'#00e676', devtools:'#38bdf8', data:'#fb7185',
      security:'#ff4444', cloud:'#34d399', uncategorized:'#4a6070'
    };
    document.getElementById('reg-cats').innerHTML = Object.entries(cats).map(([catId, items]) => `
      <div style="margin-bottom:20px">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid var(--border)">
          <div style="font-family:var(--ui);font-size:10px;font-weight:700;color:${CAT_COLORS[catId]||'#4a6070'}">${catId.toUpperCase().replace('_',' ')}</div>
          <span class="tag" style="color:var(--dim);border-color:var(--border)">${items.length}</span>
        </div>
        <div class="mod-grid">
          ${items.map(m => `
            <div class="mod-card" style="border-left-color:${m.color||CAT_COLORS[catId]}">
              <div class="mod-card-head">
                <div class="mod-icon">${m.icon||'📦'}</div>
                <div style="flex:1;min-width:0">
                  <div class="mod-title">${m.label||m.slug}</div>
                  <div class="mod-slug">${m.slug} ${m.version?'v'+m.version:''}</div>
                </div>
              </div>
              <div style="margin-bottom:6px">
                ${m._source==='manifest'?'<span class="tag tag-green">manifest</span>':m._source==='plugin_meta'?'<span class="tag tag-blue">plugin_meta</span>':'<span class="tag" style="color:var(--dim);border-color:var(--border)">filesystem</span>'}
                ${m.loader_type==='blueprint'?'<span class="tag tag-purple">blueprint</span>':m.loader_type==='subprocess'?'<span class="tag tag-amber">subprocess</span>':''}
                ${m.broken_deps?.length?`<span class="tag tag-red">⚠ deps</span>`:''}
              </div>
              ${m.description?`<div class="mod-meta">${m.description.slice(0,90)}</div>`:''}
              ${(m.capabilities||[]).length?`<div style="margin-top:4px">${m.capabilities.map(c=>`<span class="tag tag-amber">${c}</span>`).join(' ')}</div>`:''}
              <div class="mod-actions" style="margin-top:8px">
                <button class="btn btn-sm" onclick="openEditModal('${m.slug}')">✏ Edit</button>
                ${m.has_app?`<button class="btn-ghost" style="padding:4px 10px;font-size:8px" onclick="window.open('/addons/modules/${m.slug}/app','_blank')">↗</button>`:''}
              </div>
            </div>`).join('')}
        </div>
      </div>`).join('') || '<div class="loading">No modules found</div>';

  } catch(e) {
    c.innerHTML += `<div class="err-box">${e.message}</div>`;
  }
}

async function doDiscover() {
  showToast('Discovering modules…', 'info');
  try {
    var d = await apiFetch('write-registry');
    showToast(`Registry updated — ${d.count} modules`, 'ok');
    if (_tab === 'platform') loadPlatform();
    else if (_tab === 'modules') loadModules();
    refreshBadges();
  } catch(e) { showToast(e.message, 'err'); }
}

function exportRegistry() {
  window.location.href = window.PB + '/api/export-registry';
  showToast('Downloading registry export…', 'info');
}

function copyNavSnippet() {
  var snippet = `# Paste after app = Flask(__name__) in main.py
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
    () => showToast('Copy failed', 'err')
  );
}

// ══════════════════════════════════════════════════════════════
//  MODAL
// ══════════════════════════════════════════════════════════════
function showModal(html) {
  closeModal();
  var overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.id = 'modal-overlay';
  overlay.innerHTML = `<div class="modal-box">${html}</div>`;
  overlay.addEventListener('click', e => { if (e.target===overlay) closeModal(); });
  document.body.appendChild(overlay);
}
function closeModal() {
  var el = document.getElementById('modal-overlay');
  if (el) el.remove();
}

// ══════════════════════════════════════════════════════════════
//  UTILITIES
// ══════════════════════════════════════════════════════════════
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

function logClass(l) {
  l = (l||'').toLowerCase();
  if (l.includes('error') || l.includes('exception') || l.includes('traceback') || l.includes('failed')) return 'log-err';
  if (l.includes('warn')) return 'log-warn';
  if (l.includes('start') || l.includes('success') || l.includes('ok') || l.includes('installed')) return 'log-ok';
  return '';
}

function langClass(ext) {
  var map = {py:'python',js:'javascript',html:'html',css:'css',json:'json',
             md:'markdown',yaml:'yaml',yml:'yaml',sh:'bash',txt:'plaintext'};
  return 'language-' + (map[ext] || 'plaintext');
}

function copyCode(id) {
  var el = document.getElementById(id);
  if (el) navigator.clipboard.writeText(el.textContent).then(
    () => showToast('Copied', 'ok', 1500),
    () => showToast('Copy failed', 'err')
  );
}

async function refreshBadges() {
  try {
    var [inst, gen, pkgs] = await Promise.all([
      apiFetch('installed'), apiFetch('generated'), apiFetch('packages')
    ]);
    var ib = document.getElementById('installed-badge');
    var gb = document.getElementById('gen-badge');
    var pb = document.getElementById('pkg-badge');
    if (ib) ib.textContent = (inst.modules||[]).length;
    if (gb) gb.textContent = (gen||[]).length;
    if (pb) pb.textContent = (pkgs.packages||[]).length;
  } catch(e) {}
}

// ── Boot ──────────────────────────────────────────────────────
window.addEventListener('load', function() {
  if (window._graphTooltip) try { window._graphTooltip.remove(); } catch(e) {}
  renderTab('dashboard');
  refreshBadges();
});
</script>
</body></html>"""


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9100))
    print(f'[Module Center v4] Starting on http://localhost:{port}', flush=True)
    app.run(host='0.0.0.0', port=port, debug=False)
