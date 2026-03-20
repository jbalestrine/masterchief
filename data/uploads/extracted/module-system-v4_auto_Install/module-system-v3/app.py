"""
Module System v3 — MasterChief Addon
Marketplace + Generator + Installer

Proxy routing rules (CRITICAL):
  - PROXY_BASE = /addons/modules/{folder-name}/app
  - ALL HTML links use PROXY_BASE — never absolute ports
  - ALL fetch() calls use PROXY_BASE — never window.location
  - ALL Flask redirects use PROXY_BASE
  - NO url_for('static', ...) — inline all CSS/JS
"""
import os
import sys
import json
import zipfile
import tempfile
import importlib
import subprocess
from pathlib import Path
from flask import Flask, jsonify, request, redirect, Response

# ── Paths ────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
ADDON_NAME = os.environ.get('MC_ADDON_NAME', BASE_DIR.name)
PROXY_BASE = f'/addons/modules/{ADDON_NAME}/app'

OUTPUT_DIR = BASE_DIR / 'generated'
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Sub-modules ───────────────────────────────────────────────
sys.path.insert(0, str(BASE_DIR))
from introspector import introspect_package
from generator   import generate_module

app = Flask(__name__)

# ── Global JSON error handlers ────────────────────────────────
# Flask default error pages return HTML — always return JSON instead
@app.errorhandler(404)
def err404(e): return jsonify({'error': 'Not found', 'status': 404}), 404

@app.errorhandler(500)
def err500(e): return jsonify({'error': str(e), 'status': 500}), 500

@app.errorhandler(Exception)
def err_any(e): return jsonify({'error': str(e), 'status': 500}), 500

# ════════════════════════════════════════════════════════════
#  Pages — all hrefs and fetch() use PROXY_BASE
# ════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return marketplace_page()

@app.route('/generate/<package>')
def generate_page(package):
    return generate_page_html(package)

@app.route('/install')
def install_page():
    return install_page_html()

# ════════════════════════════════════════════════════════════
#  API — GET only (proxy only forwards GET)
# ════════════════════════════════════════════════════════════

@app.route('/api/packages')
def api_packages():
    """Return list of installed pip packages."""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list', '--format=json'],
            capture_output=True, text=True, timeout=15
        )
        pkgs = json.loads(result.stdout) if result.returncode == 0 else []
        return jsonify({'packages': pkgs, 'count': len(pkgs)})
    except Exception as e:
        return jsonify({'error': str(e), 'packages': []})

@app.route('/api/introspect')
def api_introspect():
    """Introspect a package and return its features."""
    package = request.args.get('package', '').strip()
    if not package:
        return jsonify({'error': 'package param required'}), 400
    try:
        result = introspect_package(package)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'features': []})

@app.route('/api/generate')
def api_generate():
    """
    Generate a module zip.
    Query params:
      package   — pip package name
      features  — comma-separated feature names to include
      slug      — optional output folder name
    """
    package  = request.args.get('package', '').strip()
    features = [f.strip() for f in request.args.get('features', '').split(',') if f.strip()]
    slug     = request.args.get('slug', '').strip() or package.replace('-', '_').replace('.', '_')

    if not package:
        return jsonify({'error': 'package param required'}), 400
    if not features:
        return jsonify({'error': 'features param required'}), 400

    try:
        result = generate_module(
            pip_name   = package,
            slug       = slug,
            features   = features,
            output_dir = OUTPUT_DIR,
        )
        if result.get('success'):
            # Return download URL using PROXY_BASE
            zip_name = Path(result['zip_path']).name
            result["zip_name"] = zip_name  # JS builds full URL from runtime PROXY_BASE
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    """Serve a generated zip for download."""
    # Safety: only serve files from OUTPUT_DIR
    safe = OUTPUT_DIR / Path(filename).name
    if not safe.exists() or safe.suffix != '.zip':
        return 'Not found', 404
    return Response(
        safe.read_bytes(),
        mimetype='application/zip',
        headers={'Content-Disposition': f'attachment; filename="{safe.name}"'}
    )

@app.route('/api/install')
def api_install():
    """Install a zip from a URL or from previously generated."""
    zip_url = request.args.get('url', '').strip()
    if not zip_url:
        return jsonify({'error': 'url param required'}), 400
    # Redirect to upload page with URL pre-filled
    return jsonify({'install_url': f'{PROXY_BASE}/install?zip_url={zip_url}'})

@app.route('/api/generated')
def api_generated():
    """List previously generated zips."""
    zips = sorted(OUTPUT_DIR.glob('*.zip'), key=lambda p: p.stat().st_mtime, reverse=True)
    return jsonify([{
        'name':     z.name,
        'size':     z.stat().st_size,
        'zip_name': z.name,
        'slug':     z.stem,
    } for z in zips])

# ════════════════════════════════════════════════════════════
#  HTML pages (inline CSS + JS, all URLs proxy-relative)
# ════════════════════════════════════════════════════════════

COMMON_CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#060809;--panel:#0a0d10;--card:#0e1419;--border:#1a2535;
  --amber:#f5a623;--green:#00ff88;--red:#ff4444;--blue:#58a6ff;
  --text:#cdd6e0;--dim:#4a6070;--mid:#7a9ab0;
  --mono:'Space Mono',monospace;--display:'Unbounded',sans-serif;
}
html,body{min-height:100vh;background:var(--bg);color:var(--text);font-family:var(--mono);font-size:13px}
a{color:inherit;text-decoration:none}
header{display:flex;align-items:center;gap:0;padding:0 32px;height:52px;
  background:var(--panel);border-bottom:1px solid var(--border);
  position:sticky;top:0;z-index:100}
.logo{font-family:var(--display);font-size:11px;font-weight:900;letter-spacing:.3em;margin-right:32px}
.logo span{color:var(--amber)}
nav{display:flex;gap:0}
.nav-link{padding:0 16px;height:52px;display:flex;align-items:center;
  font-size:11px;letter-spacing:.1em;color:var(--dim);border-bottom:2px solid transparent;
  cursor:pointer;transition:all .15s}
.nav-link:hover{color:var(--text)}
.nav-link.active{color:var(--amber);border-bottom-color:var(--amber)}
.spacer{flex:1}
.btn{background:var(--amber);color:#000;font-family:var(--mono);font-size:10px;font-weight:700;
  letter-spacing:.15em;padding:8px 18px;border:none;border-radius:2px;cursor:pointer;transition:background .15s}
.btn:hover{background:#ffc040}
.btn-ghost{background:transparent;color:var(--mid);font-family:var(--mono);font-size:10px;
  letter-spacing:.15em;padding:8px 16px;border:1px solid var(--border);border-radius:2px;
  cursor:pointer;transition:all .15s}
.btn-ghost:hover{border-color:var(--amber);color:var(--amber)}
main{max-width:1200px;margin:0 auto;padding:40px 32px}
h1{font-family:var(--display);font-size:clamp(24px,4vw,48px);font-weight:900;line-height:1;margin-bottom:8px}
h1 em{font-style:normal;-webkit-text-stroke:2px var(--amber);color:transparent}
.subtitle{color:var(--dim);font-size:12px;margin-bottom:32px}
input,select{background:var(--card);border:1px solid var(--border);color:var(--text);
  font-family:var(--mono);font-size:12px;padding:8px 12px;border-radius:2px;outline:none}
input:focus,select:focus{border-color:var(--amber)}
.tag{display:inline-flex;align-items:center;padding:2px 8px;border-radius:2px;
  font-size:10px;letter-spacing:.05em;border:1px solid}
.tag-blue{background:rgba(88,166,255,.1);color:var(--blue);border-color:rgba(88,166,255,.3)}
.tag-green{background:rgba(0,255,136,.1);color:var(--green);border-color:rgba(0,255,136,.3)}
.tag-amber{background:rgba(245,166,35,.1);color:var(--amber);border-color:rgba(245,166,35,.3)}
.tag-red{background:rgba(255,68,68,.1);color:var(--red);border-color:rgba(255,68,68,.3)}
.error-box{background:rgba(255,68,68,.05);border:1px solid rgba(255,68,68,.2);
  color:var(--red);padding:12px 16px;border-radius:2px;font-size:12px;margin:12px 0}
.success-box{background:rgba(0,255,136,.05);border:1px solid rgba(0,255,136,.2);
  color:var(--green);padding:12px 16px;border-radius:2px;font-size:12px;margin:12px 0}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
"""

def nav_html(active):
    # CRITICAL: nav links use PROXY_BASE, not absolute paths
    return f"""
<header>
  <div class="logo"><span>[</span>MODULE SYS<span>]</span></div>
  <nav>
    <div class="nav-link {'active' if active=='marketplace' else ''}"
         onclick="nav('')">MARKETPLACE</div>
    <div class="nav-link {'active' if active=='install' else ''}"
         onclick="nav('install')">INSTALL</div>
    <div class="nav-link"
         onclick="nav('api/generated')">GENERATED</div>
  </nav>
  <div class="spacer"></div>
</header>
<script>
// Detect correct base at runtime — works direct (9100) AND through proxy (8080)
// If URL contains /addons/modules/, strip everything after /app to get PROXY_BASE
// If accessed directly, BASE is empty (relative URLs resolve correctly)
const _path = window.location.pathname;
const _match = _path.match(/^(\/addons\/modules\/[^/]+\/app)/);
const PROXY_BASE = _match ? _match[1] : '';

function nav(path) {{
  window.location.href = PROXY_BASE + (path ? '/' + path : '/');
}}
async function api(path, params={{}}) {{
  const qs = new URLSearchParams(params).toString();
  const url = PROXY_BASE + '/api/' + path + (qs ? '?' + qs : '');
  const r = await fetch(url);
  const text = await r.text();
  let data;
  try {{ data = JSON.parse(text); }} 
  catch(e) {{ throw new Error('Server error (non-JSON response): ' + text.slice(0, 200)); }}
  if (!r.ok) throw new Error(data.error || 'Request failed: ' + r.status);
  return data;
}}
</script>"""


def marketplace_page():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Module Marketplace</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Unbounded:wght@400;700;900&display=swap" rel="stylesheet"/>
<style>
{COMMON_CSS}
.search-row{{display:flex;gap:10px;margin-bottom:28px}}
.search-row input{{flex:1;font-size:13px;padding:10px 14px}}
.pkg-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}}
.pkg-card{{background:var(--card);border:1px solid var(--border);border-radius:3px;
  padding:18px;cursor:pointer;transition:border-color .15s;border-left:3px solid var(--border)}}
.pkg-card:hover{{border-color:var(--amber);border-left-color:var(--amber)}}
.pkg-name{{font-family:var(--display);font-size:13px;font-weight:700;margin-bottom:4px}}
.pkg-version{{font-size:10px;color:var(--dim);margin-bottom:10px}}
.pkg-tags{{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:10px}}
.pkg-count{{font-size:10px;color:var(--mid)}}
.loading{{text-align:center;padding:60px;color:var(--dim);font-size:12px}}
</style>
</head>
<body>
{nav_html('marketplace')}
<main>
  <h1><em>MODULE</em> MARKETPLACE</h1>
  <div class="subtitle">Installed packages — click any to generate a MasterChief addon module</div>
  <div class="search-row">
    <input type="text" id="search" placeholder="Search packages…" oninput="filter(this.value)"/>
  </div>
  <div id="grid" class="pkg-grid"><div class="loading">Loading packages…</div></div>
</main>
<script>
let _all = [];
const COLORS = ['#f5a623','#58a6ff','#00ff88','#ff6b6b','#a78bfa','#34d399','#fb7185','#38bdf8'];
const ICONS  = ['📦','🔧','⚡','🌐','🛠','🔌','💡','🚀','🔍','📊','🗄','🔐','☁','🖥'];

async function load() {{
  const d = await api('packages');
  _all = d.packages || [];
  render(_all);
}}

function render(pkgs) {{
  const grid = document.getElementById('grid');
  if (!pkgs.length) {{
    grid.innerHTML = '<div class="loading">No packages found</div>';
    return;
  }}
  grid.innerHTML = pkgs.map((p,i) => {{
    const color = COLORS[i % COLORS.length];
    const icon  = ICONS[i % ICONS.length];
    const tags  = inferTags(p.name);
    return `<div class="pkg-card" onclick="nav('generate/${{p.name}}')"
              style="border-left-color:${{color}}">
      <div class="pkg-name">${{icon}} ${{p.name}}</div>
      <div class="pkg-version">v${{p.version}}</div>
      <div class="pkg-tags">${{tags.map(t=>`<span class="tag tag-blue">${{t}}</span>`).join('')}}</div>
      <div class="pkg-count">Click to generate module →</div>
    </div>`;
  }}).join('');
}}

function filter(q) {{
  q = q.toLowerCase();
  render(q ? _all.filter(p => p.name.toLowerCase().includes(q)) : _all);
}}

function inferTags(name) {{
  const n = name.toLowerCase();
  const tags = [];
  if (n.includes('azure'))  tags.push('azure');
  if (n.includes('aws'))    tags.push('aws');
  if (n.includes('flask') || n.includes('http') || n.includes('request')) tags.push('web');
  if (n.includes('sql') || n.includes('db') || n.includes('data'))  tags.push('data');
  if (n.includes('auth') || n.includes('jwt') || n.includes('crypt')) tags.push('security');
  if (n.includes('kube') || n.includes('docker') || n.includes('container')) tags.push('infra');
  if (!tags.length) tags.push('utility');
  return tags.slice(0,3);
}}

load();
</script>
</body>
</html>"""


def generate_page_html(package):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Generate — {package}</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Unbounded:wght@400;700;900&display=swap" rel="stylesheet"/>
<style>
{COMMON_CSS}
.gen-layout{{display:grid;grid-template-columns:1fr 340px;gap:24px;align-items:start}}
.features-panel{{background:var(--card);border:1px solid var(--border);border-radius:3px;padding:20px}}
.features-panel h2{{font-family:var(--display);font-size:13px;font-weight:700;margin-bottom:14px}}
.feat-list{{max-height:420px;overflow-y:auto;margin-bottom:14px}}
.feat-item{{display:flex;align-items:flex-start;gap:8px;padding:6px 0;
  border-bottom:1px solid rgba(26,37,53,.5);cursor:pointer}}
.feat-item:hover{{background:rgba(245,166,35,.04)}}
.feat-item label{{cursor:pointer;font-size:11px;color:var(--text);line-height:1.4;flex:1}}
.feat-item input[type=checkbox]{{margin-top:2px;accent-color:var(--amber);flex-shrink:0}}
.feat-actions{{display:flex;gap:8px;margin-bottom:14px}}
.feat-actions button{{flex:1}}
.slug-row{{display:flex;gap:8px;align-items:center;margin-bottom:14px}}
.slug-row label{{font-size:10px;color:var(--dim);letter-spacing:.1em;white-space:nowrap}}
.slug-row input{{flex:1}}
.result-panel{{background:var(--card);border:1px solid var(--border);border-radius:3px;padding:20px}}
.result-panel h2{{font-family:var(--display);font-size:13px;font-weight:700;margin-bottom:14px}}
.loading-dots::after{{content:'';animation:dots 1.2s infinite}}
@keyframes dots{{0%{{content:'.'}}33%{{content:'..'}}66%{{content:'...'}} }}
.summary-grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px}}
.summary-card{{background:var(--panel);border:1px solid var(--border);padding:10px;border-radius:2px}}
.summary-label{{font-size:9px;color:var(--dim);letter-spacing:.15em;margin-bottom:4px}}
.summary-val{{font-size:18px;font-weight:700}}
.file-list{{font-size:11px;color:var(--mid);line-height:2}}
.file-list span{{color:var(--green)}}
</style>
</head>
<body>
{nav_html('marketplace')}
<main>
  <div style="margin-bottom:24px">
    <div style="font-size:10px;color:var(--amber);letter-spacing:.3em;margin-bottom:6px">// GENERATE MODULE</div>
    <h1>📦 <em>{package.upper()}</em></h1>
    <div class="subtitle" id="status-line">Loading features…</div>
  </div>
  <div class="gen-layout">
    <div>
      <div class="features-panel">
        <h2>SELECT FEATURES</h2>
        <div class="feat-actions">
          <button class="btn-ghost" onclick="selectAll()">SELECT ALL</button>
          <button class="btn-ghost" onclick="selectNone()">CLEAR</button>
        </div>
        <div class="feat-list" id="feat-list">
          <div style="color:var(--dim);font-size:12px;text-align:center;padding:30px">
            <span class="loading-dots">Loading</span>
          </div>
        </div>
        <div class="slug-row">
          <label>SLUG</label>
          <input type="text" id="slug" value="{package.replace('-','_').replace('.','_')}"/>
        </div>
        <button class="btn" style="width:100%" onclick="generate()">⚡ GENERATE MODULE</button>
      </div>
    </div>
    <div class="result-panel" id="result-panel">
      <h2>OUTPUT</h2>
      <div style="color:var(--dim);font-size:12px;text-align:center;padding:40px 0">
        Configure features then click Generate
      </div>
    </div>
  </div>
</main>
<script>
const PACKAGE = {json.dumps(package)};
let _features = [];

async function load() {{
  try {{
    const d = await api('introspect', {{package: PACKAGE}});
    _features = d.features || [];
    document.getElementById('status-line').textContent =
      _features.length + ' features found';
    renderFeatures(_features);
  }} catch(e) {{
    document.getElementById('status-line').textContent = 'Error: ' + e.message;
    document.getElementById('feat-list').innerHTML =
      '<div class="error-box">Could not introspect package: ' + e.message + '</div>';
  }}
}}

function renderFeatures(features) {{
  const el = document.getElementById('feat-list');
  if (!features.length) {{
    el.innerHTML = '<div style="color:var(--dim);font-size:11px;text-align:center;padding:20px">No features found</div>';
    return;
  }}
  el.innerHTML = features.slice(0, 300).map(f => `
    <div class="feat-item" onclick="this.querySelector('input').click()">
      <input type="checkbox" name="feat" value="${{f.name}}" checked/>
      <label><strong>${{f.name}}</strong>
        ${{f.label ? '<br><span style="color:var(--dim)">' + f.label + '</span>' : ''}}
      </label>
    </div>`).join('');
}}

function selectAll()  {{ document.querySelectorAll('input[name=feat]').forEach(c => c.checked = true); }}
function selectNone() {{ document.querySelectorAll('input[name=feat]').forEach(c => c.checked = false); }}

async function generate() {{
  const checked = [...document.querySelectorAll('input[name=feat]:checked')].map(c => c.value);
  if (!checked.length) {{
    alert('Select at least one feature');
    return;
  }}
  const slug = document.getElementById('slug').value.trim() || PACKAGE.replace(/-/g,'_');
  const panel = document.getElementById('result-panel');
  panel.innerHTML = '<h2>OUTPUT</h2><div style="color:var(--mid);padding:20px;text-align:center"><span class="loading-dots">Generating</span></div>';

  try {{
    // CRITICAL: use api() helper which builds URL from PROXY_BASE
    const d = await api('generate', {{
      package:  PACKAGE,
      features: checked.join(','),
      slug:     slug,
    }});

    if (d.error) {{
      panel.innerHTML = '<h2>OUTPUT</h2><div class="error-box">' + d.error + '</div>';
      return;
    }}

    panel.innerHTML = `
      <h2>OUTPUT</h2>
      <div class="success-box">✅ Module generated successfully</div>
      <div class="summary-grid">
        <div class="summary-card">
          <div class="summary-label">SLUG</div>
          <div class="summary-val" style="font-size:14px">${{d.slug}}</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">FILES</div>
          <div class="summary-val">${{d.file_count}}</div>
        </div>
      </div>
      <div style="font-size:10px;color:var(--dim);margin-bottom:8px;letter-spacing:.1em">GENERATED FILES</div>
      <div class="file-list">
        ${{(d.files_created || []).map(f => '<span>✓</span> ' + f).join('<br>')}}
      </div>
      <div style="margin-top:16px;display:flex;gap:8px">
        <a class="btn" href="${{PROXY_BASE}}/download/${{d.zip_name}}" download="${{d.zip_name}}">⬇ DOWNLOAD ZIP</a>
        <button class="btn-ghost" onclick="nav('install')">⬆ INSTALL</button>
      </div>`;
  }} catch(e) {{
    panel.innerHTML = '<h2>OUTPUT</h2><div class="error-box">Error: ' + e.message + '</div>';
  }}
}}

load();
</script>
</body>
</html>"""


def install_page_html():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Install Module</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Unbounded:wght@400;700;900&display=swap" rel="stylesheet"/>
<style>
{COMMON_CSS}
.install-box{{max-width:680px;background:var(--card);border:1px solid var(--border);border-radius:3px;padding:28px;margin:0 auto}}
.install-box h2{{font-family:var(--display);font-size:15px;font-weight:700;margin-bottom:6px}}
.install-box .sub{{font-size:11px;color:var(--dim);margin-bottom:20px}}
.mod-row{{display:flex;gap:10px;align-items:center;padding:10px 0;border-bottom:1px solid rgba(26,37,53,.5)}}
.mod-name{{font-size:13px;font-weight:600;flex:1}}
.mod-size{{font-size:10px;color:var(--dim);white-space:nowrap}}
.progress{{background:var(--panel);border-radius:2px;height:3px;overflow:hidden;margin:6px 0}}
.progress-bar{{height:100%;background:var(--amber);width:0%;transition:width .4s}}
</style>
</head>
<body>
{nav_html('install')}
<main>
  <h1><em>INSTALL</em> MODULE</h1>
  <div class="subtitle">One-click install generated modules directly into MasterChief addons folder</div>
  <div class="install-box">
    <h2>GENERATED MODULES</h2>
    <div class="sub">Click Install to copy directly to addons/modules/ — no file upload needed</div>
    <div id="progress-wrap" style="display:none;margin-bottom:12px">
      <div class="progress"><div class="progress-bar" id="pbar"></div></div>
      <div id="progress-msg" style="font-size:11px;color:var(--mid);text-align:center;margin-top:4px"></div>
    </div>
    <div id="result"></div>
    <div id="generated-list">
      <div style="color:var(--dim);font-size:12px;text-align:center;padding:30px">Loading…</div>
    </div>
    <div style="margin-top:20px;padding-top:16px;border-top:1px solid var(--border);font-size:11px;color:var(--dim)">
      💡 After installing, reload the MasterChief addon manager to activate the new module.
    </div>
  </div>
</main>
<script>
async function loadGenerated() {{
  try {{
    const d = await api('generated');
    const el = document.getElementById('generated-list');
    if (!d.length) {{ el.innerHTML = '<span>No generated zips yet</span>'; return; }}
    el.innerHTML = d.map(z => `
      <div style="display:flex;gap:10px;align-items:center;padding:5px 0;border-bottom:1px solid rgba(26,37,53,.4)">
        <span style="flex:1">📦 ${{z.slug}}</span>
        <span style="color:var(--dim);font-size:10px">${{(z.size/1024).toFixed(1)}}KB</span>
        <a class="btn-ghost" style="padding:3px 10px;font-size:10px"
           href="${{PROXY_BASE}}/download/${{z.zip_name}}" download="${{z.zip_name}}">⬇</a>
      </div>`).join('');
  }} catch(e) {{
    document.getElementById('generated-list').innerHTML = 'Error: ' + e.message;
  }}
}}

function handleDrop(e) {{
  e.preventDefault();
  document.getElementById('drop-zone').classList.remove('drag');
  const f = e.dataTransfer.files[0];
  if (f) handleFile(f);
}}

async function handleFile(file) {{
  if (!file || !file.name.endsWith('.zip')) {{
    showResult('error', 'Please select a .zip file');
    return;
  }}

  const wrap = document.getElementById('progress-wrap');
  const pbar = document.getElementById('pbar');
  const msg  = document.getElementById('progress-msg');
  wrap.style.display = 'block';
  pbar.style.width = '20%';
  msg.textContent = 'Uploading ' + file.name + '…';

  const fd = new FormData();
  fd.append('file', file);

  try {{
    const d = await api('install-local', {{slug: slug}});
    pbar.style.width = '100%';
    if (d.success) {{
      msg.textContent = 'Installed!';
      showResult('success', '✅ ' + d.message);
    }} else {{
      showResult('error', d.error || 'Install failed');
    }}
  }} catch(e) {{
    showResult('error', 'Upload error: ' + e.message);
  }}
}}

function showResult(type, msg) {{
  document.getElementById('result').innerHTML =
    `<div class="${{type}}-box">${{msg}}</div>`;
}}

// POST endpoint — must exist on the Flask side
// (Flask needs to handle multipart — see below)
loadGenerated();
</script>
</body>
</html>"""


@app.route('/api/install-local')
def api_install_local():
    """
    Install a previously generated zip by copying it directly to addons/modules/.
    GET-only — proxy safe. Uses filesystem, no POST needed.
    """
    slug = request.args.get('slug', '').strip()
    if not slug:
        return jsonify({'error': 'slug param required'}), 400

    zip_path = OUTPUT_DIR / f'{slug}.zip'
    if not zip_path.exists():
        return jsonify({'error': f'Generated zip not found: {slug}.zip — generate it first'}), 404

    # addons/modules/ is two levels up from this addon's folder
    addons_dir = BASE_DIR.parent.parent
    if not addons_dir.exists():
        return jsonify({'error': f'Addons dir not found at {addons_dir}'}), 500

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            top_dirs = {n.split('/')[0] for n in names if '/' in n}
            if len(top_dirs) != 1:
                return jsonify({'error': 'Zip must contain exactly one top-level folder'}), 400
            extracted_slug = top_dirs.pop()
            # Security: no path traversal
            for name in names:
                if '..' in name or name.startswith('/'):
                    return jsonify({'error': f'Unsafe path: {name}'}), 400
            zf.extractall(str(addons_dir))
        return jsonify({'success': True, 'slug': extracted_slug,
                        'path': str(addons_dir / extracted_slug),
                        'message': f'Installed to addons/modules/{extracted_slug}/ — restart or reload addon manager to activate'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9100))
    print(f'[module-system] Starting on http://localhost:{port}', flush=True)
    print(f'[module-system] Proxy base: {PROXY_BASE}', flush=True)
    app.run(host='0.0.0.0', port=port, debug=False)
