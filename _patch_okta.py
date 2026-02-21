"""Patch main.py: add full Okta integration page."""

NAV_INSERT = '<a href="/okta" class="{{ \'active\' if request.path==\'/okta\' else \'\' }}">\U0001f512 Okta</a>\n\n</nav>'

OKTA_TEMPLATE = r'''
<style>
.okta-layout { display:grid; grid-template-columns:300px 1fr; gap:20px; margin-top:16px; }
@media(max-width:860px){ .okta-layout{grid-template-columns:1fr;} }
.okta-panel { background:#1e1e2e; border:1px solid #2a2a3a; border-radius:10px; padding:18px; }
.okta-panel h3 { margin:0 0 14px; font-size:1rem; color:#00b4d8; border-bottom:1px solid #2a2a3a; padding-bottom:8px; }
.ok-field { margin-bottom:10px; }
.ok-field label { display:block; font-size:.78rem; color:#888; margin-bottom:3px; }
.ok-input { width:100%; background:#111; border:1px solid #333; color:#eee; padding:6px 9px; border-radius:5px; font-size:.83rem; box-sizing:border-box; }
.ok-input:focus { outline:none; border-color:#00b4d8; }
.ok-btn { background:#00b4d8; color:#111; border:none; padding:7px 16px; border-radius:5px; font-size:.85rem; font-weight:600; cursor:pointer; margin-top:4px; }
.ok-btn:hover { background:#0096b4; color:#fff; }
.ok-btn-sm { padding:3px 10px; font-size:.76rem; }
.ok-btn-danger { background:#c0392b; color:#fff; }
.ok-btn-danger:hover { background:#e74c3c; }
.ok-status { font-size:.78rem; margin-top:6px; min-height:1.2em; }
.ok-connected { display:flex; align-items:center; gap:8px; font-size:.8rem; color:#4caf50; margin-bottom:10px; }
.ok-dot { width:8px; height:8px; background:#4caf50; border-radius:50%; flex-shrink:0; }
.apps-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(160px,1fr)); gap:12px; }
.app-card { background:#161620; border:1px solid #2a2a3a; border-radius:8px; padding:14px 12px; text-align:center; cursor:pointer; transition:border-color .15s, background .15s; text-decoration:none; display:block; }
.app-card:hover { border-color:#00b4d8; background:#1a1a2e; }
.app-icon { width:48px; height:48px; border-radius:8px; object-fit:contain; margin:0 auto 8px; display:block; background:#252535; padding:4px; }
.app-icon-placeholder { width:48px; height:48px; border-radius:8px; background:#252535; margin:0 auto 8px; display:flex; align-items:center; justify-content:center; font-size:1.4rem; }
.app-name { font-size:.78rem; color:#ddd; font-weight:600; line-height:1.3; word-break:break-word; }
.app-type { font-size:.67rem; color:#555; margin-top:3px; }
.apps-empty { color:#555; font-size:.88rem; padding:40px 0; text-align:center; }
.ok-search { width:100%; background:#111; border:1px solid #333; color:#eee; padding:7px 10px; border-radius:5px; font-size:.83rem; box-sizing:border-box; margin-bottom:14px; }
.ok-search:focus { outline:none; border-color:#00b4d8; }
.ok-mfa-panel { background:#1a1a2a; border:1px solid #00b4d8; border-radius:8px; padding:14px; margin-top:10px; display:none; }
.ok-mfa-panel h4 { margin:0 0 10px; color:#00b4d8; font-size:.9rem; }
</style>

<div style="display:flex; align-items:center; gap:14px; margin-bottom:4px;">
  <img src="https://www.vectorlogo.zone/logos/okta/okta-icon.svg" alt="Okta" style="width:36px;height:36px;border-radius:6px;" onerror="this.style.display='none'">
  <div>
    <h2 style="margin:0;">Okta App Launcher</h2>
    <p style="color:#888;font-size:.88rem;margin:2px 0 0;">Sign in with your Okta credentials to browse and launch your assigned apps.</p>
  </div>
</div>

<div class="okta-layout">

  <!-- Left: login panel -->
  <div>
    <div class="okta-panel">
      <h3>&#128274; Sign In</h3>

      <div id="ok-connected-banner" style="display:none;" class="ok-connected">
        <span class="ok-dot"></span>
        <div>
          <div id="ok-connected-who" style="font-weight:600;"></div>
          <div style="color:#888;font-size:.72rem;" id="ok-connected-org"></div>
        </div>
        <button class="ok-btn ok-btn-danger ok-btn-sm" onclick="oktaSignOut()" style="margin:0 0 0 auto;">Sign out</button>
      </div>

      <div id="ok-login-form">
        <div class="ok-field">
          <label>Okta Domain</label>
          <input id="ok-domain" class="ok-input" placeholder="yourorg.okta.com" value="tegna.okta.com">
        </div>
        <div class="ok-field">
          <label>Username (email)</label>
          <input id="ok-username" class="ok-input" placeholder="you@company.com" autocomplete="username">
        </div>
        <div class="ok-field">
          <label>Password</label>
          <input id="ok-password" class="ok-input" type="password" placeholder="Your password" autocomplete="current-password">
        </div>
        <button class="ok-btn" onclick="oktaSignIn()">&#128274; Sign In to Okta</button>
        <div class="ok-status" id="ok-sign-in-status"></div>
      </div>

      <!-- MFA panel (shown when MFA factor required) -->
      <div class="ok-mfa-panel" id="ok-mfa-panel">
        <h4>&#128241; Multi-Factor Authentication</h4>
        <p style="font-size:.78rem;color:#aaa;margin:0 0 10px;" id="ok-mfa-prompt">Enter your verification code.</p>
        <div class="ok-field">
          <label>Code</label>
          <input id="ok-mfa-code" class="ok-input" placeholder="6-digit code" maxlength="10" onkeydown="if(event.key==='Enter')oktaMfaVerify();">
        </div>
        <button class="ok-btn" onclick="oktaMfaVerify()">Verify</button>
        <div class="ok-status" id="ok-mfa-status"></div>
      </div>
    </div>

    <!-- App stats -->
    <div class="okta-panel" style="margin-top:14px;" id="ok-stats-panel" style="display:none;">
      <h3>&#128202; Stats</h3>
      <div id="ok-stats-body" style="font-size:.82rem;color:#aaa;"></div>
    </div>
  </div>

  <!-- Right: apps grid -->
  <div>
    <div class="okta-panel">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
        <h3 style="margin:0;padding:0;border:none;">&#128196; My Apps</h3>
        <button class="ok-btn ok-btn-sm" onclick="oktaLoadApps()" id="ok-load-apps-btn">&#8635; Refresh</button>
      </div>
      <input id="ok-app-search" class="ok-search" placeholder="Search apps&#8230;" oninput="oktaFilterApps()" style="display:none;">
      <div class="ok-status" id="ok-apps-status"></div>
      <div class="apps-grid" id="ok-apps-grid"></div>
      <div class="apps-empty" id="ok-apps-empty">Sign in to load your Okta apps.</div>
    </div>
  </div>

</div>

<script>
// ── Okta state ────────────────────────────────────────────────────────────────
var _oktaSession  = null;   // session id from Okta
var _oktaStateToken = null; // for MFA flows
var _oktaFactorId  = null;
var _oktaAllApps   = [];

(function(){
  var saved = JSON.parse(localStorage.getItem('okta_prefs')||'{}');
  if(saved.domain)   document.getElementById('ok-domain').value   = saved.domain;
  if(saved.username) document.getElementById('ok-username').value = saved.username;
})();

function oktaSavePref(){
  localStorage.setItem('okta_prefs', JSON.stringify({
    domain: document.getElementById('ok-domain').value.trim(),
    username: document.getElementById('ok-username').value.trim()
  }));
}

function oktaSignIn(){
  var domain   = document.getElementById('ok-domain').value.trim().replace(/^https?:\/\//,'').replace(/\/+$/,'');
  var username = document.getElementById('ok-username').value.trim();
  var password = document.getElementById('ok-password').value;
  var st       = document.getElementById('ok-sign-in-status');
  if(!domain||!username||!password){ st.textContent='\u26A0 Fill in all fields.'; return; }
  st.textContent='Signing in\u2026';
  oktaSavePref();
  fetch('/api/okta/signin',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({domain,username,password})})
  .then(function(r){ return r.json(); }).then(function(j){
    if(j.session_id){
      _oktaSession = j.session_id;
      st.textContent='';
      showConnected(j);
      oktaLoadApps();
    } else if(j.mfa_required){
      _oktaStateToken = j.state_token;
      _oktaFactorId   = j.factor_id;
      document.getElementById('ok-mfa-panel').style.display='';
      document.getElementById('ok-mfa-prompt').textContent = j.mfa_prompt || 'Enter your authentication code.';
      st.textContent='';
    } else {
      st.innerHTML='<span style="color:#f55;">\u274C '+(j.error||JSON.stringify(j))+'</span>';
    }
  }).catch(function(e){ st.innerHTML='<span style="color:#f55;">Error: '+e+'</span>'; });
}

function oktaMfaVerify(){
  var code  = document.getElementById('ok-mfa-code').value.trim();
  var st    = document.getElementById('ok-mfa-status');
  var domain = document.getElementById('ok-domain').value.trim().replace(/^https?:\/\//,'').replace(/\/+$/,'');
  if(!code){ st.textContent='\u26A0 Enter the code.'; return; }
  st.textContent='Verifying\u2026';
  fetch('/api/okta/mfa',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({domain,state_token:_oktaStateToken,factor_id:_oktaFactorId,passcode:code})})
  .then(function(r){ return r.json(); }).then(function(j){
    if(j.session_id){
      _oktaSession = j.session_id;
      document.getElementById('ok-mfa-panel').style.display='none';
      st.textContent='';
      showConnected(j);
      oktaLoadApps();
    } else {
      st.innerHTML='<span style="color:#f55;">\u274C '+(j.error||JSON.stringify(j))+'</span>';
    }
  }).catch(function(e){ st.innerHTML='<span style="color:#f55;">Error: '+e+'</span>'; });
}

function showConnected(j){
  var banner = document.getElementById('ok-connected-banner');
  banner.style.display='flex';
  document.getElementById('ok-login-form').style.display='none';
  document.getElementById('ok-connected-who').textContent = j.display_name||j.login||'Signed in';
  document.getElementById('ok-connected-org').textContent = document.getElementById('ok-domain').value.trim();
  document.getElementById('ok-app-search').style.display='';
}

function oktaSignOut(){
  _oktaSession = null;
  _oktaAllApps = [];
  document.getElementById('ok-connected-banner').style.display='none';
  document.getElementById('ok-login-form').style.display='';
  document.getElementById('ok-mfa-panel').style.display='none';
  document.getElementById('ok-apps-grid').innerHTML='';
  document.getElementById('ok-apps-empty').textContent='Sign in to load your Okta apps.';
  document.getElementById('ok-apps-empty').style.display='';
  document.getElementById('ok-app-search').style.display='none';
  document.getElementById('ok-sign-in-status').textContent='Signed out.';
  document.getElementById('ok-password').value='';
}

function oktaLoadApps(){
  var st = document.getElementById('ok-apps-status');
  if(!_oktaSession){ st.innerHTML='<span style="color:#f55;">\u26A0 Sign in first.</span>'; return; }
  var domain = document.getElementById('ok-domain').value.trim().replace(/^https?:\/\//,'').replace(/\/+$/,'');
  st.textContent='Loading apps\u2026';
  document.getElementById('ok-apps-empty').style.display='none';
  fetch('/api/okta/apps',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({domain,session_id:_oktaSession})})
  .then(function(r){ return r.json(); }).then(function(j){
    st.textContent='';
    if(j.apps){
      _oktaAllApps = j.apps;
      oktaRenderApps(_oktaAllApps);
      var statsEl = document.getElementById('ok-stats-body');
      statsEl.innerHTML='<b>'+j.apps.length+'</b> apps assigned';
      document.getElementById('ok-stats-panel').style.display='';
    } else {
      st.innerHTML='<span style="color:#f55;">\u274C '+(j.error||JSON.stringify(j))+'</span>';
    }
  }).catch(function(e){ st.innerHTML='<span style="color:#f55;">Error: '+e+'</span>'; });
}

function oktaRenderApps(apps){
  var grid  = document.getElementById('ok-apps-grid');
  var empty = document.getElementById('ok-apps-empty');
  grid.innerHTML='';
  if(!apps||apps.length===0){
    empty.textContent='No apps found.'; empty.style.display=''; return;
  }
  empty.style.display='none';
  apps.filter(function(a){ return !a.hidden; }).forEach(function(app){
    var card = document.createElement('a');
    card.className='app-card';
    card.href  = app.linkUrl || '#';
    card.target='_blank';
    card.rel   ='noopener noreferrer';
    var iconHtml = app.logoUrl
      ? '<img class="app-icon" src="'+app.logoUrl+'" alt="" onerror="this.style.display=\'none\';this.nextSibling.style.display=\'flex\';">'
        +'<div class="app-icon-placeholder" style="display:none;">\U0001f4e6</div>'
      : '<div class="app-icon-placeholder">\U0001f4e6</div>';
    card.innerHTML = iconHtml
      +'<div class="app-name">'+escHtmlOk(app.label||app.appName||'App')+'</div>'
      +'<div class="app-type">'+escHtmlOk(app.appName||'')+'</div>';
    grid.appendChild(card);
  });
}

function oktaFilterApps(){
  var q = document.getElementById('ok-app-search').value.toLowerCase();
  if(!q){ oktaRenderApps(_oktaAllApps); return; }
  oktaRenderApps(_oktaAllApps.filter(function(a){
    return (a.label||'').toLowerCase().includes(q) || (a.appName||'').toLowerCase().includes(q);
  }));
}

function escHtmlOk(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
</script>
'''

BACKEND_OKTA = '''

@app.route('/api/okta/signin', methods=['POST'])
def api_okta_signin():
    """Authenticate with Okta Primary Authentication API and create a session."""
    try:
        import urllib.request as _ur, urllib.parse as _up
        data = request.get_json() or {}
        domain   = data.get('domain', '').strip().lstrip('https://').rstrip('/')
        username = data.get('username', '').strip()
        password = data.get('password', '')
        if not domain or not username or not password:
            return jsonify({'error': 'domain, username and password required'}), 400

        # Step 1: Primary authentication
        authn_url = f'https://{domain}/api/v1/authn'
        authn_body = json.dumps({'username': username, 'password': password,
                                  'options': {'warnBeforePasswordExpired': False, 'multiOptionalFactorEnroll': False}}).encode()
        req = _ur.Request(authn_url, data=authn_body, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept', 'application/json')
        with _ur.urlopen(req, timeout=15) as resp:
            authn = json.loads(resp.read().decode())

        status = authn.get('status')

        if status == 'SUCCESS':
            session_token = authn['sessionToken']
        elif status in ('MFA_REQUIRED', 'MFA_ENROLL_ACTIVATE'):
            # Return MFA challenge info to the client
            state_token = authn.get('stateToken', '')
            factors = authn.get('_embedded', {}).get('factors', [])
            # Prefer TOTP (token:software:totp) or push
            factor = next((f for f in factors if f.get('factorType') == 'token:software:totp'), None)
            if not factor:
                factor = next((f for f in factors if f.get('factorType') == 'push'), None)
            if not factor and factors:
                factor = factors[0]
            if not factor:
                return jsonify({'error': 'MFA required but no factors available'}), 400
            prompt = f'Enter code for: {factor.get("provider","")}'
            return jsonify({'mfa_required': True, 'state_token': state_token,
                            'factor_id': factor.get('id', ''), 'mfa_prompt': prompt})
        elif status == 'LOCKED_OUT':
            return jsonify({'error': 'Account is locked out.'}), 403
        elif status == 'PASSWORD_EXPIRED':
            return jsonify({'error': 'Password has expired. Reset it in Okta first.'}), 403
        else:
            return jsonify({'error': f'Unexpected status: {status}'}), 400

        # Step 2: Exchange session token for a session (get session id for API calls)
        sess_url = f'https://{domain}/api/v1/sessions'
        sess_body = json.dumps({'sessionToken': session_token}).encode()
        req2 = _ur.Request(sess_url, data=sess_body, method='POST')
        req2.add_header('Content-Type', 'application/json')
        req2.add_header('Accept', 'application/json')
        with _ur.urlopen(req2, timeout=15) as resp2:
            session = json.loads(resp2.read().decode())

        return jsonify({
            'session_id': session.get('id'),
            'login': session.get('login', username),
            'display_name': (authn.get('_embedded', {}).get('user', {}).get('profile') or {}).get('displayName', ''),
        })
    except Exception as e:
        app.logger.exception('Okta signin failed')
        err_msg = str(e)
        try:
            if hasattr(e, 'read'):
                body_err = json.loads(e.read().decode())
                err_msg = body_err.get('errorSummary') or body_err.get('message') or err_msg
        except Exception:
            pass
        return jsonify({'error': err_msg}), 500


@app.route('/api/okta/mfa', methods=['POST'])
def api_okta_mfa():
    """Verify an MFA factor and return a session."""
    try:
        import urllib.request as _ur
        data = request.get_json() or {}
        domain      = data.get('domain', '').strip().lstrip('https://').rstrip('/')
        state_token = data.get('state_token', '')
        factor_id   = data.get('factor_id', '')
        passcode    = data.get('passcode', '').strip()
        if not all([domain, state_token, factor_id, passcode]):
            return jsonify({'error': 'domain, state_token, factor_id and passcode required'}), 400

        verify_url = f'https://{domain}/api/v1/authn/factors/{factor_id}/verify'
        body = json.dumps({'stateToken': state_token, 'passCode': passcode}).encode()
        req = _ur.Request(verify_url, data=body, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept', 'application/json')
        with _ur.urlopen(req, timeout=15) as resp:
            authn = json.loads(resp.read().decode())

        if authn.get('status') != 'SUCCESS':
            return jsonify({'error': f"MFA status: {authn.get('status')}. Check your code."}), 400

        session_token = authn['sessionToken']
        sess_url  = f'https://{domain}/api/v1/sessions'
        sess_body = json.dumps({'sessionToken': session_token}).encode()
        req2 = _ur.Request(sess_url, data=sess_body, method='POST')
        req2.add_header('Content-Type', 'application/json')
        req2.add_header('Accept', 'application/json')
        with _ur.urlopen(req2, timeout=15) as resp2:
            session = json.loads(resp2.read().decode())

        return jsonify({
            'session_id': session.get('id'),
            'login': session.get('login', ''),
        })
    except Exception as e:
        app.logger.exception('Okta MFA failed')
        err_msg = str(e)
        try:
            if hasattr(e, 'read'):
                body_err = json.loads(e.read().decode())
                err_msg = body_err.get('errorSummary') or err_msg
        except Exception:
            pass
        return jsonify({'error': err_msg}), 500


@app.route('/api/okta/apps', methods=['POST'])
def api_okta_apps():
    """Fetch the app links assigned to the current Okta user."""
    try:
        import urllib.request as _ur
        data = request.get_json() or {}
        domain     = data.get('domain', '').strip().lstrip('https://').rstrip('/')
        session_id = data.get('session_id', '').strip()
        if not domain or not session_id:
            return jsonify({'error': 'domain and session_id required'}), 400

        url = f'https://{domain}/api/v1/users/me/appLinks'
        req = _ur.Request(url)
        req.add_header('Accept', 'application/json')
        req.add_header('Cookie', f'sid={session_id}')
        with _ur.urlopen(req, timeout=20) as resp:
            apps = json.loads(resp.read().decode())

        return jsonify({'apps': apps, 'count': len(apps)})
    except Exception as e:
        app.logger.exception('Okta apps failed')
        err_msg = str(e)
        try:
            if hasattr(e, 'read'):
                body_err = json.loads(e.read().decode())
                err_msg = body_err.get('errorSummary') or err_msg
        except Exception:
            pass
        return jsonify({'error': err_msg}), 500
'''

# ─── Patch main.py ────────────────────────────────────────────────────────────
with open('main.py', encoding='utf-8') as f:
    text = f.read()

changes = 0

# 1. Nav link
OLD_NAV = '<a href="/teams" class="{{ \'active\' if request.path==\'/teams\' else \'\' }}">\U0001f4c5 Teams</a>\n\n</nav>'
NEW_NAV = ('<a href="/teams" class="{{ \'active\' if request.path==\'/teams\' else \'\' }}">\U0001f4c5 Teams</a>\n\n'
           '<a href="/okta" class="{{ \'active\' if request.path==\'/okta\' else \'\' }}">\U0001f512 Okta</a>\n\n</nav>')
if OLD_NAV in text:
    text = text.replace(OLD_NAV, NEW_NAV, 1); changes += 1; print('OK 1: nav link')
else:
    print('FAIL 1: nav anchor not found')

# 2. OKTA_TEMPLATE variable + route — insert after TEAMS_TEMPLATE closing triple-quote
# Find end of teams template and routes
teams_route_end = "@app.route('/api/modules/toggle'"
idx = text.find(teams_route_end)
if idx == -1:
    # Try alternate
    teams_route_end = "def api_teams_chat_send"
    idx2 = text.find(teams_route_end)
    # Find end of that function
    idx = text.find("\n\n\n@app.route", idx2) if idx2 != -1 else -1
    if idx == -1:
        idx = text.find("\n\n@app.route('/api/modules", idx2) if idx2 != -1 else -1

if idx != -1:
    INSERT_BLOCK = (
        "\nOKTA_TEMPLATE = '''" + OKTA_TEMPLATE + "'''\n\n"
        "@app.route('/okta')\n"
        "@requires_permission('dashboard')\n"
        "def okta_page():\n"
        "    return render_template_string(HTML_TEMPLATE.replace"
        "('{% block content %}{% endblock %}', OKTA_TEMPLATE), "
        "request=request, get_flashed_messages=get_flashed_messages)\n"
        + BACKEND_OKTA + "\n"
    )
    text = text[:idx] + INSERT_BLOCK + text[idx:]
    changes += 1; print('OK 2: OKTA_TEMPLATE + routes inserted')
else:
    print('FAIL 2: insertion point not found')

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(text)

print(f'\nPatches applied: {changes}/2')
