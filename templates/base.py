"""
MasterChief HTML Templates

Contains all HTML templates used by the Flask application.
"""

# Base HTML template with navigation and styling
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>MasterChief - DevOps Platform</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:Arial,sans-serif;background:#1a1a1a;color:#e0e0e0;line-height:1.6;}
.container{max-width:1400px;margin:0 auto;padding:20px;}
header{background:#2d2d2d;padding:20px;margin-bottom:30px;border-bottom:3px solid #4CAF50;}
h1{color:#4CAF50;font-size:2.5em;margin-bottom:10px;}
.subtitle{color:#888;font-size:1.1em;}
nav{background:#252525;padding:15px;margin-bottom:30px;border-radius:8px;}
nav a{color:#4CAF50;text-decoration:none;margin-right:20px;padding:8px 15px;border-radius:5px;display:inline-block;transition:all 0.3s;}
nav a:hover,nav a.active{background:#4CAF50;color:#fff;}
.dashboard-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px;margin-bottom:30px;}
.card{background:#2d2d2d;padding:25px;border-radius:10px;border-left:4px solid #4CAF50;box-shadow:0 4px 6px rgba(0,0,0,0.3);}
.card h3{color:#4CAF50;margin-bottom:15px;font-size:1.4em;}
.stat-value{font-size:2.5em;font-weight:bold;color:#fff;margin:10px 0;}
.stat-label{color:#888;font-size:0.9em;text-transform:uppercase;}
.progress-bar{background:#1a1a1a;height:20px;border-radius:10px;overflow:hidden;margin:10px 0;}
.progress-fill{background:linear-gradient(90deg,#4CAF50,#8BC34A);height:100%;transition:width 0.3s;}
table{width:100%;border-collapse:collapse;margin-top:15px;}
th,td{padding:12px;text-align:left;border-bottom:1px solid #3a3a3a;}
th{background:#252525;color:#4CAF50;font-weight:bold;}
tr:hover{background:#333;}
.btn{background:#4CAF50;color:#fff;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;text-decoration:none;display:inline-block;margin:5px;transition:all 0.3s;}
.btn:hover{background:#45a049;transform:translateY(-2px);}
.btn-danger{background:#f44336;}
.btn-danger:hover{background:#da190b;}
.btn-warning{background:#ff9800;}
.btn-warning:hover{background:#e68900;}
.btn-info{background:#2196F3;}
.btn-info:hover{background:#0b7dda;}
.form-group{margin-bottom:20px;}
label{display:block;margin-bottom:8px;color:#4CAF50;font-weight:bold;}
input,textarea,select{width:100%;padding:12px;background:#1a1a1a;border:1px solid #3a3a3a;color:#e0e0e0;border-radius:5px;font-size:1em;}
input:focus,textarea:focus,select:focus{outline:none;border-color:#4CAF50;}
.section{background:#2d2d2d;padding:25px;border-radius:10px;margin-bottom:25px;}
.status-badge{padding:5px 12px;border-radius:15px;font-size:0.85em;font-weight:bold;}
.status-running{background:#4CAF50;color:#fff;}
.status-stopped{background:#f44336;color:#fff;}
.alert{padding:15px;margin-bottom:20px;border-radius:5px;border-left:4px solid;}
.alert-success{background:#1b5e20;border-color:#4CAF50;color:#c8e6c9;}
.alert-error{background:#b71c1c;border-color:#f44336;color:#ffcdd2;}
.alert-info{background:#0d47a1;border-color:#2196F3;color:#bbdefb;}
.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:1000;}
.modal-content{background:#2d2d2d;margin:50px auto;padding:30px;border-radius:10px;max-width:600px;position:relative;}
.close{position:absolute;top:15px;right:20px;font-size:30px;cursor:pointer;color:#888;}
.close:hover{color:#4CAF50;}
pre{background:#1a1a1a;padding:15px;border-radius:5px;overflow-x:auto;border-left:3px solid #4CAF50;}
code{color:#4CAF50;}
.file-upload{border:2px dashed #4CAF50;padding:40px;text-align:center;border-radius:10px;cursor:pointer;transition:all 0.3s;}
.file-upload:hover{background:#252525;border-color:#8BC34A;}
</style>
</head>
<body>
<div class="container">
<header>
<h1>⚡ MasterChief</h1>
<p class="subtitle">DevOps Automation Platform</p>
<div style="position:absolute;right:20px;top:24px;">
    <label style="color:#ccc;font-size:0.9em;">Language: <select id="langSelect" style="background:#1a1a1a;color:#eee;border:1px solid #333;padding:6px;border-radius:6px;"><option value="en">English</option><option value="es">Español</option></select></label>
    </div>
</header>
<nav>
<a href="/" class="{{ 'active' if request.path=='/' else '' }}">Dashboard</a>
<a href="/echo-chat" class="{{ 'active' if '/echo-chat' in request.path else '' }}">🌙 Echo Chat</a>
<a href="/scripts" class="{{ 'active' if '/scripts' in request.path else '' }}">Scripts</a>
<a href="/processes" class="{{ 'active' if '/processes' in request.path else '' }}">Processes</a>
<a href="/services" class="{{ 'active' if '/services' in request.path else '' }}">Services</a>
<a href="/addons" class="{{ 'active' if '/addons' in request.path and '/modules' not in request.path else '' }}">Addons</a>
<a href="/modules" class="{{ 'active' if request.path=='/modules' else '' }}">⚙️ Modules</a>
<a href="/addons/modules" class="{{ 'active' if '/addons/modules' in request.path else '' }}">🧩 Addon Modules</a>
<a href="/echo-train" class="{{ 'active' if '/echo-train' in request.path else '' }}">Training</a>
{% if ui_modules is defined %}{% for _mod_name, _mod in ui_modules.items() %}<a href="{{ _mod.url }}" class="{{ 'active' if _mod.url in request.path else '' }}" title="Addon Module: {{ _mod_name }}">{{ _mod.icon }} {{ _mod_name }}</a>
{% endfor %}{% endif %}
</nav>
{% with messages=get_flashed_messages(with_categories=true) %}
{% if messages %}
{% for category,message in messages %}
<div class="alert alert-{{ category }}">{{ message }}</div>
{% endfor %}
{% endif %}
{% endwith %}
{% block content %}{% endblock %}
</div>
<script>
function confirmDelete(item){return confirm('Are you sure you want to delete '+item+'?');}
function openModal(modalId){document.getElementById(modalId).style.display='block';}
function closeModal(modalId){document.getElementById(modalId).style.display='none';}
function refreshStats(){fetch('/api/stats').then(r=>r.json()).then(data=>{
document.getElementById('cpu-value').textContent=data.cpu.percent.toFixed(1)+'%';
document.getElementById('cpu-progress').style.width=data.cpu.percent+'%';
document.getElementById('mem-value').textContent=data.memory.percent.toFixed(1)+'%';
document.getElementById('mem-progress').style.width=data.memory.percent+'%';
document.getElementById('disk-value').textContent=data.disk.percent.toFixed(1)+'%';
document.getElementById('disk-progress').style.width=data.disk.percent+'%';
}).catch(err=>console.error('Failed to refresh stats:',err));}
setInterval(refreshStats,5000);
function refreshIndex(){
        fetch('/scripts/refresh_index',{method:'POST'}).then(async r => {
        // Training UI helpers
        function loadTrainJobs() {
            fetch('/api/echo/train_list').then(r => r.json()).then(j => {
                const jobs = j.jobs || [];
                const el = document.getElementById('trainingJobsList');
                if (!el) return;
                el.innerHTML = '';
                jobs.forEach(job => {
                    const div = document.createElement('div');
                    div.style.border = '1px solid #444'; div.style.padding = '8px'; div.style.margin = '6px 0';
                    div.innerHTML = `<b>${job.id}</b> - ${job.status} - <button onclick="viewLog('${job.id}')">Log</button> <button onclick="cancelJob('${job.id}')">Cancel</button>`;
                    el.appendChild(div);
                });
            }).catch(console.error);
        }
        function startTrain(event) {
            event.preventDefault();
            const form = document.getElementById('trainForm');
            const fd = new FormData(form);
            const body = {};
            form.querySelectorAll('input,select').forEach(i => { if (i.name) body[i.name] = i.value });
            fetch('/api/echo/train_model', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }).then(r => r.json()).then(j => {
                alert(JSON.stringify(j));
                loadTrainJobs();
            }).catch(e => { console.error(e); alert('Start failed') });
        }
        function viewLog(id) {
            fetch('/api/echo/train_status?job_id=' + encodeURIComponent(id)).then(r => r.json()).then(j => {
                const modal = document.getElementById('trainLogModal');
                document.getElementById('trainLogContent').textContent = j.log_tail || 'No log';
                modal.style.display = 'block';
            }).catch(console.error);
        }
        function cancelJob(id) {
            fetch('/api/echo/train_cancel', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ job_id: id }) }).then(r => r.json()).then(j => { alert(JSON.stringify(j)); loadTrainJobs(); }).catch(console.error);
        }
        setInterval(loadTrainJobs, 5000);
        if(r.status===401){
            // server requires admin token
            let token = prompt('Admin token required to refresh index:');
            if(!token) return alert('Cancelled');
            try{
                const r2 = await fetch('/scripts/refresh_index',{method:'POST',headers:{'X-ADMIN-TOKEN':token}});
                const j2 = await r2.json();
                if(j2.ok) location.reload(); else alert('Refresh failed: '+(j2.error||'unknown'));
            }catch(e){ alert('Refresh error: '+e); }
        } else {
            const j = await r.json();
            if(j.ok){ location.reload(); } else { alert('Refresh failed: '+(j.error||'unknown')); }
        }
    }).catch(e=>{ alert('Refresh error: '+e); });
}
</script>
</body>
</html>"""