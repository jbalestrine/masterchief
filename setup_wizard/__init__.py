"""Setup Wizard — first-run configuration for MasterChief."""

from flask import Blueprint, request, jsonify, render_template_string, session

_wizard_bp = Blueprint('setup_wizard', __name__, url_prefix='/setup')

_SETUP_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>MasterChief — Setup Wizard</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#1a1a1a;color:#e0e0e0;display:flex;align-items:center;justify-content:center;min-height:100vh}
.wizard{background:#232323;border:1px solid #3a3a3a;border-radius:12px;width:560px;padding:40px;box-shadow:0 8px 32px rgba(0,0,0,.4)}
.wizard h1{color:#4CAF50;font-size:24px;margin-bottom:8px}
.wizard p.sub{color:#888;margin-bottom:24px;font-size:14px}
.form-row{margin-bottom:16px}
.form-row label{display:block;font-weight:600;margin-bottom:6px;font-size:13px}
.form-row input,.form-row select{width:100%;padding:10px 12px;background:#1a1a1a;color:#e0e0e0;border:1px solid #3a3a3a;border-radius:4px;font-size:14px}
.form-row input:focus,.form-row select:focus{outline:none;border-color:#4CAF50}
.btn{background:#4CAF50;color:#fff;border:none;padding:12px 24px;border-radius:4px;font-size:14px;font-weight:600;cursor:pointer;width:100%;margin-top:8px}
.btn:hover{background:#8BC34A}
.msg{padding:10px;border-radius:4px;margin-bottom:16px;font-size:13px}
.msg.ok{background:#1b3a1b;color:#4CAF50;border:1px solid #2e7d32}
.msg.err{background:#3a1b1b;color:#f44336;border:1px solid #c62828}
</style>
</head>
<body>
<div class="wizard">
  <h1>MasterChief Setup</h1>
  <p class="sub">Configure your platform settings to get started.</p>
  {% if message %}<div class="msg {{ 'ok' if success else 'err' }}">{{ message }}</div>{% endif %}
  <form method="POST" action="/setup/configure">
    <div class="form-row"><label>Instance Name</label><input name="instance_name" value="{{ config.get('instance_name','MasterChief') }}" /></div>
    <div class="form-row"><label>Admin Email</label><input name="admin_email" type="email" value="{{ config.get('admin_email','') }}" placeholder="admin@example.com" /></div>
    <div class="form-row"><label>Default Port</label><input name="port" type="number" value="{{ config.get('port', 8888) }}" /></div>
    <div class="form-row"><label>Theme</label>
      <select name="theme">
        <option value="dark" {{ 'selected' if config.get('theme')=='dark' else '' }}>Dark (CAF)</option>
        <option value="light" {{ 'selected' if config.get('theme')=='light' else '' }}>Light</option>
      </select>
    </div>
    <div class="form-row"><label>Enable Auth Module</label>
      <select name="auth_enabled">
        <option value="true" {{ 'selected' if config.get('auth_enabled') else '' }}>Yes</option>
        <option value="false" {{ 'selected' if not config.get('auth_enabled') else '' }}>No</option>
      </select>
    </div>
    <button class="btn" type="submit">Save &amp; Continue</button>
  </form>
</div>
</body>
</html>"""

_config = {
    'instance_name': 'MasterChief',
    'admin_email': '',
    'port': 8888,
    'theme': 'dark',
    'auth_enabled': False,
    'setup_complete': False,
}


@_wizard_bp.route('/')
def wizard_index():
    return render_template_string(_SETUP_HTML, config=_config, message=None, success=False)


@_wizard_bp.route('/configure', methods=['POST'])
def configure():
    _config['instance_name'] = request.form.get('instance_name', 'MasterChief')
    _config['admin_email'] = request.form.get('admin_email', '')
    _config['port'] = int(request.form.get('port', 8888))
    _config['theme'] = request.form.get('theme', 'dark')
    _config['auth_enabled'] = request.form.get('auth_enabled') == 'true'
    _config['setup_complete'] = True

    # Persist to config.yml if available
    try:
        from pathlib import Path
        import json
        cfg_path = Path(__file__).resolve().parent.parent / 'data' / 'setup_config.json'
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        cfg_path.write_text(json.dumps(_config, indent=2), encoding='utf-8')
    except Exception:
        pass

    return render_template_string(
        _SETUP_HTML,
        config=_config,
        message='Configuration saved successfully!',
        success=True,
    )


@_wizard_bp.route('/status')
def status():
    return jsonify({'setup_complete': _config.get('setup_complete', False), 'config': _config})


def init_setup_wizard(app):
    """Register the setup wizard blueprint with the Flask app."""
    app.register_blueprint(_wizard_bp)

    # Load persisted config if it exists
    try:
        from pathlib import Path
        import json
        cfg_path = Path(__file__).resolve().parent.parent / 'data' / 'setup_config.json'
        if cfg_path.exists():
            saved = json.loads(cfg_path.read_text(encoding='utf-8'))
            _config.update(saved)
    except Exception:
        pass

    print('[MC] Setup wizard registered at /setup')
