"""MasterChief System Diagnostics — HTML Template"""

DIAGNOSTICS_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MasterChief · System Diagnostics</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<style>
/* ── Reset & base ────────────────────────────────────────── */
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg0:#0d1117;--bg1:#161b22;--bg2:#21262d;--bg3:#2d333b;
  --border:#30363d;--text:#e6edf3;--muted:#8b949e;--accent:#7c3aed;
  --green:#3fb950;--yellow:#d29922;--red:#f85149;--blue:#58a6ff;
  --cyan:#39d353;--orange:#d18616;
  --node-route:#7c3aed;--node-fn:#2563eb;--node-handler:#059669;
  --node-template:#d97706;--node-ext:#dc2626;--node-orphan:#4b5563;
  --node-file:#0891b2;--node-flask:#6366f1;
}
body{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg0);color:var(--text);
  height:100vh;display:flex;flex-direction:column;overflow:hidden;font-size:13px}

/* ── Header ─────────────────────────────────────────────── */
#header{background:var(--bg1);border-bottom:1px solid var(--border);
  padding:0 16px;height:48px;display:flex;align-items:center;gap:12px;flex-shrink:0;
  z-index:100;position:relative}
#header .logo{font-size:16px;font-weight:700;color:var(--accent);display:flex;align-items:center;gap:6px}
#header .logo svg{width:20px;height:20px}
.summary-chips{display:flex;gap:6px;margin-left:8px;flex-wrap:wrap}
.chip{background:var(--bg3);border:1px solid var(--border);border-radius:20px;
  padding:2px 10px;font-size:11px;cursor:default;white-space:nowrap}
.chip.err{border-color:var(--red);color:var(--red)}
.chip.warn{border-color:var(--yellow);color:var(--yellow)}
.chip.ok{border-color:var(--green);color:var(--green)}
.chip.info{border-color:var(--blue);color:var(--blue)}
.spacer{flex:1}
.header-btn{background:var(--bg3);border:1px solid var(--border);color:var(--text);
  padding:5px 14px;border-radius:6px;cursor:pointer;font-size:12px;
  display:flex;align-items:center;gap:5px;transition:all .15s}
.header-btn:hover{background:var(--accent);border-color:var(--accent)}
.header-btn.primary{background:var(--accent);border-color:var(--accent)}
.header-btn.primary:hover{background:#6d28d9}
#scan-status{font-size:11px;color:var(--muted);min-width:120px;text-align:right}

/* ── Body layout ─────────────────────────────────────────── */
#body{display:flex;flex:1;overflow:hidden}

/* ── Left: File Tree ─────────────────────────────────────── */
#tree-panel{width:260px;min-width:180px;background:var(--bg1);border-right:1px solid var(--border);
  display:flex;flex-direction:column;overflow:hidden;flex-shrink:0;transition:width .2s}
#tree-panel.collapsed{width:0;min-width:0}
#tree-header{padding:8px 12px;font-size:11px;font-weight:600;letter-spacing:.06em;
  text-transform:uppercase;color:var(--muted);border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
#tree-search{padding:6px 10px;border-bottom:1px solid var(--border);flex-shrink:0}
#tree-search input{width:100%;background:var(--bg3);border:1px solid var(--border);
  color:var(--text);border-radius:4px;padding:4px 8px;font-size:12px;outline:none}
#tree-search input:focus{border-color:var(--accent)}
#tree-content{overflow-y:auto;flex:1;padding:4px 0}
.tree-item{display:flex;align-items:center;gap:5px;padding:2px 8px 2px 0;
  cursor:pointer;border-radius:4px;margin:0 4px;position:relative;user-select:none}
.tree-item:hover{background:var(--bg3)}
.tree-item.selected{background:var(--accent)22;border-left:2px solid var(--accent)}
.tree-item .indent{display:inline-block;width:12px;flex-shrink:0}
.tree-item .arrow{width:12px;font-size:9px;color:var(--muted);flex-shrink:0;text-align:center}
.tree-item .icon{flex-shrink:0;font-size:13px}
.tree-item .fname{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px}
.tree-item .badge{font-size:9px;padding:1px 5px;border-radius:8px;flex-shrink:0}
.badge-orphan{background:#4b556322;color:#9ca3af;border:1px solid #4b5563}
.badge-active{background:#05966922;color:#34d399;border:1px solid #059669}
.badge-err{background:#dc262622;color:#f87171;border:1px solid #dc2626}

/* ── Center: Main ────────────────────────────────────────── */
#main-panel{flex:1;display:flex;flex-direction:column;overflow:hidden;min-width:0}
#tabs{background:var(--bg1);border-bottom:1px solid var(--border);
  display:flex;align-items:center;padding:0 12px;gap:0;flex-shrink:0;overflow-x:auto}
.tab{padding:10px 16px;cursor:pointer;font-size:12px;color:var(--muted);
  border-bottom:2px solid transparent;white-space:nowrap;transition:color .15s;
  display:flex;align-items:center;gap:5px}
.tab:hover{color:var(--text)}
.tab.active{color:var(--text);border-bottom-color:var(--accent)}
.tab .count{background:var(--bg3);border-radius:10px;padding:1px 6px;font-size:10px;
  color:var(--muted)}
.tab.active .count{background:var(--accent)33;color:var(--accent)}
#tab-content{flex:1;overflow:hidden;position:relative}
.tab-pane{display:none;height:100%;overflow:hidden}
.tab-pane.active{display:flex;flex-direction:column}

/* ── Graph pane ──────────────────────────────────────────── */
#graph-toolbar{background:var(--bg2);border-bottom:1px solid var(--border);
  padding:6px 12px;display:flex;align-items:center;gap:8px;flex-shrink:0}
.zoom-btns{display:flex;gap:3px}
.zb{background:var(--bg3);border:1px solid var(--border);color:var(--muted);
  padding:3px 10px;border-radius:4px;cursor:pointer;font-size:11px;transition:all .15s}
.zb:hover,.zb.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.filter-btns{display:flex;gap:4px;flex-wrap:wrap}
.fb{display:flex;align-items:center;gap:4px;padding:3px 8px;border-radius:4px;
  cursor:pointer;font-size:11px;border:1px solid var(--border);
  background:var(--bg3);transition:all .15s}
.fb .dot{width:8px;height:8px;border-radius:50%}
.fb.active{border-color:currentColor}
.fb.inactive{opacity:.4}
#graph-container{flex:1;overflow:hidden;position:relative;cursor:grab}
#graph-container:active{cursor:grabbing}
#graph-svg{width:100%;height:100%}
.legend{position:absolute;bottom:12px;left:12px;background:var(--bg2)ee;
  border:1px solid var(--border);border-radius:8px;padding:10px 14px;
  display:grid;grid-template-columns:1fr 1fr;gap:4px 20px;min-width:280px}
.legend-title{grid-column:1/-1;font-size:10px;text-transform:uppercase;
  letter-spacing:.08em;color:var(--muted);margin-bottom:4px}
.legend-item{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--muted)}
.legend-dot{width:10px;height:10px;border-radius:50%}
.legend-line{width:20px;height:2px}
.legend-dash{width:20px;height:0;border-top:2px dashed}
.graph-tooltip{position:absolute;background:var(--bg2);border:1px solid var(--border);
  border-radius:6px;padding:8px 12px;font-size:12px;pointer-events:none;
  max-width:240px;z-index:50;display:none}
.graph-tooltip .tt-type{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.graph-tooltip .tt-name{font-weight:600;margin:2px 0 4px}
.graph-tooltip .tt-file{color:var(--blue);font-size:11px}

/* ── Table panes ─────────────────────────────────────────── */
.table-toolbar{padding:8px 12px;background:var(--bg2);border-bottom:1px solid var(--border);
  display:flex;align-items:center;gap:8px;flex-shrink:0}
.table-toolbar input{background:var(--bg3);border:1px solid var(--border);color:var(--text);
  border-radius:4px;padding:4px 10px;font-size:12px;outline:none;min-width:200px}
.table-toolbar input:focus{border-color:var(--accent)}
.tbl-wrap{flex:1;overflow:auto}
table{width:100%;border-collapse:collapse;font-size:12px}
thead th{background:var(--bg2);padding:7px 12px;text-align:left;font-weight:500;
  color:var(--muted);border-bottom:1px solid var(--border);position:sticky;top:0;
  white-space:nowrap;cursor:pointer;user-select:none}
thead th:hover{color:var(--text)}
thead th.sorted{color:var(--accent)}
tbody tr{border-bottom:1px solid var(--border)55;transition:background .1s}
tbody tr:hover{background:var(--bg2)}
tbody tr.clickable{cursor:pointer}
tbody td{padding:6px 12px;line-height:1.4;vertical-align:top}
.pill{display:inline-block;padding:1px 8px;border-radius:10px;font-size:10px;font-weight:500}
.pill-get{background:#05966922;color:#34d399;border:1px solid #059669}
.pill-post{background:#2563eb22;color:#60a5fa;border:1px solid #2563eb}
.pill-put{background:#d9772222;color:#fbbf24;border:1px solid #d97706}
.pill-del{background:#dc262622;color:#f87171;border:1px solid #dc2626}
.pill-route{background:#7c3aed22;color:#a78bfa;border:1px solid #7c3aed}
.pill-fn{background:#2563eb22;color:#60a5fa;border:1px solid #2563eb}
.pill-orphan{background:#4b556322;color:#9ca3af;border:1px solid #4b5563}
.pill-active{background:#05966922;color:#34d399;border:1px solid #059669}
.pill-error{background:#dc262622;color:#f87171;border:1px solid #dc2626}
.pill-warn{background:#d9772222;color:#fbbf24;border:1px solid #d97706}
.pill-info{background:#2563eb22;color:#60a5fa;border:1px solid #2563eb}
td.mono{font-family:'Cascadia Code','Fira Code',monospace;font-size:11px}
td.link{color:var(--blue);cursor:pointer}
td.link:hover{text-decoration:underline}

/* ── Issues pane ─────────────────────────────────────────── */
.issue-row{display:flex;gap:10px;padding:8px 12px;border-bottom:1px solid var(--border)44;
  cursor:pointer;align-items:flex-start;transition:background .1s}
.issue-row:hover{background:var(--bg2)}
.issue-sev{width:6px;border-radius:3px;flex-shrink:0;margin-top:3px;align-self:stretch}
.sev-error{background:var(--red)}
.sev-warning{background:var(--yellow)}
.sev-info{background:var(--blue)}
.issue-body{flex:1}
.issue-msg{font-size:12px;line-height:1.4}
.issue-meta{font-size:11px;color:var(--muted);margin-top:2px}
.issue-suggest{font-size:11px;color:var(--cyan);margin-top:3px;padding-left:6px;
  border-left:2px solid var(--cyan)55}

/* ── Services pane ───────────────────────────────────────── */
.svc-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
  gap:12px;padding:16px;overflow-y:auto;align-content:start}
.svc-card{background:var(--bg2);border:1px solid var(--border);border-radius:8px;
  padding:14px;transition:border-color .2s}
.svc-card:hover{border-color:var(--accent)66}
.svc-card.running{border-left:3px solid var(--green)}
.svc-card.stopped{border-left:3px solid var(--muted)}
.svc-name{font-weight:600;font-size:13px;margin-bottom:6px}
.svc-meta{font-size:11px;color:var(--muted);display:flex;gap:10px;flex-wrap:wrap}
.svc-badge{padding:2px 8px;border-radius:10px;font-size:11px;font-weight:500}
.svc-badge.running{background:#05966922;color:#34d399;border:1px solid #059669}
.svc-badge.stopped{background:#4b556322;color:#9ca3af;border:1px solid #4b5563}
.svc-actions{margin-top:10px;display:flex;gap:6px}
.svc-btn{background:var(--bg3);border:1px solid var(--border);color:var(--text);
  padding:3px 10px;border-radius:4px;cursor:pointer;font-size:11px}
.svc-btn:hover{background:var(--accent);border-color:var(--accent);color:#fff}

/* ── Right: Inspector ────────────────────────────────────── */
#inspector{width:0;min-width:0;background:var(--bg1);border-left:1px solid var(--border);
  display:flex;flex-direction:column;overflow:hidden;flex-shrink:0;transition:width .2s}
#inspector.open{width:400px;min-width:300px}
#insp-header{padding:8px 12px;border-bottom:1px solid var(--border);
  display:flex;align-items:center;gap:8px;flex-shrink:0}
#insp-header .insp-title{font-size:12px;font-weight:600;flex:1;overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
#insp-close{cursor:pointer;color:var(--muted);font-size:16px;padding:2px 4px}
#insp-close:hover{color:var(--text)}
#insp-meta{padding:10px 12px;border-bottom:1px solid var(--border);flex-shrink:0}
.insp-tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;
  margin-right:5px;margin-bottom:4px}
#insp-actions{padding:8px 12px;border-bottom:1px solid var(--border);
  display:flex;gap:6px;flex-shrink:0;flex-wrap:wrap}
.insp-btn{background:var(--bg3);border:1px solid var(--border);color:var(--text);
  padding:4px 12px;border-radius:5px;cursor:pointer;font-size:11px;
  display:flex;align-items:center;gap:4px;transition:all .15s;text-decoration:none}
.insp-btn:hover{background:var(--accent);border-color:var(--accent);color:#fff}
.insp-btn.primary{background:var(--accent);border-color:var(--accent)}
#insp-code{flex:1;overflow:auto}
#insp-code pre{margin:0;border-radius:0!important}
#insp-code code{font-size:11px!important;background:transparent!important}
#insp-suggestions{border-top:1px solid var(--border);flex-shrink:0}
#insp-sug-header{padding:8px 12px;cursor:pointer;display:flex;align-items:center;
  gap:6px;font-size:11px;color:var(--muted)}
#insp-sug-header:hover{color:var(--text)}
#insp-sug-body{padding:8px 12px;max-height:180px;overflow-y:auto;display:none}
.sug-item{display:flex;gap:7px;padding:5px 0;font-size:11px;border-bottom:1px solid var(--border)44}
.sug-item:last-child{border-bottom:none}
.sug-icon{flex-shrink:0;width:16px;text-align:center}

/* ── Bottom status bar ───────────────────────────────────── */
#status-bar{background:var(--accent);height:22px;display:flex;align-items:center;
  padding:0 12px;gap:16px;flex-shrink:0;font-size:11px}
.sb-item{display:flex;align-items:center;gap:4px;cursor:default;color:#ffffffcc}
.sb-item span{color:#fff}

/* ── Scrollbars ──────────────────────────────────────────── */
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:var(--bg1)}
::-webkit-scrollbar-thumb{background:var(--bg3);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:var(--muted)}

/* ── Overlay / loading ───────────────────────────────────── */
#scan-overlay{position:fixed;inset:0;background:#0d111799;z-index:200;
  display:none;align-items:center;justify-content:center;flex-direction:column;gap:12px}
#scan-overlay.visible{display:flex}
.spinner{width:36px;height:36px;border:3px solid var(--bg3);
  border-top-color:var(--accent);border-radius:50%;animation:spin .7s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.scan-msg{color:var(--text);font-size:14px}

/* ── Resize handle ───────────────────────────────────────── */
.resize-handle{width:4px;cursor:col-resize;background:transparent;flex-shrink:0}
.resize-handle:hover{background:var(--accent)55}
</style>
</head>
<body>

<!-- Loading overlay -->
<div id="scan-overlay">
  <div class="spinner"></div>
  <div class="scan-msg" id="scan-msg">Scanning workspace…</div>
</div>

<!-- Header -->
<div id="header">
  <div class="logo">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/>
    </svg>
    MasterChief · Diagnostics
  </div>
  <div class="summary-chips" id="summary-chips"></div>
  <div class="spacer"></div>
  <div id="scan-status">Not scanned</div>
  <button class="header-btn" onclick="exportData()">⬇ Export</button>
  <button class="header-btn primary" onclick="startScan()">⟳ Scan Workspace</button>
</div>

<!-- Body -->
<div id="body">

  <!-- File Tree -->
  <div id="tree-panel">
    <div id="tree-header">
      Explorer
      <span style="cursor:pointer;font-size:16px;color:var(--muted)" onclick="toggleTree()" title="Collapse">⟨</span>
    </div>
    <div id="tree-search"><input type="text" placeholder="Filter files…" oninput="filterTree(this.value)"></div>
    <div id="tree-content"></div>
  </div>
  <div class="resize-handle" id="tree-resize"></div>

  <!-- Main panel -->
  <div id="main-panel">
    <div id="tabs">
      <div class="tab active" data-tab="graph">🗺 Architecture<span class="count" id="cnt-graph">—</span></div>
      <div class="tab" data-tab="routes">🔌 Routes<span class="count" id="cnt-routes">—</span></div>
      <div class="tab" data-tab="files">📁 Files<span class="count" id="cnt-files">—</span></div>
      <div class="tab" data-tab="issues">⚠️ Issues<span class="count" id="cnt-issues">—</span></div>
      <div class="tab" data-tab="services">⚙ Services<span class="count" id="cnt-services">—</span></div>
    </div>

    <div id="tab-content">

      <!-- GRAPH TAB -->
      <div class="tab-pane active" id="pane-graph">
        <div id="graph-toolbar">
          <span style="font-size:11px;color:var(--muted);font-weight:600">ZOOM LEVEL</span>
          <div class="zoom-btns">
            <div class="zb active" id="zb-overview" onclick="setZoom('overview')">Overview</div>
            <div class="zb" id="zb-module" onclick="setZoom('module')">Module</div>
            <div class="zb" id="zb-detail" onclick="setZoom('detail')">Detailed</div>
          </div>
          <div style="width:1px;height:18px;background:var(--border);margin:0 4px"></div>
          <span style="font-size:11px;color:var(--muted);font-weight:600">SHOW</span>
          <div class="filter-btns" id="filter-btns">
            <div class="fb active" data-type="route" onclick="toggleFilter(this)" style="color:var(--node-route)">
              <div class="dot" style="background:var(--node-route)"></div>Routes
            </div>
            <div class="fb active" data-type="function" onclick="toggleFilter(this)" style="color:var(--node-fn)">
              <div class="dot" style="background:var(--node-fn)"></div>Functions
            </div>
            <div class="fb active" data-type="file" onclick="toggleFilter(this)" style="color:var(--node-file)">
              <div class="dot" style="background:var(--node-file)"></div>Files
            </div>
            <div class="fb active" data-type="external" onclick="toggleFilter(this)" style="color:var(--node-ext)">
              <div class="dot" style="background:var(--node-ext)"></div>External
            </div>
            <div class="fb active" data-type="orphan" onclick="toggleFilter(this)" style="color:var(--node-orphan)">
              <div class="dot" style="background:var(--node-orphan)"></div>Orphans
            </div>
          </div>
          <div class="spacer"></div>
          <button class="header-btn" onclick="resetGraphView()" style="padding:3px 10px;font-size:11px">⊙ Reset View</button>
        </div>
        <div id="graph-container">
          <svg id="graph-svg"></svg>
          <div class="graph-tooltip" id="graph-tooltip">
            <div class="tt-type" id="tt-type"></div>
            <div class="tt-name" id="tt-name"></div>
            <div class="tt-file" id="tt-file"></div>
          </div>
          <!-- Legend -->
          <div class="legend">
            <div class="legend-title">KEY</div>
            <div class="legend-item"><div class="legend-dot" style="background:var(--node-route)"></div>Route endpoint</div>
            <div class="legend-item"><div class="legend-dot" style="background:var(--node-fn)"></div>Function / handler</div>
            <div class="legend-item"><div class="legend-dot" style="background:var(--node-file)"></div>Source file</div>
            <div class="legend-item"><div class="legend-dot" style="background:var(--node-ext)"></div>External / Flask API</div>
            <div class="legend-item"><div class="legend-dot" style="background:var(--node-orphan);border:1px dashed #6b7280"></div>Orphan (unused)</div>
            <div class="legend-item"><div class="legend-dash" style="border-color:#6b7280"></div>Import link</div>
            <div class="legend-item">
              <svg width="20" height="10"><line x1="0" y1="5" x2="18" y2="5" stroke="#f85149" stroke-width="1.5" stroke-dasharray="3,2"/><text x="14" y="8" fill="#f85149" font-size="8">!</text></svg>
              Dead / broken ref
            </div>
          </div>
        </div>
      </div>

      <!-- ROUTES TAB -->
      <div class="tab-pane" id="pane-routes">
        <div class="table-toolbar">
          <input type="text" id="routes-filter" placeholder="Filter routes by path, method, or handler…" oninput="filterRoutes(this.value)">
          <div class="spacer"></div>
          <span style="font-size:11px;color:var(--muted)" id="routes-count"></span>
        </div>
        <div class="tbl-wrap">
          <table id="routes-table">
            <thead>
              <tr>
                <th onclick="sortTable('routes','methods')">Method</th>
                <th onclick="sortTable('routes','path')">Path</th>
                <th onclick="sortTable('routes','handler')">Handler</th>
                <th onclick="sortTable('routes','file')">File</th>
                <th onclick="sortTable('routes','line')">Line</th>
                <th>Calls</th>
                <th>Auth</th>
              </tr>
            </thead>
            <tbody id="routes-tbody"></tbody>
          </table>
        </div>
      </div>

      <!-- FILES TAB -->
      <div class="tab-pane" id="pane-files">
        <div class="table-toolbar">
          <input type="text" id="files-filter" placeholder="Filter files…" oninput="filterFiles(this.value)">
          <div class="spacer"></div>
          <span style="font-size:11px;color:var(--muted)" id="files-count"></span>
        </div>
        <div class="tbl-wrap">
          <table id="files-table">
            <thead>
              <tr>
                <th>File</th>
                <th onclick="sortTable('files','lines')">Lines</th>
                <th onclick="sortTable('files','routes')">Routes</th>
                <th onclick="sortTable('files','functions')">Functions</th>
                <th onclick="sortTable('files','imports')">Imports</th>
                <th onclick="sortTable('files','size')">Size</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody id="files-tbody"></tbody>
          </table>
        </div>
      </div>

      <!-- ISSUES TAB -->
      <div class="tab-pane" id="pane-issues">
        <div class="table-toolbar">
          <input type="text" id="issues-filter" placeholder="Filter issues…" oninput="filterIssues(this.value)">
          <label style="font-size:11px;color:var(--muted);display:flex;align-items:center;gap:4px">
            <input type="checkbox" id="sev-error" checked onchange="filterIssues()"> Errors
          </label>
          <label style="font-size:11px;color:var(--muted);display:flex;align-items:center;gap:4px">
            <input type="checkbox" id="sev-warning" checked onchange="filterIssues()"> Warnings
          </label>
          <label style="font-size:11px;color:var(--muted);display:flex;align-items:center;gap:4px">
            <input type="checkbox" id="sev-info" checked onchange="filterIssues()"> Info
          </label>
          <div class="spacer"></div>
          <span style="font-size:11px;color:var(--muted)" id="issues-count"></span>
        </div>
        <div id="issues-list" style="overflow-y:auto;flex:1"></div>
      </div>

      <!-- SERVICES TAB -->
      <div class="tab-pane" id="pane-services">
        <div class="table-toolbar">
          <button class="header-btn" onclick="loadServices()">↻ Refresh</button>
          <span style="font-size:11px;color:var(--muted)" id="services-count"></span>
        </div>
        <div id="services-grid" class="svc-grid"></div>
      </div>

    </div><!-- /tab-content -->
  </div><!-- /main-panel -->

  <!-- Inspector panel -->
  <div id="inspector">
    <div id="insp-header">
      <span id="insp-title" class="insp-title">Inspector</span>
      <span id="insp-close" onclick="closeInspector()">✕</span>
    </div>
    <div id="insp-meta"></div>
    <div id="insp-actions"></div>
    <div id="insp-code"></div>
    <div id="insp-suggestions">
      <div id="insp-sug-header" onclick="toggleSuggestions()">
        💡 <span id="sug-count">0</span> Suggestions <span id="sug-arrow">▶</span>
      </div>
      <div id="insp-sug-body"></div>
    </div>
  </div>
</div>

<!-- Status bar -->
<div id="status-bar">
  <div class="sb-item">MasterChief System Diagnostics</div>
  <div class="sb-item">Routes: <span id="sb-routes">—</span></div>
  <div class="sb-item">Functions: <span id="sb-fns">—</span></div>
  <div class="sb-item">Errors: <span id="sb-errors">—</span></div>
  <div class="sb-item">Warnings: <span id="sb-warns">—</span></div>
  <div class="spacer" style="flex:1"></div>
  <div class="sb-item" id="sb-scan-time"></div>
</div>

<script>
// ════════════════════════════════════════════════════════════
//  Global state
// ════════════════════════════════════════════════════════════
let _data = null;
let _graphData = null;
let _simulation = null;
let _zoomLevel = 'overview';
let _activeFilters = new Set(['route','function','file','external','orphan']);
let _sortStates = {};
let _inspItem = null;

// ════════════════════════════════════════════════════════════
//  Bootstrap
// ════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  setupTabs();
  setupResizeHandle();
  startScan();
});

function setupTabs() {
  document.querySelectorAll('.tab').forEach(t => {
    t.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(x => x.classList.remove('active'));
      t.classList.add('active');
      document.getElementById('pane-' + t.dataset.tab).classList.add('active');
      if (t.dataset.tab === 'services') loadServices();
    });
  });
}

function setupResizeHandle() {
  const handle = document.getElementById('tree-resize');
  const panel  = document.getElementById('tree-panel');
  let dragging = false, startX = 0, startW = 0;
  handle.addEventListener('mousedown', e => {
    dragging = true; startX = e.clientX; startW = panel.offsetWidth;
    document.body.style.userSelect = 'none';
  });
  document.addEventListener('mousemove', e => {
    if (!dragging) return;
    panel.style.width = Math.max(0, Math.min(500, startW + e.clientX - startX)) + 'px';
  });
  document.addEventListener('mouseup', () => {
    dragging = false; document.body.style.userSelect = '';
  });
}

// ════════════════════════════════════════════════════════════
//  Scan
// ════════════════════════════════════════════════════════════
async function startScan() {
  showOverlay('Scanning workspace…');
  try {
    const res = await fetch('/sys/api/scan');
    _data = await res.json();
    if (_data.error) { hideOverlay(); alert('Scan error: ' + _data.error); return; }
    applyData(_data);
  } catch(e) {
    hideOverlay();
    alert('Failed to contact /sys/api/scan: ' + e);
  }
}

function applyData(data) {
  updateSummaryChips(data.summary);
  renderFileTree(data.file_tree);
  renderRoutes(data.routes || []);
  renderFiles(data.files || []);
  renderIssues(data.issues || []);
  buildGraph(data.graph || {nodes:[],edges:[]});
  updateStatusBar(data.summary);
  document.getElementById('scan-status').textContent =
    `Last scan: ${new Date().toLocaleTimeString()} (${data.scan_time}s)`;
  document.getElementById('sb-scan-time').textContent = `Scan: ${data.scan_time}s`;
  hideOverlay();
}

// ════════════════════════════════════════════════════════════
//  Summary chips
// ════════════════════════════════════════════════════════════
function updateSummaryChips(s) {
  const el = document.getElementById('summary-chips');
  el.innerHTML = `
    <div class="chip ok">📁 ${s.total_files} files</div>
    <div class="chip info">🐍 ${s.python_files} Python</div>
    <div class="chip info">🔌 ${s.routes} routes</div>
    <div class="chip info">⚙ ${s.functions} functions</div>
    ${s.errors > 0   ? `<div class="chip err">❌ ${s.errors} errors</div>` : ''}
    ${s.warnings > 0 ? `<div class="chip warn">⚠ ${s.warnings} warnings</div>` : ''}
    <div class="chip">${s.orphan_functions} orphan fns</div>
  `;
  // Update tab counts
  document.getElementById('cnt-routes').textContent   = s.routes;
  document.getElementById('cnt-files').textContent    = s.python_files;
  document.getElementById('cnt-issues').textContent   = s.issues;
  document.getElementById('cnt-services').textContent = '?';
}

function updateStatusBar(s) {
  document.getElementById('sb-routes').textContent  = s.routes;
  document.getElementById('sb-fns').textContent     = s.functions;
  document.getElementById('sb-errors').textContent  = s.errors;
  document.getElementById('sb-warns').textContent   = s.warnings;
}

// ════════════════════════════════════════════════════════════
//  File Tree
// ════════════════════════════════════════════════════════════
function renderFileTree(tree) {
  const el = document.getElementById('tree-content');
  el.innerHTML = '';
  renderTreeNode(el, tree, 0);
}

function renderTreeNode(container, node, depth) {
  if (node.type === 'dir') {
    const wrap = document.createElement('div');
    wrap.dataset.open = 'true';

    const row = document.createElement('div');
    row.className = 'tree-item';
    row.innerHTML = `
      <span class="indent" style="width:${depth*12}px"></span>
      <span class="arrow" id="arr-${node.name}">▾</span>
      <span class="icon">📂</span>
      <span class="fname">${node.name}</span>
    `;
    row.addEventListener('click', () => {
      const childWrap = wrap.querySelector('.tree-children');
      const arr = row.querySelector('.arrow');
      if (childWrap) {
        const open = wrap.dataset.open === 'true';
        childWrap.style.display = open ? 'none' : '';
        wrap.dataset.open = open ? 'false' : 'true';
        arr.textContent = open ? '▸' : '▾';
      }
    });
    wrap.appendChild(row);

    const childWrap = document.createElement('div');
    childWrap.className = 'tree-children';
    (node.children || []).forEach(child => renderTreeNode(childWrap, child, depth + 1));
    (node.files   || []).forEach(file  => renderFileItem(childWrap, file, depth + 1));
    wrap.appendChild(childWrap);
    container.appendChild(wrap);
  }
}

function renderFileItem(container, file, depth) {
  const row = document.createElement('div');
  row.className = 'tree-item';
  const icon = _fileIcon(file.ext);
  const badge = file.status === 'orphan'
    ? '<span class="badge badge-orphan">orphan</span>'
    : file.status === 'active'
    ? ''
    : '';
  row.innerHTML = `
    <span class="indent" style="width:${depth*12}px"></span>
    <span class="arrow"></span>
    <span class="icon">${icon}</span>
    <span class="fname">${file.name}</span>
    ${badge}
  `;
  if (file.status === 'orphan') row.style.opacity = '0.55';
  row.addEventListener('click', () => inspectFile(file.rel_path, 0));
  container.appendChild(row);
}

function _fileIcon(ext) {
  const icons = {
    '.py':'🐍','.html':'🌐','.js':'📜','.css':'🎨','.json':'📋',
    '.md':'📝','.yml':'⚙','.yaml':'⚙','.sh':'💻','.txt':'📄',
    '.ts':'📘','.jsx':'⚛','.tsx':'⚛','.sql':'🗄','.env':'🔒',
  };
  return icons[ext] || '📄';
}

function filterTree(q) {
  q = q.toLowerCase();
  document.querySelectorAll('#tree-content .tree-item').forEach(row => {
    const name = (row.querySelector('.fname')?.textContent || '').toLowerCase();
    row.style.display = (!q || name.includes(q)) ? '' : 'none';
  });
}

function toggleTree() {
  document.getElementById('tree-panel').classList.toggle('collapsed');
}

// ════════════════════════════════════════════════════════════
//  Routes table
// ════════════════════════════════════════════════════════════
let _routes = [];
function renderRoutes(routes) {
  _routes = routes;
  document.getElementById('routes-count').textContent = `${routes.length} routes`;
  _renderRoutesTable(routes);
}

function _renderRoutesTable(routes) {
  const tbody = document.getElementById('routes-tbody');
  const AUTH_HINTS = ['login_required','require_auth','jwt_required','token_required','auth_required'];
  tbody.innerHTML = routes.map(r => {
    const methods = (r.methods || ['GET']).map(m =>
      `<span class="pill pill-${m.toLowerCase()}">${m}</span>`).join(' ');
    const hasAuth = AUTH_HINTS.some(a =>
      (r.decorators || []).some(d => d.includes(a)) ||
      (r.calls || []).includes(a));
    const authBadge = hasAuth
      ? '<span style="color:var(--green)">✓</span>'
      : '<span style="color:var(--red)">✗</span>';
    const calls = (r.calls || []).slice(0,3).join(', ') + ((r.calls||[]).length > 3 ? '…' : '');
    return `<tr class="clickable" onclick="inspectRoute(${JSON.stringify(r).replace(/"/g,'&quot;')})">
      <td>${methods}</td>
      <td class="mono">${r.path || ''}</td>
      <td class="mono link">${r.handler || ''}</td>
      <td class="mono" style="color:var(--blue)">${(r.file||'').split('/').pop()}</td>
      <td style="color:var(--muted)">${r.line || ''}</td>
      <td class="mono" style="color:var(--muted);font-size:10px">${calls}</td>
      <td style="text-align:center">${authBadge}</td>
    </tr>`;
  }).join('');
}

function filterRoutes(q) {
  q = q.toLowerCase();
  const filtered = q ? _routes.filter(r =>
    (r.path||'').toLowerCase().includes(q) ||
    (r.handler||'').toLowerCase().includes(q) ||
    (r.methods||[]).some(m => m.toLowerCase().includes(q))
  ) : _routes;
  document.getElementById('routes-count').textContent = `${filtered.length} of ${_routes.length}`;
  _renderRoutesTable(filtered);
}

// ════════════════════════════════════════════════════════════
//  Files table
// ════════════════════════════════════════════════════════════
let _files = [];
function renderFiles(files) {
  _files = files;
  document.getElementById('files-count').textContent = `${files.length} Python files`;
  _renderFilesTable(files);
}

function _renderFilesTable(files) {
  const tbody = document.getElementById('files-tbody');
  tbody.innerHTML = files.map(f => {
    const sz = f.size > 1024*1024
      ? (f.size/1024/1024).toFixed(1)+'MB'
      : f.size > 1024 ? (f.size/1024).toFixed(0)+'KB' : f.size+'B';
    const stpill = f.status === 'active'
      ? '<span class="pill pill-active">active</span>'
      : f.has_error
      ? '<span class="pill pill-error">error</span>'
      : '<span class="pill pill-orphan">orphan</span>';
    return `<tr class="clickable" onclick="inspectFile('${f.rel_path}',0)">
      <td class="mono link">${f.rel_path}</td>
      <td style="color:var(--muted);text-align:right">${f.lines.toLocaleString()}</td>
      <td style="text-align:center">${f.routes > 0 ? `<span style="color:var(--node-route)">${f.routes}</span>` : '<span style="color:var(--muted)">0</span>'}</td>
      <td style="text-align:center">${f.functions > 0 ? `<span style="color:var(--node-fn)">${f.functions}</span>` : '<span style="color:var(--muted)">0</span>'}</td>
      <td style="text-align:center;color:var(--muted)">${f.imports}</td>
      <td style="text-align:right;color:var(--muted)">${sz}</td>
      <td>${stpill}</td>
    </tr>`;
  }).join('');
}

function filterFiles(q) {
  q = q.toLowerCase();
  const filtered = q ? _files.filter(f => f.rel_path.toLowerCase().includes(q)) : _files;
  document.getElementById('files-count').textContent = `${filtered.length} of ${_files.length}`;
  _renderFilesTable(filtered);
}

function sortTable(which, col) {
  const key = which + '.' + col;
  _sortStates[key] = !_sortStates[key];
  const asc = _sortStates[key];
  if (which === 'routes') {
    _routes.sort((a,b) => {
      const av = a[col]||'', bv = b[col]||'';
      return asc ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1);
    });
    _renderRoutesTable(_routes);
  } else {
    _files.sort((a,b) => {
      const av = a[col]||0, bv = b[col]||0;
      return asc ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1);
    });
    _renderFilesTable(_files);
  }
}

// ════════════════════════════════════════════════════════════
//  Issues
// ════════════════════════════════════════════════════════════
let _issues = [];
function renderIssues(issues) {
  _issues = issues;
  _renderIssuesList(issues);
}

function _renderIssuesList(issues) {
  const el = document.getElementById('issues-list');
  document.getElementById('issues-count').textContent = `${issues.length} issues`;
  if (!issues.length) {
    el.innerHTML = '<div style="padding:40px;text-align:center;color:var(--muted)">✅ No issues found</div>';
    return;
  }
  el.innerHTML = issues.map(i => {
    const sevClass = `sev-${i.severity}`;
    const meta = [i.file, i.line ? `line ${i.line}` : ''].filter(Boolean).join(' · ');
    return `<div class="issue-row" onclick="inspectFile('${i.file}',${i.line||0})">
      <div class="issue-sev ${sevClass}"></div>
      <div class="issue-body">
        <div class="issue-msg">${i.message}</div>
        <div class="issue-meta">${meta} · <span style="color:var(--muted)">${i.type||''}</span></div>
        ${i.suggestion ? `<div class="issue-suggest">💡 ${i.suggestion}</div>` : ''}
      </div>
    </div>`;
  }).join('');
}

function filterIssues(q) {
  q = (document.getElementById('issues-filter')?.value || '').toLowerCase();
  const showErr  = document.getElementById('sev-error')?.checked ?? true;
  const showWarn = document.getElementById('sev-warning')?.checked ?? true;
  const showInfo = document.getElementById('sev-info')?.checked ?? true;
  const filtered = _issues.filter(i => {
    if (i.severity === 'error'   && !showErr)  return false;
    if (i.severity === 'warning' && !showWarn) return false;
    if (i.severity === 'info'    && !showInfo) return false;
    if (!q) return true;
    return (i.message||'').toLowerCase().includes(q) ||
           (i.file||'').toLowerCase().includes(q);
  });
  _renderIssuesList(filtered);
}

// ════════════════════════════════════════════════════════════
//  Services
// ════════════════════════════════════════════════════════════
async function loadServices() {
  try {
    const res = await fetch('/sys/api/services');
    const data = await res.json();
    const svcs = data.services || [];
    document.getElementById('cnt-services').textContent = svcs.length;
    document.getElementById('services-count').textContent = `${svcs.filter(s=>s.status==='running').length} running`;
    const grid = document.getElementById('services-grid');
    if (!svcs.length) {
      grid.innerHTML = '<div style="padding:40px;color:var(--muted)">No running services detected.</div>';
      return;
    }
    grid.innerHTML = svcs.map(s => `
      <div class="svc-card ${s.status}">
        <div class="svc-name">${s.name}</div>
        <div class="svc-meta">
          <span class="svc-badge ${s.status}">${s.status}</span>
          ${s.pid ? `PID: <b>${s.pid}</b>` : ''}
          ${s.port ? `Port: <b>${s.port}</b>` : ''}
          ${s.entry_point ? `Entry: <code>${s.entry_point}</code>` : ''}
        </div>
        ${s.port ? `
        <div class="svc-actions">
          <a class="svc-btn" href="http://localhost:${s.port}" target="_blank">🌐 Open</a>
        </div>` : ''}
      </div>
    `).join('');
  } catch(e) {
    document.getElementById('services-grid').innerHTML =
      `<div style="padding:20px;color:var(--red)">Error loading services: ${e}</div>`;
  }
}

// ════════════════════════════════════════════════════════════
//  D3 Graph
// ════════════════════════════════════════════════════════════
const NODE_COLORS = {
  route:'#7c3aed', function:'#2563eb', handler:'#059669',
  file:'#0891b2', external:'#dc2626', flask:'#6366f1',
  template:'#d97706', orphan:'#4b5563', unknown:'#4b5563',
};

function _nodeColor(d) {
  if (d.status === 'orphan') return NODE_COLORS.orphan;
  return NODE_COLORS[d.type] || '#6b7280';
}

function buildGraph(graphData) {
  _graphData = graphData;
  _renderGraph();
}

function _visibleNodes(level) {
  if (!_graphData) return {nodes:[], edges:[]};
  let nodes = _graphData.nodes.filter(n => _activeFilters.has(n.type) ||
    (n.status === 'orphan' && _activeFilters.has('orphan')));

  if (level === 'overview') {
    // Only file-level and route nodes
    nodes = nodes.filter(n => n.type === 'file' || n.type === 'route');
  } else if (level === 'module') {
    // Routes + handlers, no deep utils
    nodes = nodes.filter(n => n.type === 'file' || n.type === 'route' ||
      (n.type === 'function' && n.group === 'handlers'));
  }
  // 'detail' = all nodes

  const nodeIds = new Set(nodes.map(n => n.id));
  const edges = _graphData.edges.filter(e =>
    nodeIds.has(e.source) && nodeIds.has(e.target) &&
    !(level === 'overview' && e.type === 'calls'));

  return {nodes, edges};
}

function _renderGraph() {
  const container = document.getElementById('graph-container');
  const w = container.clientWidth || 800;
  const h = container.clientHeight || 600;

  d3.select('#graph-svg').selectAll('*').remove();

  const {nodes, edges} = _visibleNodes(_zoomLevel);
  if (!nodes.length) return;

  // Clone for simulation
  const simNodes = nodes.map(n => ({...n}));
  const nodeById  = new Map(simNodes.map(n => [n.id, n]));
  const simEdges  = edges
    .map(e => ({...e, source: nodeById.get(e.source), target: nodeById.get(e.target)}))
    .filter(e => e.source && e.target);

  const svg = d3.select('#graph-svg')
    .attr('width', w).attr('height', h);

  // Arrow markers
  const defs = svg.append('defs');
  ['active','dead','orphan','imports'].forEach(t => {
    defs.append('marker')
      .attr('id', `arrow-${t}`)
      .attr('viewBox','0 -4 8 8').attr('refX',12).attr('refY',0)
      .attr('markerWidth',6).attr('markerHeight',6).attr('orient','auto')
      .append('path').attr('d','M0,-4L8,0L0,4')
      .attr('fill', t==='dead'?'#f85149':t==='orphan'?'#4b5563':t==='imports'?'#30363d':'#8b949e');
  });

  const zoom = d3.zoom().scaleExtent([0.1, 4])
    .on('zoom', e => g.attr('transform', e.transform));
  svg.call(zoom);

  const g = svg.append('g');

  // Edges
  const link = g.append('g').selectAll('line')
    .data(simEdges).join('line')
    .attr('stroke', d => d.type === 'imports' ? '#30363d' : d.status === 'dead' ? '#f85149' : '#444c56')
    .attr('stroke-width', d => d.type === 'calls' ? 1.5 : 1)
    .attr('stroke-dasharray', d => d.type === 'imports' ? '3,3' : d.status === 'dead' ? '4,2' : null)
    .attr('marker-end', d => `url(#arrow-${d.type === 'imports' ? 'imports' : d.status || 'active'})`);

  // Dead edge warning icon
  const deadEdgeLabels = g.append('g').selectAll('text')
    .data(simEdges.filter(e => e.status === 'dead')).join('text')
    .attr('font-size', 10).attr('fill', '#f85149').attr('text-anchor','middle').text('⚠');

  // Nodes
  const node = g.append('g').selectAll('g')
    .data(simNodes).join('g')
    .attr('cursor', 'pointer')
    .call(d3.drag()
      .on('start', (event, d) => {
        if (!event.active) _simulation.alphaTarget(0.3).restart();
        d.fx = d.x; d.fy = d.y;
      })
      .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
      .on('end', (event, d) => {
        if (!event.active) _simulation.alphaTarget(0);
        d.fx = null; d.fy = null;
      }))
    .on('click', (event, d) => { event.stopPropagation(); nodeClick(d); })
    .on('mouseover', (event, d) => showTooltip(event, d))
    .on('mousemove', (event) => moveTooltip(event))
    .on('mouseout', () => hideTooltip());

  // Node shape
  node.each(function(d) {
    const sel = d3.select(this);
    const color = _nodeColor(d);
    const r = d.type === 'route' ? 16 : d.type === 'file' ? 18 : 12;
    const isDead = d.status === 'orphan';

    if (d.type === 'file') {
      sel.append('rect')
        .attr('x', -r).attr('y', -r).attr('width', r*2).attr('height', r*2)
        .attr('rx', 4).attr('fill', color + '33').attr('stroke', color)
        .attr('stroke-width', isDead ? 1 : 1.5)
        .attr('stroke-dasharray', isDead ? '3,2' : null);
    } else if (d.type === 'route') {
      sel.append('rect')
        .attr('x', -r*1.8).attr('y', -r*0.7).attr('width', r*3.6).attr('height', r*1.4)
        .attr('rx', r*0.7).attr('fill', color + '33').attr('stroke', color)
        .attr('stroke-width', 1.5);
    } else {
      sel.append('circle')
        .attr('r', r).attr('fill', color + '33').attr('stroke', color)
        .attr('stroke-width', isDead ? 1 : 1.5)
        .attr('stroke-dasharray', isDead ? '3,2' : null);
    }

    // Label
    sel.append('text')
      .attr('dy', r + 12)
      .attr('text-anchor', 'middle')
      .attr('font-size', 9)
      .attr('fill', isDead ? '#6b7280' : '#8b949e')
      .text(d.label.length > 20 ? d.label.slice(0,18)+'…' : d.label);
  });

  // Simulation
  _simulation = d3.forceSimulation(simNodes)
    .force('link', d3.forceLink(simEdges).distance(d =>
      d.type === 'imports' ? 180 : d.source.type === 'route' ? 100 : 70).strength(0.4))
    .force('charge', d3.forceManyBody().strength(-200))
    .force('center', d3.forceCenter(w/2, h/2))
    .force('collide', d3.forceCollide(30))
    .on('tick', () => {
      link
        .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
      deadEdgeLabels
        .attr('x', d => (d.source.x + d.target.x)/2)
        .attr('y', d => (d.source.y + d.target.y)/2);
      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

  svg.on('click', () => {
    document.getElementById('graph-tooltip').style.display = 'none';
  });
}

function setZoom(level) {
  _zoomLevel = level;
  ['overview','module','detail'].forEach(l => {
    document.getElementById('zb-'+l).classList.toggle('active', l === level);
  });
  _renderGraph();
}

function toggleFilter(el) {
  const type = el.dataset.type;
  if (_activeFilters.has(type)) _activeFilters.delete(type);
  else _activeFilters.add(type);
  el.classList.toggle('active', _activeFilters.has(type));
  el.classList.toggle('inactive', !_activeFilters.has(type));
  _renderGraph();
}

function resetGraphView() {
  _renderGraph();
}

function showTooltip(event, d) {
  const tt = document.getElementById('graph-tooltip');
  document.getElementById('tt-type').textContent = (d.type || '').toUpperCase();
  document.getElementById('tt-name').textContent = d.label;
  document.getElementById('tt-file').textContent = d.file ? `${d.file}:${d.line||'?'}` : '';
  tt.style.display = 'block';
  moveTooltip(event);
}

function moveTooltip(event) {
  const container = document.getElementById('graph-container').getBoundingClientRect();
  const tt = document.getElementById('graph-tooltip');
  tt.style.left = (event.clientX - container.left + 12) + 'px';
  tt.style.top  = (event.clientY - container.top  + 12) + 'px';
}
function hideTooltip() { document.getElementById('graph-tooltip').style.display = 'none'; }

async function nodeClick(d) {
  if (d.file) {
    await inspectFile(d.file, d.line || 0);
  }
}

// ════════════════════════════════════════════════════════════
//  Inspector
// ════════════════════════════════════════════════════════════
async function inspectFile(relPath, focusLine) {
  if (!relPath) return;
  document.getElementById('inspector').classList.add('open');
  document.getElementById('insp-title').textContent = relPath.split('/').pop();
  document.getElementById('insp-meta').innerHTML =
    `<span class="insp-tag" style="background:var(--bg3);color:var(--blue)">${relPath}</span>
     ${focusLine ? `<span class="insp-tag" style="background:var(--bg3);color:var(--muted)">line ${focusLine}</span>` : ''}`;

  // Build action buttons
  const vscodeUri = `vscode://file/${location.hostname !== 'localhost'
    ? relPath
    : ('c:/Users/Echo/masterchief/' + relPath).replace(/\//g,'\\')}${focusLine ? `:${focusLine}` : ''}`;

  document.getElementById('insp-actions').innerHTML = `
    <a class="insp-btn primary" href="${vscodeUri}">✏️ Open in VS Code</a>
    <button class="insp-btn" onclick="copyPath('${relPath}')">📋 Copy Path</button>
    <a class="insp-btn" href="/sys/api/file?path=${encodeURIComponent(relPath)}" target="_blank">⬇ Raw</a>
  `;

  // Load content
  document.getElementById('insp-code').innerHTML =
    '<pre><code style="color:var(--muted);padding:20px">Loading…</code></pre>';

  try {
    const res  = await fetch(`/sys/api/file?path=${encodeURIComponent(relPath)}&line=${focusLine}`);
    const data = await res.json();
    if (data.error) {
      document.getElementById('insp-code').innerHTML =
        `<pre><code style="color:var(--red);padding:16px">Error: ${data.error}</code></pre>`;
      return;
    }

    const lang = {'.py':'python','.js':'javascript','.html':'html','.css':'css',
      '.json':'json','.yml':'yaml','.yaml':'yaml','.sh':'bash','.md':'markdown'}[
        '.' + relPath.split('.').pop()] || 'plaintext';

    const codeEl = document.createElement('code');
    codeEl.className = `language-${lang}`;
    codeEl.textContent = data.content;
    const pre = document.createElement('pre');
    pre.appendChild(codeEl);
    document.getElementById('insp-code').innerHTML = '';
    document.getElementById('insp-code').appendChild(pre);
    hljs.highlightElement(codeEl);

    // Scroll to focus line
    if (focusLine > 1) {
      setTimeout(() => {
        const lines = pre.querySelectorAll
          ? null : null;
        // Approx scroll using line height ~18px
        pre.scrollTop = Math.max(0, (focusLine - 5) * 18);
      }, 50);
    }

    loadSuggestions(relPath, data);
  } catch(e) {
    document.getElementById('insp-code').innerHTML =
      `<pre><code style="color:var(--red);padding:16px">Network error: ${e}</code></pre>`;
  }
}

async function inspectRoute(r) {
  if (r && typeof r === 'string') r = JSON.parse(r);
  await inspectFile(r.file, r.line || 0);
}

function loadSuggestions(relPath, data) {
  const suggestions = [];
  if (_data) {
    const myIssues = (_data.issues || []).filter(i => i.file === relPath);
    myIssues.forEach(i => {
      suggestions.push({
        icon: i.severity === 'error' ? '❌' : i.severity === 'warning' ? '⚠️' : '💡',
        text: i.message,
        sub: i.suggestion,
      });
    });
  }
  if (data.lines > 1000) {
    suggestions.push({icon:'📐',text:'Large file',sub:'Consider refactoring into smaller modules.'});
  }

  document.getElementById('sug-count').textContent = suggestions.length;
  if (!suggestions.length) {
    document.getElementById('insp-sug-header').textContent = '✅ No issues in this file';
    document.getElementById('insp-sug-body').style.display = 'none';
    return;
  }
  document.getElementById('insp-sug-header').innerHTML =
    `💡 <span id="sug-count">${suggestions.length}</span> Suggestions <span id="sug-arrow">▶</span>`;
  document.getElementById('insp-sug-body').innerHTML =
    suggestions.map(s => `
      <div class="sug-item">
        <span class="sug-icon">${s.icon}</span>
        <div>
          <div>${s.text}</div>
          ${s.sub ? `<div style="color:var(--cyan);font-size:10px;margin-top:2px">${s.sub}</div>` : ''}
        </div>
      </div>`).join('');
}

function toggleSuggestions() {
  const body = document.getElementById('insp-sug-body');
  const arrow = document.getElementById('sug-arrow');
  const open = body.style.display !== 'none';
  body.style.display = open ? 'none' : 'block';
  if (arrow) arrow.textContent = open ? '▶' : '▼';
}

function closeInspector() {
  document.getElementById('inspector').classList.remove('open');
}

function copyPath(path) {
  navigator.clipboard.writeText(path).catch(() => {});
}

// ════════════════════════════════════════════════════════════
//  Export
// ════════════════════════════════════════════════════════════
function exportData() {
  if (!_data) { alert('Run a scan first.'); return; }
  const blob = new Blob([JSON.stringify(_data, null, 2)], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `masterchief-diagnostics-${new Date().toISOString().slice(0,10)}.json`;
  a.click();
}

// ════════════════════════════════════════════════════════════
//  Overlay
// ════════════════════════════════════════════════════════════
function showOverlay(msg) {
  document.getElementById('scan-msg').textContent = msg;
  document.getElementById('scan-overlay').classList.add('visible');
}
function hideOverlay() {
  document.getElementById('scan-overlay').classList.remove('visible');
}
</script>
</body>
</html>
"""
