# Module Command Center — MasterChief Integration Guide

## What This Is

Module Command Center is the **platform layer** for MasterChief. Once wired in,
it becomes the central nervous system for all addons:

- Every installed module auto-appears in the correct nav section (Admin Ops, Add Ons, Systems Modules, etc.)
- Capabilities declared by modules are discoverable by other modules via the capability bus
- New modules install and register themselves without any changes to `main.py`
- This addon itself is listed under **Admin Ops** in the nav

---

## One-Time main.py Integration (3 steps)

### Step 1 — Paste this block into main.py

Add **after** `app = Flask(__name__)`, before your routes:

```python
# ── Module Registry Integration ─────────────────────────────────────────────
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
    _load_module_registry()
    return jsonify(_MODULE_REGISTRY)


@app.route('/api/nav-sections')
def api_nav_sections():
    _load_module_registry()
    return jsonify({
        'sections': _MODULE_REGISTRY.get('_nav_sections', []),
        'total_modules': _MODULE_REGISTRY.get('count', 0),
    })


@app.route('/api/capabilities')
def api_capabilities():
    _load_module_registry()
    cap_map = {}
    for slug, m in _MODULE_REGISTRY.get('modules', {}).items():
        for cap in m.get('capabilities', []):
            cap_map.setdefault(cap, []).append(slug)
    return jsonify(cap_map)
# ── End Module Registry Integration ─────────────────────────────────────────
```

### Step 2 — Add sidebar placeholder in your nav template

In whatever template renders your MasterChief sidebar, add:

```html
<!-- Module nav sections auto-injected here -->
<div id="sidebar-modules"></div>
```

### Step 3 — Paste this JS into your nav template

```javascript
// Auto-inject module nav sections from registry
(async function injectModuleNav() {
  try {
    const r = await fetch('/api/nav-sections');
    const d = await r.json();
    const sidebar = document.getElementById('sidebar-modules');
    if (!sidebar || !d.sections) return;

    sidebar.innerHTML = d.sections.map(section => `
      <div class="nav-section">
        <div class="nav-section-label">${section.icon} ${section.label.toUpperCase()}</div>
        ${section.items.map(item => `
          <a class="nav-item addon-link"
             href="${item.url}"
             style="border-left-color:${item.color}">
            ${item.icon} ${item.label}
          </a>`).join('')}
      </div>`
    ).join('');
  } catch(e) {
    console.warn('[registry] Nav inject failed:', e.message);
  }
})();
```

---

## That's it.

After these 3 steps:
- Every module with a `manifest.json` auto-appears in the nav
- The Module Command Center itself appears under **Admin Ops**
- New modules install and show up without touching `main.py` again

---

## How Modules Register

Each addon folder can include a `manifest.json`:

```json
{
  "slug": "cloud-command",
  "label": "Cloud Command",
  "icon": "☁",
  "color": "#00ff88",
  "category": "cloud",
  "nav_section": "Cloud & Infra",
  "capabilities": ["github-pr", "azure-vm", "azure-devops"],
  "requires": [],
  "description": "Multi-cloud management panel"
}
```

**Categories available:**
| Category ID    | Nav Label          |
|----------------|--------------------|
| `admin_ops`    | Admin Ops          |
| `addons`       | Add Ons            |
| `sys_modules`  | Systems Modules    |
| `integrations` | Integrations       |
| `devtools`     | Dev Tools          |
| `data`         | Data & Analytics   |
| `security`     | Security           |
| `cloud`        | Cloud & Infra      |

---

## Capability Bus

Modules can declare what they **provide** and what they **require**:

```json
{
  "capabilities": ["log-stream", "file-browse"],
  "requires":     ["registry-read"]
}
```

Any module can then discover capability providers:

```javascript
const caps = await fetch('/api/capabilities').then(r => r.json());
// caps = { "log-stream": ["log-streamer"], "file-browse": ["diagnostics-alchemy"] }

const logProvider = caps['log-stream']?.[0];
const logUrl = `/addons/modules/${logProvider}/app/api/stream`;
```

This is how modules link to and enhance each other without hardcoded dependencies.

---

## Platform API (exposed by this addon)

All endpoints proxied at `/addons/modules/module-system-v3/app/api/...`

| Endpoint              | Description                                      |
|-----------------------|--------------------------------------------------|
| `GET /api/registry`   | Full registry JSON                               |
| `GET /api/nav-sections` | Grouped nav for sidebar injection              |
| `GET /api/capabilities` | Capability bus map                             |
| `GET /api/write-registry` | Force re-discover + write registry.json     |
| `GET /api/update-manifest` | Edit a module's manifest                   |
| `GET /api/installed`  | All installed modules with metadata              |
| `GET /api/packages`   | All pip packages                                 |
| `GET /api/introspect` | Introspect a package's API surface               |
| `GET /api/generate`   | Generate an addon zip                            |
| `GET /api/install`    | Install a generated zip to addons/modules/       |
| `GET /api/remove`     | Remove an installed module                       |
| `GET /api/pip-install`| Install a pip package                            |
| `GET /api/addon-logs` | Read addon log output                            |
| `GET /download/<zip>` | Download a generated zip                         |
