"""
MasterChief Template Renderers

Contains functions for rendering HTML templates with proper content injection.
"""

from flask import render_template_string, request, get_flashed_messages
from templates.base import HTML_TEMPLATE
from templates.pages import (
    DASHBOARD_TEMPLATE,
    SCRIPTS_TEMPLATE,
    SCRIPT_VIEW_TEMPLATE,
    SCRIPT_EXECUTE_TEMPLATE,
    MODULES_TEMPLATE,
    ECHO_RESOURCES_TEMPLATE,
    ADDONS_MODULES_TEMPLATE,
    MODULE_MANAGER_TEMPLATE,
    ADDONS_MODULE_CONFIG_TEMPLATE,
    ECHO_TRAINING_TEMPLATE
)


def render_dashboard(stats):
    """
    Render the dashboard page with system statistics.
    """
    return render_template_string(
        HTML_TEMPLATE.replace('{% block content %}{% endblock %}',
                            DASHBOARD_TEMPLATE.replace('{% extends "base.html" %}','')
                                             .replace('{% block content %}','')
                                             .replace('{% endblock %}','')),
        stats=stats,
        request=request,
        get_flashed_messages=get_flashed_messages
    )


def render_modules_page(enabled_modules, managers):
    """
    Render the modules management page.
    """
    return render_template_string(
        HTML_TEMPLATE.replace('{% block content %}{% endblock %}',
                            MODULES_TEMPLATE.replace('{% extends "base.html" %}','')
                                           .replace('{% block content %}','')
                                           .replace('{% endblock %}','')),
        enabled_modules=enabled_modules,
        managers=managers,
        request=request,
        get_flashed_messages=get_flashed_messages
    )


def render_scripts_page(scripts, categories):
    """
    Render the scripts management page.
    """
    return render_template_string(
        HTML_TEMPLATE.replace('{% block content %}{% endblock %}',
                            SCRIPTS_TEMPLATE.replace('{% extends "base.html" %}','')
                                           .replace('{% block content %}','')
                                           .replace('{% endblock %}','')),
        scripts=scripts,
        categories=categories,
        request=request,
        get_flashed_messages=get_flashed_messages
    )


def render_script_view(filename, content):
    """
    Render the script view page.
    """
    return render_template_string(
        HTML_TEMPLATE.replace('{% block content %}{% endblock %}',
                            SCRIPT_VIEW_TEMPLATE.replace('{% extends "base.html" %}','')
                                               .replace('{% block content %}','')
                                               .replace('{% endblock %}','')),
        filename=filename,
        content=content,
        request=request,
        get_flashed_messages=get_flashed_messages
    )


def render_script_execute(filename, result=None):
    """
    Render the script execution page.
    """
    return render_template_string(
        HTML_TEMPLATE.replace('{% block content %}{% endblock %}',
                            SCRIPT_EXECUTE_TEMPLATE.replace('{% extends "base.html" %}','')
                                                  .replace('{% block content %}','')
                                                  .replace('{% endblock %}','')),
        filename=filename,
        result=result,
        request=request,
        get_flashed_messages=get_flashed_messages
    )


def render_script_edit(content, filepath, b64path, message=None):
    """
    Render the script edit page.
    """
    # For now, return a placeholder - we'll need to extract SCRIPT_EDIT_TEMPLATE
    return render_template_string(
        HTML_TEMPLATE.replace('{% block content %}{% endblock %}',
                            '<div class="section"><h2>Edit Script: {{ filepath }}</h2><p>Edit functionality coming soon...</p></div>'),
        content=content,
        filepath=filepath,
        b64path=b64path,
        message=message,
        request=request,
        get_flashed_messages=get_flashed_messages
    )


def render_resources_page():
    """
    Render the resources management page.
    """
    return render_template_string(
        HTML_TEMPLATE.replace('{% block content %}{% endblock %}',
                            ECHO_RESOURCES_TEMPLATE.replace('{% extends "base.html" %}','')
                                                  .replace('{% block content %}','')
                                                  .replace('{% endblock %}','')),
        request=request,
        get_flashed_messages=get_flashed_messages
    )


def render_addons_modules_page(installed_modules, ui_modules=None):
    """
    Render the addons modules management page.
    """
    if ui_modules is None:
        ui_modules = {}
    return render_template_string(
        HTML_TEMPLATE.replace('{% block content %}{% endblock %}',
                            ADDONS_MODULES_TEMPLATE.replace('{% extends "base.html" %}','')
                                                  .replace('{% block content %}','')
                                                  .replace('{% endblock %}','')),
        installed_modules=installed_modules,
        ui_modules=ui_modules,
        request=request,
        get_flashed_messages=get_flashed_messages
    )


def render_module_manager_page(module):
    """
    Render the module manager page for a specific module.
    """
    return render_template_string(
        HTML_TEMPLATE.replace('{% block content %}{% endblock %}',
                            MODULE_MANAGER_TEMPLATE.replace('{% extends "base.html" %}','')
                                                  .replace('{% block content %}','')
                                                  .replace('{% endblock %}','')),
        module=module,
        request=request,
        get_flashed_messages=get_flashed_messages
    )


def render_addons_module_config_page(module_name, config_file, content):
    """
    Render the addons module configuration page.
    """
    return render_template_string(
        HTML_TEMPLATE.replace('{% block content %}{% endblock %}',
                            ADDONS_MODULE_CONFIG_TEMPLATE.replace('{% extends "base.html" %}','')
                                                     .replace('{% block content %}','')
                                                     .replace('{% endblock %}','')),
        module_name=module_name,
        config_file=config_file,
        content=content,
        request=request,
        get_flashed_messages=get_flashed_messages
    )


def render_echo_training_page():
    """Render the Echo Training Studio page."""
    ECHO_TRAINING_TEMPLATE_INLINE = """
<style>
/* ── Training Studio layout ───────────────────────────────────────────── */
.ts-wrap { display:grid; grid-template-columns:420px 1fr; gap:20px; margin-top:6px; }
@media(max-width:900px){ .ts-wrap { grid-template-columns:1fr; } }

/* tabs */
.ts-tabs { display:flex; gap:0; border-bottom:2px solid #333; margin-bottom:14px; }
.ts-tab  { padding:7px 18px; font-size:.88rem; cursor:pointer; border-radius:6px 6px 0 0;
           color:#888; border:1px solid transparent; border-bottom:none; background:none; }
.ts-tab.active { color:#eee; background:#1e1e2e; border-color:#333; margin-bottom:-2px; }
.ts-panel { display:none; } .ts-panel.active { display:block; }

/* form controls */
.ts-field { display:flex; flex-direction:column; gap:4px; margin-bottom:12px; }
.ts-field label { font-size:.82rem; color:#aaa; }
.ts-input, .ts-select, .ts-textarea {
  background:#121212; border:1px solid #444; color:#eee;
  padding:6px 10px; border-radius:5px; font-size:.85rem; width:100%; box-sizing:border-box;
}
.ts-input:focus,.ts-select:focus,.ts-textarea:focus { border-color:#7ec8e3; outline:none; }
.ts-textarea { font-family:monospace; resize:vertical; min-height:70px; }
.ts-row { display:flex; gap:10px; }
.ts-row .ts-field { flex:1; }
.ts-hint { font-size:.75rem; color:#666; margin-top:2px; }
.ts-adv-toggle { font-size:.78rem; color:#7ec8e3; cursor:pointer; margin-bottom:10px; display:inline-block; }
.ts-adv { display:none; }
.ts-adv.open { display:block; }
.ts-section-title { font-size:.8rem; font-weight:600; color:#777; text-transform:uppercase;
                    letter-spacing:.06em; margin-bottom:8px; margin-top:4px; }

/* file picker list */
.ts-file-list { max-height:160px; overflow-y:auto; border:1px solid #333; border-radius:5px;
                background:#0d0d0d; padding:4px 0; margin-top:4px; }
.ts-file-item { padding:4px 10px; font-size:.8rem; font-family:monospace; color:#ccc;
                cursor:pointer; display:flex; justify-content:space-between; align-items:center;
                border-bottom:1px solid #1a1a1a; }
.ts-file-item:hover,.ts-file-item.selected { background:#252535; color:#7ec8e3; }
.ts-file-item .ts-fsize { color:#555; font-size:.72rem; }

/* upload drop zone */
.ts-dropzone { border:2px dashed #444; border-radius:8px; padding:24px; text-align:center;
               color:#777; cursor:pointer; transition:border-color .2s,color .2s; margin-bottom:10px; }
.ts-dropzone.drag-over,.ts-dropzone:hover { border-color:#7ec8e3; color:#7ec8e3; }
.ts-dropzone input[type=file] { display:none; }

/* quality radio */
.ts-quality-row { display:flex; gap:10px; flex-wrap:wrap; }
.ts-qbtn { padding:4px 12px; border:1px solid #444; border-radius:20px; font-size:.78rem;
           cursor:pointer; color:#aaa; background:none; transition:all .15s; }
.ts-qbtn:hover,.ts-qbtn.sel { border-color:#7ec8e3; color:#7ec8e3; background:#0d1f2a; }

/* right panel */
.ts-right { display:flex; flex-direction:column; gap:14px; }
.ts-jobs-panel { background:#1e1e2e; border:1px solid #333; border-radius:10px; padding:16px; }
.ts-jobs-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }
.ts-jobs-header h3 { margin:0; font-size:1rem; }

/* job rows */
.ts-job { border:1px solid #2a2a2a; border-radius:6px; padding:10px 12px; margin-bottom:8px;
          background:#16161e; cursor:pointer; transition:border-color .15s; }
.ts-job:hover { border-color:#444; }
.ts-job-top { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.ts-job-id  { font-family:monospace; font-size:.75rem; color:#666; }
.ts-job-model { font-size:.78rem; color:#aaa; flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.ts-job-status { font-size:.75rem; font-weight:600; padding:2px 8px; border-radius:10px; white-space:nowrap; }
.st-queued   { background:#2d2d2d; color:#888; }
.st-running  { background:#0d2040; color:#7ec8e3; }
.st-done     { background:#1b4d2e; color:#4CAF50; }
.st-error,.st-failed { background:#3a1010; color:#f55; }
.st-cancelled{ background:#2d2d2d; color:#888; }
.ts-job-meta { font-size:.74rem; color:#555; margin-top:3px; }
.ts-job-actions { display:flex; gap:6px; margin-top:6px; }
.ts-log-box  { display:none; margin-top:8px; background:#0a0a0a; border:1px solid #222;
               border-radius:5px; padding:8px; max-height:260px; overflow-y:auto; }
.ts-log-box pre{ margin:0; font-size:.73rem; color:#99c; white-space:pre-wrap; word-break:break-all; }
.ts-log-box.open { display:block; }

/* output models list */
.ts-models-panel { background:#1e1e2e; border:1px solid #333; border-radius:10px; padding:16px; }

/* spinner */
.ts-spinner { display:inline-block; width:12px; height:12px; border:2px solid #444;
              border-top-color:#7ec8e3; border-radius:50%; animation:ts-spin .7s linear infinite; margin-right:6px; }
@keyframes ts-spin{ to{ transform:rotate(360deg); } }

/* status bar */
#ts-statusbar { font-size:.8rem; color:#aaa; padding:6px 0; min-height:1.4em; }
</style>

<div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">
  <h2 style="margin:0;">🎓 Echo Training Studio</h2>
  <span id="ts-statusbar"></span>
</div>

<div class="ts-wrap">

<!-- ══════ LEFT: config panel ══════ -->
<div class="ts-left">

  <!-- tabs -->
  <div class="ts-tabs">
    <button class="ts-tab active" onclick="tsTab(this,'tab-finetune')">🔧 Fine-tune Job</button>
    <button class="ts-tab"        onclick="tsTab(this,'tab-feedback')">💬 Feedback Pair</button>
    <button class="ts-tab"        onclick="tsTab(this,'tab-upload')">📤 Upload Data</button>
  </div>

  <!-- ─── Tab 1: Fine-tune Job ─── -->
  <div id="tab-finetune" class="ts-panel active">

    <div class="ts-section-title">Base Model</div>
    <div class="ts-field">
      <label>Select from discovered models</label>
      <select id="ft-model-sel" class="ts-select" onchange="ftPickModel(this.value)">
        <option value="">— loading… —</option>
      </select>
      <input id="ft-model-path" class="ts-input" placeholder="or type full path: models/my.gguf" style="margin-top:4px;">
      <span class="ts-hint">Model must exist on the server filesystem.</span>
    </div>

    <div class="ts-section-title">Training Data</div>
    <div class="ts-field">
      <label>Select a training file <span style="color:#555;">(from data/echo_training/)</span></label>
      <div id="ft-file-list" class="ts-file-list"><div style="padding:8px;color:#555">Loading…</div></div>
      <input id="ft-file-sel" class="ts-input" placeholder="or type filename: my_data.jsonl" style="margin-top:6px;">
      <span class="ts-hint">Accepts .jsonl (one {"prompt","completion"} per line) or .txt.</span>
    </div>

    <div class="ts-section-title">Engine &amp; Basic Settings</div>
    <div class="ts-row">
      <div class="ts-field">
        <label>Engine</label>
        <select id="ft-engine" class="ts-select" onchange="ftEngineChange()">
          <option value="stub">stub (dry-run, safe)</option>
          <option value="peft">peft / LoRA (GPU)</option>
        </select>
      </div>
      <div class="ts-field">
        <label>Output name</label>
        <input id="ft-output" class="ts-input" placeholder="auto-generated if blank">
      </div>
    </div>
    <div id="ft-peft-warn" style="display:none;background:#2a1800;border:1px solid #6a3800;border-radius:5px;padding:8px;font-size:.8rem;color:#f90;margin-bottom:10px;">
      ⚠️ PEFT requires <code>transformers</code>, <code>peft</code>, <code>accelerate</code>, <code>bitsandbytes</code> and a CUDA GPU.
      The server will return an error if these are missing.
    </div>

    <span class="ts-adv-toggle" onclick="tsToggleAdv()">▶ Advanced hyperparameters</span>
    <div id="ft-adv" class="ts-adv">
      <div class="ts-row">
        <div class="ts-field"><label>Epochs</label><input id="ft-epochs" class="ts-input" type="number" value="1" min="1" max="100"></div>
        <div class="ts-field"><label>Batch size</label><input id="ft-batch" class="ts-input" type="number" value="8" min="1" max="256"></div>
      </div>
      <div class="ts-row">
        <div class="ts-field"><label>Learning rate</label><input id="ft-lr" class="ts-input" type="text" value="0.0001"></div>
        <div class="ts-field"><label>Warmup ratio</label><input id="ft-warmup" class="ts-input" type="text" value="0.05" placeholder="0.0–1.0"></div>
      </div>
      <div class="ts-row">
        <div class="ts-field"><label>Max sequence length</label><input id="ft-maxlen" class="ts-input" type="number" value="512" min="64" max="8192"></div>
        <div class="ts-field"><label>Gradient accum. steps</label><input id="ft-grad-accum" class="ts-input" type="number" value="1" min="1" max="64"></div>
      </div>
      <div class="ts-field">
        <label>LoRA rank (peft only)</label>
        <input id="ft-lora-rank" class="ts-input" type="number" value="8" min="1" max="256">
      </div>
    </div>

    <button class="btn btn-primary" style="width:100%;margin-top:14px;" onclick="ftStartJob()">
      🚀 Start Training Job
    </button>
    <div id="ft-start-status" style="font-size:.8rem;color:#aaa;margin-top:6px;min-height:1.2em;"></div>
  </div>

  <!-- ─── Tab 2: Feedback Pair ─── -->
  <div id="tab-feedback" class="ts-panel">
    <p style="font-size:.85rem;color:#aaa;margin-top:0;">
      Teach Echo directly from a single conversation example. This is immediate in-memory training (no job queue).
    </p>
    <div class="ts-field">
      <label>User message</label>
      <textarea id="fb-user" class="ts-textarea" placeholder="What the user said…" rows="3"></textarea>
    </div>
    <div class="ts-field">
      <label>Bot response <span style="color:#555;">(ideal / corrected)</span></label>
      <textarea id="fb-bot" class="ts-textarea" placeholder="What Echo should have responded…" rows="4"></textarea>
    </div>
    <div class="ts-field">
      <label>Quality rating</label>
      <div class="ts-quality-row">
        <button class="ts-qbtn sel" data-q="excellent" onclick="fbQuality(this)">⭐⭐⭐ Excellent</button>
        <button class="ts-qbtn"     data-q="good"      onclick="fbQuality(this)">⭐⭐ Good</button>
        <button class="ts-qbtn"     data-q="acceptable"onclick="fbQuality(this)">⭐ Acceptable</button>
        <button class="ts-qbtn"     data-q="poor"      onclick="fbQuality(this)">👎 Poor</button>
      </div>
    </div>
    <button class="btn btn-primary" style="width:100%;margin-top:10px;" onclick="fbSubmit()">
      💾 Submit Feedback Pair
    </button>
    <div id="fb-status" style="font-size:.8rem;color:#aaa;margin-top:6px;min-height:1.2em;"></div>
  </div>

  <!-- ─── Tab 3: Upload Data ─── -->
  <div id="tab-upload" class="ts-panel">
    <p style="font-size:.85rem;color:#aaa;margin-top:0;">
      Upload training data or persona files to the server. They will be saved to <code>data/echo_training/</code>.
    </p>
    <div class="ts-dropzone" id="ul-dropzone" onclick="document.getElementById('ul-file-input').click()"
         ondragover="event.preventDefault();this.classList.add('drag-over');"
         ondragleave="this.classList.remove('drag-over');"
         ondrop="ulDrop(event)">
      <input type="file" id="ul-file-input" accept=".jsonl,.json,.txt,.md,.csv" onchange="ulPicked(this.files)">
      <div style="font-size:2rem;margin-bottom:6px;">📂</div>
      <div style="font-size:.9rem;">Drop files here or <b>click to browse</b></div>
      <div style="font-size:.78rem;margin-top:4px;">.jsonl · .json · .txt · .md · .csv</div>
    </div>
    <div class="ts-field">
      <label>File type</label>
      <select id="ul-type" class="ts-select">
        <option value="training">training data (rows ingested into echo_training/)</option>
        <option value="persona">persona / system prompt</option>
      </select>
    </div>
    <div id="ul-queue" style="font-size:.82rem;color:#aaa;margin-bottom:6px;"></div>
    <button class="btn btn-success" onclick="ulUploadAll()" id="ul-btn" disabled>⬆ Upload All</button>
    <div id="ul-status" style="font-size:.8rem;color:#aaa;margin-top:6px;min-height:1.2em;"></div>
  </div>

</div><!-- /ts-left -->

<!-- ══════ RIGHT: jobs + output models ══════ -->
<div class="ts-right">

  <div class="ts-jobs-panel">
    <div class="ts-jobs-header">
      <h3>📋 Training Jobs</h3>
      <div style="display:flex;gap:8px;align-items:center;">
        <span id="ts-jobs-live" style="font-size:.75rem;color:#555;"></span>
        <button class="btn btn-sm btn-secondary" onclick="tsLoadJobs()">↻ Refresh</button>
      </div>
    </div>
    <div id="ts-jobs-list"><em style="color:#555;font-size:.85rem;">No jobs yet.</em></div>
  </div>

  <div class="ts-models-panel">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
      <h3 style="margin:0;font-size:1rem;">🧠 Available Models</h3>
      <button class="btn btn-sm btn-secondary" onclick="tsLoadModels()">↻ Refresh</button>
    </div>
    <div id="ts-models-list" style="font-size:.82rem;color:#aaa;"></div>
  </div>

</div><!-- /ts-right -->
</div><!-- /ts-wrap -->

<script>
// ════════════════════════════════════════════════════════════════════════
//  Echo Training Studio — client-side logic
// ════════════════════════════════════════════════════════════════════════

// ── utils ────────────────────────────────────────────────────────────────
function tsStatus(msg, color){
  const el = document.getElementById('ts-statusbar');
  if(el){ el.textContent = msg; el.style.color = color||'#aaa'; }
}

function tsTab(btn, panelId){
  document.querySelectorAll('.ts-tab').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.ts-panel').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById(panelId).classList.add('active');
}

function tsToggleAdv(){
  const el = document.getElementById('ft-adv');
  const tog = document.querySelector('.ts-adv-toggle');
  el.classList.toggle('open');
  tog.textContent = el.classList.contains('open') ? '▼ Advanced hyperparameters' : '▶ Advanced hyperparameters';
}

function ftEngineChange(){
  const eng = document.getElementById('ft-engine').value;
  document.getElementById('ft-peft-warn').style.display = (eng==='peft') ? '' : 'none';
}

// ── models ───────────────────────────────────────────────────────────────
function tsLoadModels(){
  fetch('/api/echo/models').then(r=>r.json()).then(j=>{
    const models = j.models || [];
    const sel = document.getElementById('ft-model-sel');
    sel.innerHTML = '<option value="">— select a model —</option>' +
      models.map(m=>`<option value="${m}">${m}</option>`).join('');
    const listEl = document.getElementById('ts-models-list');
    if(!models.length){
      listEl.innerHTML = '<em style="color:#555">No .gguf files found in models/</em>';
      return;
    }
    listEl.innerHTML = models.map(m=>`<div style="padding:3px 0;border-bottom:1px solid #222;font-family:monospace;">${m}</div>`).join('');
  }).catch(e=>{ tsStatus('Models error: '+e,'#f55'); });
}

function ftPickModel(val){
  if(val) document.getElementById('ft-model-path').value = val;
}

// ── training files ────────────────────────────────────────────────────────
function tsLoadTrainingFiles(){
  const el = document.getElementById('ft-file-list');
  el.innerHTML = '<div style="padding:8px;color:#555">Loading…</div>';
  fetch('/api/echo/training_files').then(r=>r.json()).then(j=>{
    const files = j.files || [];
    if(!files.length){ el.innerHTML='<div style="padding:8px;color:#555">No training files yet. Upload some first.</div>'; return; }
    el.innerHTML = files.map(f=>`
      <div class="ts-file-item" onclick="ftPickFile('${f.name}', this)" data-name="${f.name}">
        <span>${f.name}</span>
        <span class="ts-fsize">${(f.size/1024).toFixed(1)}KB</span>
      </div>`).join('');
  }).catch(e=>{ el.innerHTML='<div style="padding:8px;color:#f55">Error: '+e+'</div>'; });
}

function ftPickFile(name, row){
  document.querySelectorAll('.ts-file-item').forEach(r=>r.classList.remove('selected'));
  row.classList.add('selected');
  document.getElementById('ft-file-sel').value = name;
}

// ── start fine-tune job ───────────────────────────────────────────────────
function ftStartJob(){
  const model = document.getElementById('ft-model-path').value.trim() ||
                document.getElementById('ft-model-sel').value;
  const tfile = document.getElementById('ft-file-sel').value.trim();
  const engine= document.getElementById('ft-engine').value;
  const output= document.getElementById('ft-output').value.trim();
  const epochs= parseInt(document.getElementById('ft-epochs').value)||1;
  const batch = parseInt(document.getElementById('ft-batch').value)||8;
  const lr    = parseFloat(document.getElementById('ft-lr').value)||0.0001;

  if(!model){ document.getElementById('ft-start-status').textContent='⚠ Select or enter a model path.'; return; }
  if(!tfile){ document.getElementById('ft-start-status').textContent='⚠ Select or enter a training file.'; return; }

  const payload = { model, training_file: tfile, engine, output_name: output||undefined,
                    epochs, batch_size: batch, lr };

  document.getElementById('ft-start-status').innerHTML='<span class="ts-spinner"></span>Submitting…';

  fetch('/api/echo/train_model', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})
    .then(r=>r.json()).then(j=>{
      if(j.ok || j.job_id){
        document.getElementById('ft-start-status').textContent = '✅ Job started: '+j.job_id;
        tsStatus('Job '+j.job_id+' queued','#4CAF50');
        setTimeout(tsLoadJobs, 800);
      } else {
        document.getElementById('ft-start-status').textContent = '❌ '+(j.error||JSON.stringify(j));
        tsStatus('Start failed','#f55');
      }
    }).catch(e=>{ document.getElementById('ft-start-status').textContent='Error: '+e; });
}

// ── feedback pair ─────────────────────────────────────────────────────────
let _fbQuality = 'excellent';
function fbQuality(btn){
  document.querySelectorAll('.ts-qbtn').forEach(b=>b.classList.remove('sel'));
  btn.classList.add('sel');
  _fbQuality = btn.dataset.q;
}

function fbSubmit(){
  const user = document.getElementById('fb-user').value.trim();
  const bot  = document.getElementById('fb-bot').value.trim();
  if(!user||!bot){ document.getElementById('fb-status').textContent='⚠ Fill both user and bot fields.'; return; }
  document.getElementById('fb-status').innerHTML='<span class="ts-spinner"></span>Saving…';
  fetch('/api/echo/train',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({user_message:user,bot_response:bot,quality:_fbQuality})})
    .then(r=>r.json()).then(j=>{
      if(j.success||j.ok){
        document.getElementById('fb-status').textContent='✅ Feedback saved!';
        document.getElementById('fb-user').value=''; document.getElementById('fb-bot').value='';
      } else {
        document.getElementById('fb-status').textContent='❌ '+(j.error||JSON.stringify(j));
      }
    }).catch(e=>{ document.getElementById('fb-status').textContent='Error: '+e; });
}

// ── upload ────────────────────────────────────────────────────────────────
let _ulFiles = [];
function ulDrop(e){
  e.preventDefault();
  document.getElementById('ul-dropzone').classList.remove('drag-over');
  ulPicked(e.dataTransfer.files);
}
function ulPicked(files){
  _ulFiles = Array.from(files);
  const queue = document.getElementById('ul-queue');
  queue.textContent = _ulFiles.length ? 'Ready to upload: '+_ulFiles.map(f=>f.name).join(', ') : '';
  document.getElementById('ul-btn').disabled = !_ulFiles.length;
}
function ulUploadAll(){
  if(!_ulFiles.length) return;
  const type = document.getElementById('ul-type').value;
  const statusEl = document.getElementById('ul-status');
  statusEl.innerHTML = '<span class="ts-spinner"></span>Uploading…';
  Promise.all(_ulFiles.map(file=>{
    const fd = new FormData(); fd.append('file',file); fd.append('type',type);
    return fetch('/api/echo/upload_ingest',{method:'POST',body:fd}).then(r=>r.json());
  })).then(results=>{
    const ok  = results.filter(r=>r.ok||r.saved);
    const err = results.filter(r=>!r.ok&&!r.saved);
    statusEl.textContent = '✅ '+ok.length+' uploaded'+(err.length?' | ❌ '+err.length+' failed':'');
    _ulFiles=[]; document.getElementById('ul-queue').textContent='';
    document.getElementById('ul-btn').disabled=true;
    tsLoadTrainingFiles();
  }).catch(e=>{ statusEl.textContent='Error: '+e; });
}

// ── jobs ──────────────────────────────────────────────────────────────────
let _tsJobsData = {};
let _tsAutoPoll = null;

function tsLoadJobs(){
  fetch('/api/echo/train_list').then(r=>r.json()).then(j=>{
    const jobs=(j.jobs||[]).slice().reverse();
    _tsJobsData={};
    jobs.forEach(job=>{ _tsJobsData[job.id]=job; });
    renderJobs(jobs);
    const running = jobs.filter(j=>['queued','running'].includes(j.status));
    if(running.length && !_tsAutoPoll){
      _tsAutoPoll = setInterval(tsPollRunning,3000);
      document.getElementById('ts-jobs-live').textContent='⬤ live polling';
    } else if(!running.length && _tsAutoPoll){
      clearInterval(_tsAutoPoll); _tsAutoPoll=null;
      document.getElementById('ts-jobs-live').textContent='';
    }
  }).catch(e=>{ tsStatus('Jobs error: '+e,'#f55'); });
}

function tsPollRunning(){
  const running = Object.values(_tsJobsData).filter(j=>['queued','running'].includes(j.status));
  if(!running.length){ clearInterval(_tsAutoPoll); _tsAutoPoll=null; document.getElementById('ts-jobs-live').textContent=''; return; }
  running.forEach(job=>{
    fetch('/api/echo/train_status?job_id='+encodeURIComponent(job.id))
      .then(r=>r.json()).then(j=>{
        if(j.job){ _tsJobsData[job.id]=j.job; }
        // update just this job's status badge
        const badge = document.getElementById('ts-badge-'+job.id);
        if(badge && j.job){ badge.textContent=j.job.status; badge.className='ts-job-status st-'+j.job.status; }
        // update log if open
        const logEl = document.getElementById('ts-log-'+job.id);
        if(logEl && logEl.classList.contains('open') && j.log_tail){
          logEl.querySelector('pre').textContent = j.log_tail;
          logEl.scrollTop = logEl.scrollHeight;
        }
      }).catch(()=>{});
  });
}

function renderJobs(jobs){
  const el = document.getElementById('ts-jobs-list');
  if(!jobs.length){ el.innerHTML='<em style="color:#555;font-size:.85rem;">No jobs yet. Start one from the Fine-tune tab.</em>'; return; }
  el.innerHTML = jobs.map(job=>{
    const sc = 'ts-job-status st-'+(job.status||'queued');
    const duration = job.started_at&&job.finished_at ? ((job.finished_at-job.started_at)/60).toFixed(1)+'m' : '';
    const m = (job.model||'').split(/[/\\\\]/).pop();
    const f = (job.training_file||'').split(/[/\\\\]/).pop();
    return `<div class="ts-job" onclick="tsToggleLog('${job.id}')">
      <div class="ts-job-top">
        <span class="ts-job-id">${job.id.slice(0,12)}</span>
        <span class="ts-job-model" title="${job.model||''}">${m||'—'}</span>
        <span id="ts-badge-${job.id}" class="${sc}">${job.status||'?'}</span>
      </div>
      <div class="ts-job-meta">data: ${f||'—'} &nbsp;|&nbsp; engine: ${job.engine||'—'} ${duration?'&nbsp;|&nbsp; time: '+duration:''}</div>
      <div class="ts-job-actions" onclick="event.stopPropagation()">
        <button class="btn btn-xs btn-secondary" onclick="tsViewLog('${job.id}')">📋 Logs</button>
        ${['queued','running'].includes(job.status) ? `<button class="btn btn-xs btn-danger" onclick="tsCancelJob('${job.id}')">✕ Cancel</button>` : ''}
      </div>
      <div class="ts-log-box" id="ts-log-${job.id}"><pre>(click Logs to load)</pre></div>
    </div>`;
  }).join('');
}

function tsToggleLog(id){
  const el = document.getElementById('ts-log-'+id);
  if(!el) return;
  el.classList.toggle('open');
  if(el.classList.contains('open')) tsViewLog(id);
}

function tsViewLog(id){
  const el = document.getElementById('ts-log-'+id);
  if(!el) return;
  el.classList.add('open');
  el.querySelector('pre').textContent = 'Loading…';
  fetch('/api/echo/train_status?job_id='+encodeURIComponent(id))
    .then(r=>r.json()).then(j=>{
      el.querySelector('pre').textContent = j.log_tail || '(no log output yet)';
      el.scrollTop = el.scrollHeight;
    }).catch(e=>{ el.querySelector('pre').textContent='Error: '+e; });
}

function tsCancelJob(id){
  if(!confirm('Cancel job '+id.slice(0,12)+'?')) return;
  fetch('/api/echo/train_cancel',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({job_id:id})})
    .then(r=>r.json()).then(j=>{
      tsStatus(j.ok?'Job cancelled':'Cancel failed: '+(j.error||'?'), j.ok?'#4CAF50':'#f55');
      setTimeout(tsLoadJobs,600);
    }).catch(e=>{ tsStatus('Error: '+e,'#f55'); });
}

// ── init ──────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded',()=>{
  tsLoadModels();
  tsLoadTrainingFiles();
  tsLoadJobs();
});
</script>
"""
    return render_template_string(
        HTML_TEMPLATE.replace('{% block content %}{% endblock %}', ECHO_TRAINING_TEMPLATE_INLINE),
        request=request,
        get_flashed_messages=get_flashed_messages
    )