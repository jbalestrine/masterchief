with open('main.py', encoding='utf-8') as f:
    text = f.read()

OLD_INIT = """// Init date range defaults
(function(){
  const now = new Date();
  const y = now.getFullYear(), m = now.getMonth();
  const s = new Date(y, m, 1);
  const e = new Date(y, m+1, 0);
  document.getElementById('tm-range-start').value = s.toISOString().slice(0,10);
  document.getElementById('tm-range-end').value   = e.toISOString().slice(0,10);
  calRender();
  // Restore saved creds
  const saved = JSON.parse(localStorage.getItem('tm_creds')||'{}');
  if(saved.tenant)      document.getElementById('tm-tenant').value = saved.tenant;
  if(saved.client_id)   document.getElementById('tm-client-id').value = saved.client_id;
  if(saved.upn)         document.getElementById('tm-upn').value = saved.upn;
})();

function teamsConnect(){
  const tenant = document.getElementById('tm-tenant').value.trim();
  const clientId = document.getElementById('tm-client-id').value.trim();
  const clientSecret = document.getElementById('tm-client-secret').value.trim();
  const upn = document.getElementById('tm-upn').value.trim();
  const st = document.getElementById('tm-conn-status');
  if(!tenant||!clientId||!clientSecret){ st.textContent='\\u26A0 Fill in Tenant ID, Client ID and Secret.'; return; }
  st.textContent='Connecting\u2026';
  fetch('/api/teams/connect',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({tenant_id:tenant,client_id:clientId,client_secret:clientSecret,upn})})
  .then(r=>r.json()).then(j=>{
    if(j.token){
      _teamsToken = j.token;
      st.innerHTML='<span style="color:#4caf50;">\\u2705 Connected \u2014 '+j.scope+'</span>';
      document.getElementById('teams-connected-banner').style.display='flex';
      // Save non-secret creds
      localStorage.setItem('tm_creds', JSON.stringify({tenant,client_id:clientId,upn}));
    } else {
      st.innerHTML='<span style="color:#f55;">\\u274C '+(j.error||JSON.stringify(j))+'</span>';
    }
  }).catch(e=>{ st.innerHTML='<span style="color:#f55;">Error: '+e+'</span>'; });
}"""

NEW_INIT = """// Init date range defaults
(function(){
  const now = new Date();
  const y = now.getFullYear(), m = now.getMonth();
  const s = new Date(y, m, 1);
  const e = new Date(y, m+1, 0);
  document.getElementById('tm-range-start').value = s.toISOString().slice(0,10);
  document.getElementById('tm-range-end').value   = e.toISOString().slice(0,10);
  calRender();
  // Restore saved creds
  const saved = JSON.parse(localStorage.getItem('tm_creds')||'{}');
  if(saved.tenant)    document.getElementById('tm-tenant').value = saved.tenant;
  if(saved.username)  document.getElementById('tm-username').value = saved.username;
  if(saved.client_id) document.getElementById('tm-client-id').value = saved.client_id;
  if(saved.upn)       document.getElementById('tm-upn').value = saved.upn;
  if(saved.mode)      tmSetMode(saved.mode);
})();

function tmSetMode(mode){
  _tmMode = mode;
  document.getElementById('tm-mode-upw').style.display  = mode==='upw' ? '' : 'none';
  document.getElementById('tm-mode-app').style.display  = mode==='app' ? '' : 'none';
  document.getElementById('tm-tab-upw').style.background = mode==='upw' ? '#252535' : '#161620';
  document.getElementById('tm-tab-upw').style.color      = mode==='upw' ? '#7ec8e3' : '#666';
  document.getElementById('tm-tab-app').style.background = mode==='app' ? '#252535' : '#161620';
  document.getElementById('tm-tab-app').style.color      = mode==='app' ? '#7ec8e3' : '#666';
}

function teamsConnect(){
  const tenant = document.getElementById('tm-tenant').value.trim();
  const st     = document.getElementById('tm-conn-status');
  if(!tenant){ st.textContent='\\u26A0 Enter a Tenant ID (or "common").'; return; }
  st.textContent='Connecting\u2026';
  let payload;
  if(_tmMode==='upw'){
    const username = document.getElementById('tm-username').value.trim();
    const password = document.getElementById('tm-password').value;
    if(!username||!password){ st.textContent='\\u26A0 Enter your username and password.'; return; }
    payload = {grant_type:'password', tenant_id:tenant, username, password};
    _teamsUpn = username;
  } else {
    const clientId     = document.getElementById('tm-client-id').value.trim();
    const clientSecret = document.getElementById('tm-client-secret').value.trim();
    const upn          = document.getElementById('tm-upn').value.trim();
    if(!clientId||!clientSecret){ st.textContent='\\u26A0 Fill in Client ID and Secret.'; return; }
    payload = {grant_type:'client_credentials', tenant_id:tenant, client_id:clientId, client_secret:clientSecret, upn};
    _teamsUpn = upn||null;
  }
  fetch('/api/teams/connect',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})
  .then(r=>r.json()).then(j=>{
    if(j.token){
      _teamsToken = j.token;
      const who = _teamsUpn ? ' ('+_teamsUpn+')' : '';
      st.innerHTML='<span style="color:#4caf50;">\\u2705 Connected'+who+'</span>';
      document.getElementById('teams-connected-banner').style.display='flex';
      document.getElementById('teams-connected-who').textContent = who;
      const save = {mode:_tmMode, tenant};
      if(_tmMode==='upw') save.username = document.getElementById('tm-username').value.trim();
      else { save.client_id=document.getElementById('tm-client-id').value.trim(); save.upn=document.getElementById('tm-upn').value.trim(); }
      localStorage.setItem('tm_creds', JSON.stringify(save));
    } else {
      st.innerHTML='<span style="color:#f55;">\\u274C '+(j.error||JSON.stringify(j))+'</span>';
    }
  }).catch(e=>{ st.innerHTML='<span style="color:#f55;">Error: '+e+'</span>'; });
}"""

if OLD_INIT in text:
    text = text.replace(OLD_INIT, NEW_INIT, 1)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print('SUCCESS: replaced init+teamsConnect')
else:
    # Debug: find where they differ
    for i, (a, b) in enumerate(zip(OLD_INIT, text[text.find('// Init date range defaults'):])):
        if a != b:
            print(f'MISMATCH at char {i}: expected {repr(a)} got {repr(b)}')
            print('Context old:', repr(OLD_INIT[max(0,i-20):i+20]))
            print('Context new:', repr(text[text.find('// Init date range defaults')+max(0,i-20):text.find('// Init date range defaults')+i+20]))
            break
    else:
        print('No mismatch found in compared range, but substring not found')
        print('OLD_INIT length:', len(OLD_INIT))
        idx = text.find('// Init date range defaults')
        print('File snippet length:', len(text[idx:idx+len(OLD_INIT)]))
