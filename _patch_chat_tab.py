"""Patch main.py to add Teams Chat tab."""

CHAT_CSS = """
.chat-item { padding:8px 10px; border-radius:6px; cursor:pointer; border:1px solid #2a2a3a; background:#161620; }
.chat-item:hover { background:#1e1e30; }
.chat-item.selected { border-color:#7ec8e3; background:#1a1a2e; }
.chat-item-name { font-size:.82rem; color:#ddd; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.chat-item-preview { font-size:.72rem; color:#555; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; margin-top:2px; }
.msg-bubble { max-width:75%; padding:7px 12px; border-radius:10px; font-size:.82rem; line-height:1.45; }
.msg-row { display:flex; }
.msg-row.me { justify-content:flex-end; }
.msg-row.them { justify-content:flex-start; }
.msg-row.me .msg-bubble { background:#1b3a6b; color:#a8d4ff; border-bottom-right-radius:2px; }
.msg-row.them .msg-bubble { background:#1e1e2e; color:#ddd; border:1px solid #2a2a3a; border-bottom-left-radius:2px; }
.msg-sender { font-size:.68rem; color:#666; margin-bottom:2px; }
.msg-time { font-size:.65rem; color:#444; margin-top:3px; text-align:right; }"""

CHAT_HTML_TABS = (
    '\n<!-- \u2500\u2500 Page tabs \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 -->\n'
    '<div style="display:flex;gap:0;margin-bottom:18px;border-radius:8px;overflow:hidden;border:1px solid #2a2a3a;width:fit-content;">\n'
    '  <button id="tc-main-cal" onclick="tcMainTab(\'cal\')" style="padding:8px 22px;font-size:.88rem;font-weight:600;border:none;cursor:pointer;background:#252535;color:#7ec8e3;">\U0001f4c5 Calendar</button>\n'
    '  <button id="tc-main-chat" onclick="tcMainTab(\'chat\')" style="padding:8px 22px;font-size:.88rem;font-weight:600;border:none;cursor:pointer;background:#161620;color:#666;">\U0001f4ac Chat</button>\n'
    '</div>\n\n<!-- Calendar pane -->\n<div id="tc-pane-cal">'
)

CHAT_PANE = (
    '</div><!-- /tc-pane-cal -->\n\n'
    '<!-- Chat pane -->\n'
    '<div id="tc-pane-chat" style="display:none;">\n'
    '  <div class="teams-layout" style="grid-template-columns:280px 1fr;">\n\n'
    '    <!-- Chat list -->\n'
    '    <div>\n'
    '      <div class="teams-panel" style="height:100%;">\n'
    '        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">\n'
    '          <h3 style="margin:0;padding:0;border:none;">\U0001f4ac Recent Chats</h3>\n'
    '          <button class="tm-btn tm-btn-sm" onclick="chatLoad()">&#8635; Refresh</button>\n'
    '        </div>\n'
    '        <div class="tm-status" id="chat-list-status"></div>\n'
    '        <div id="chat-list" style="display:flex;flex-direction:column;gap:4px;max-height:520px;overflow-y:auto;margin-top:6px;"></div>\n'
    '      </div>\n'
    '    </div>\n\n'
    '    <!-- Message view -->\n'
    '    <div>\n'
    '      <div class="teams-panel" style="display:flex;flex-direction:column;gap:10px;">\n'
    '        <div id="chat-header" style="display:flex;align-items:center;justify-content:space-between;">\n'
    '          <h3 style="margin:0;padding:0;border:none;" id="chat-title">Select a chat \u2190</h3>\n'
    '          <button class="tm-btn tm-btn-sm" onclick="chatRefreshMsgs()" id="chat-refresh-btn" style="display:none;">&#8635; Refresh</button>\n'
    '        </div>\n'
    '        <div id="chat-msgs" style="flex:1;min-height:320px;max-height:420px;overflow-y:auto;display:flex;flex-direction:column;gap:6px;padding:4px 0;"></div>\n'
    '        <div id="chat-compose" style="display:none;margin-top:4px;">\n'
    '          <div style="display:flex;gap:8px;">\n'
    '            <input id="chat-input" class="tm-input" placeholder="Type a message\u2026" style="flex:1;" onkeydown="if(event.key===\'Enter\'&amp;&amp;!event.shiftKey){event.preventDefault();chatSend();}">\n'
    '            <button class="tm-btn" onclick="chatSend()">Send &#10148;</button>\n'
    '          </div>\n'
    '          <div class="tm-status" id="chat-send-status"></div>\n'
    '        </div>\n'
    '      </div>\n'
    '    </div>\n\n'
    '  </div>\n'
    '</div><!-- /tc-pane-chat -->'
)

CHAT_JS = r"""
// ── Chat state ───────────────────────────────────────────────────────────────
let _chatList = [];
let _chatSelectedId = null;
let _tcMainMode = 'cal';

function tcMainTab(tab){
  _tcMainMode = tab;
  document.getElementById('tc-pane-cal').style.display  = tab==='cal'  ? '' : 'none';
  document.getElementById('tc-pane-chat').style.display = tab==='chat' ? '' : 'none';
  document.getElementById('tc-main-cal').style.background  = tab==='cal'  ? '#252535' : '#161620';
  document.getElementById('tc-main-cal').style.color       = tab==='cal'  ? '#7ec8e3' : '#666';
  document.getElementById('tc-main-chat').style.background = tab==='chat' ? '#252535' : '#161620';
  document.getElementById('tc-main-chat').style.color      = tab==='chat' ? '#7ec8e3' : '#666';
  if(tab==='chat' && _chatList.length===0 && _teamsToken) chatLoad();
}

function chatLoad(){
  var st = document.getElementById('chat-list-status');
  if(!_teamsToken){ st.innerHTML='<span style="color:#f55;">\u26A0 Connect first (use the connection panel on the left).</span>'; return; }
  st.textContent='Loading chats\u2026';
  fetch('/api/teams/chats',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({token:_teamsToken})})
  .then(function(r){ return r.json(); }).then(function(j){
    if(j.chats){
      _chatList = j.chats;
      var el = document.getElementById('chat-list');
      el.innerHTML='';
      if(_chatList.length===0){ st.textContent='No chats found.'; return; }
      st.textContent='';
      _chatList.forEach(function(c){
        var name = c.topic || (c.members||[]).map(function(m){ return m.displayName||''; }).filter(Boolean).join(', ') || c.id;
        var preview = (c.lastMessagePreview&&c.lastMessagePreview.body&&c.lastMessagePreview.body.content)||'';
        var div = document.createElement('div');
        div.className='chat-item';
        div.dataset.id = c.id;
        div.innerHTML='<div class="chat-item-name">'+escHtml(name)+'</div>'
          +'<div class="chat-item-preview">'+escHtml(preview.replace(/<[^>]+>/g,'').slice(0,60))+'</div>';
        (function(id,n){ div.onclick=function(){ chatSelect(id,n); }; })(c.id,name);
        el.appendChild(div);
      });
    } else {
      st.innerHTML='<span style="color:#f55;">\u274C '+(j.error||JSON.stringify(j))+'</span>';
    }
  }).catch(function(e){ document.getElementById('chat-list-status').innerHTML='<span style="color:#f55;">Error: '+e+'</span>'; });
}

function chatSelect(id, name){
  _chatSelectedId = id;
  document.querySelectorAll('.chat-item').forEach(function(el){
    el.classList.toggle('selected', el.dataset.id===id);
  });
  document.getElementById('chat-title').textContent = name;
  document.getElementById('chat-refresh-btn').style.display='';
  document.getElementById('chat-compose').style.display='';
  chatRefreshMsgs();
}

function chatRefreshMsgs(){
  if(!_chatSelectedId) return;
  var el = document.getElementById('chat-msgs');
  el.innerHTML='<div style="color:#555;font-size:.8rem;padding:10px;">Loading messages\u2026</div>';
  fetch('/api/teams/chat/messages',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({token:_teamsToken, chat_id:_chatSelectedId, me_upn:_teamsUpn})})
  .then(function(r){ return r.json(); }).then(function(j){
    el.innerHTML='';
    if(!j.messages){ el.innerHTML='<span style="color:#f55;">\u274C '+(j.error||'Error')+'</span>'; return; }
    var msgs = j.messages.slice().reverse();
    if(msgs.length===0){ el.innerHTML='<div style="color:#555;font-size:.8rem;padding:10px;">No messages yet.</div>'; return; }
    msgs.forEach(function(m){
      var upn = (m.from&&m.from.user&&m.from.user.userPrincipalName)||'';
      var isMe = _teamsUpn && upn.toLowerCase()===_teamsUpn.toLowerCase();
      var sender = (m.from&&m.from.user&&m.from.user.displayName)||(m.from&&m.from.application&&m.from.application.displayName)||'';
      var body = ((m.body&&m.body.content)||'').replace(/<[^>]+>/g,' ').replace(/&nbsp;/g,' ').trim();
      var t = m.createdDateTime ? new Date(m.createdDateTime).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'}) : '';
      var row = document.createElement('div');
      row.className='msg-row '+(isMe?'me':'them');
      var inner = document.createElement('div');
      inner.innerHTML=((!isMe&&sender)?'<div class="msg-sender">'+escHtml(sender)+'</div>':'')
        +'<div class="msg-bubble">'+(body?escHtml(body):'<em style="color:#555;">(attachment)</em>')
        +'<div class="msg-time">'+t+'</div></div>';
      row.appendChild(inner);
      el.appendChild(row);
    });
    el.scrollTop = el.scrollHeight;
  }).catch(function(e){ el.innerHTML='<span style="color:#f55;">Error: '+e+'</span>'; });
}

function chatSend(){
  var input = document.getElementById('chat-input');
  var st    = document.getElementById('chat-send-status');
  var msg   = input.value.trim();
  if(!msg||!_chatSelectedId) return;
  st.textContent='Sending\u2026';
  fetch('/api/teams/chat/send',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({token:_teamsToken, chat_id:_chatSelectedId, message:msg})})
  .then(function(r){ return r.json(); }).then(function(j){
    if(j.ok){ input.value=''; st.textContent=''; setTimeout(chatRefreshMsgs,600); }
    else { st.innerHTML='<span style="color:#f55;">\u274C '+(j.error||JSON.stringify(j))+'</span>'; }
  }).catch(function(e){ st.innerHTML='<span style="color:#f55;">Error: '+e+'</span>'; });
}

function escHtml(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
"""

BACKEND_ROUTES = """

@app.route('/api/teams/chats', methods=['POST'])
def api_teams_chats():
    \"\"\"List the current user's recent chats via Microsoft Graph.\"\"\"
    try:
        import urllib.request as _ur, urllib.parse as _up
        data = request.get_json() or {}
        token = data.get('token', '').strip()
        if not token:
            return jsonify({'error': 'token required'}), 400
        url = ('https://graph.microsoft.com/v1.0/me/chats'
               '?$top=50&$expand=members&$select=id,topic,chatType,lastMessagePreview')
        req = _ur.Request(url)
        req.add_header('Authorization', 'Bearer ' + token)
        with _ur.urlopen(req, timeout=20) as resp:
            result = json.loads(resp.read().decode())
        return jsonify({'chats': result.get('value', [])})
    except Exception as e:
        app.logger.exception('Teams chats failed')
        err_msg = str(e)
        try:
            if hasattr(e, 'read'):
                body_err = json.loads(e.read().decode())
                err_msg = (body_err.get('error') or {}).get('message') or err_msg
        except Exception:
            pass
        return jsonify({'error': err_msg}), 500


@app.route('/api/teams/chat/messages', methods=['POST'])
def api_teams_chat_messages():
    \"\"\"Fetch recent messages from a specific Teams chat.\"\"\"
    try:
        import urllib.request as _ur, urllib.parse as _up
        data = request.get_json() or {}
        token   = data.get('token', '').strip()
        chat_id = data.get('chat_id', '').strip()
        if not token or not chat_id:
            return jsonify({'error': 'token and chat_id required'}), 400
        url = ('https://graph.microsoft.com/v1.0/me/chats/'
               + _up.quote(chat_id, safe='')
               + '/messages?$top=50&$select=id,body,from,createdDateTime,messageType')
        req = _ur.Request(url)
        req.add_header('Authorization', 'Bearer ' + token)
        with _ur.urlopen(req, timeout=20) as resp:
            result = json.loads(resp.read().decode())
        msgs = [m for m in result.get('value', []) if m.get('messageType') == 'message']
        return jsonify({'messages': msgs})
    except Exception as e:
        app.logger.exception('Teams chat messages failed')
        err_msg = str(e)
        try:
            if hasattr(e, 'read'):
                body_err = json.loads(e.read().decode())
                err_msg = (body_err.get('error') or {}).get('message') or err_msg
        except Exception:
            pass
        return jsonify({'error': err_msg}), 500


@app.route('/api/teams/chat/send', methods=['POST'])
def api_teams_chat_send():
    \"\"\"Send a text message to a Teams chat.\"\"\"
    try:
        import urllib.request as _ur, urllib.parse as _up
        data = request.get_json() or {}
        token   = data.get('token', '').strip()
        chat_id = data.get('chat_id', '').strip()
        message = data.get('message', '').strip()
        if not token or not chat_id or not message:
            return jsonify({'error': 'token, chat_id and message required'}), 400
        url = ('https://graph.microsoft.com/v1.0/me/chats/'
               + _up.quote(chat_id, safe='') + '/messages')
        body = json.dumps({'body': {'content': message, 'contentType': 'text'}}).encode()
        req = _ur.Request(url, data=body, method='POST')
        req.add_header('Authorization', 'Bearer ' + token)
        req.add_header('Content-Type', 'application/json')
        with _ur.urlopen(req, timeout=20) as resp:
            result = json.loads(resp.read().decode())
        return jsonify({'ok': True, 'id': result.get('id')})
    except Exception as e:
        app.logger.exception('Teams chat send failed')
        err_msg = str(e)
        try:
            if hasattr(e, 'read'):
                body_err = json.loads(e.read().decode())
                err_msg = (body_err.get('error') or {}).get('message') or err_msg
        except Exception:
            pass
        return jsonify({'error': err_msg}), 500
"""

# ─── Apply ─────────────────────────────────────────────────────────────────────
import re

with open('main.py', encoding='utf-8') as f:
    text = f.read()

changes = 0

# 1. CSS
OLD_CSS = '.teams-dot { width:8px; height:8px; background:#4caf50; border-radius:50%; }\n</style>'
NEW_CSS = '.teams-dot { width:8px; height:8px; background:#4caf50; border-radius:50%; }' + CHAT_CSS + '\n</style>'
if OLD_CSS in text:
    text = text.replace(OLD_CSS, NEW_CSS, 1); changes += 1; print('OK 1: CSS')
else:
    print('FAIL 1: CSS anchor missing')

# 2. Heading + tab bar
m = re.search(r'(<h2>[^\n]*Microsoft Teams[^\n]*</h2>\n<p[^>]*>[^<]*</p>\n\n)(<div class="teams-layout">)', text)
if m:
    repl = ('<h2>\U0001f4c5 Microsoft Teams</h2>\n'
            '<p style="color:#888;font-size:.88rem;">Connect to Microsoft Graph to load your calendar, view events, and chat.</p>\n'
            + CHAT_HTML_TABS + '\n<div class="teams-layout">')
    text = text[:m.start()] + repl + text[m.end():]
    changes += 1; print('OK 2: heading + tab bar')
else:
    print('FAIL 2: heading not found')

# 3. Chat pane before <script>
script_marker = '\n<script>\n// \u2500\u2500 Teams Calendar state'
idx = text.find(script_marker)
if idx != -1:
    close = '</div>\n</div>\n\n'
    close_pos = text.rfind(close, idx - 200, idx + 1)
    if close_pos != -1:
        insert_at = close_pos + len(close)
        text = text[:insert_at] + CHAT_PANE + '\n\n' + text[insert_at:]
        changes += 1; print('OK 3: chat pane')
    else:
        print('FAIL 3: closing </div></div> not found before <script>')
else:
    print('FAIL 3: script marker not found')

# 4. Chat JS before </script>"""
teams_start = text.find('TEAMS_TEMPLATE = """')
end_marker = '\n</script>\n"""'
pos = text.find(end_marker, teams_start)
if pos != -1:
    text = text[:pos] + CHAT_JS + '\n</script>\n"""' + text[pos + len(end_marker):]
    changes += 1; print('OK 4: chat JS')
else:
    print('FAIL 4: </script> end not found')

# 5. Scope update (may already be updated)
OLD_SCOPE = ("'scope': 'https://graph.microsoft.com/Calendars.Read "
             "https://graph.microsoft.com/User.Read offline_access openid',")
NEW_SCOPE = ("'scope': 'https://graph.microsoft.com/Calendars.Read "
             "https://graph.microsoft.com/Chat.Read "
             "https://graph.microsoft.com/Chat.ReadWrite "
             "https://graph.microsoft.com/User.Read offline_access openid',")
if OLD_SCOPE in text:
    text = text.replace(OLD_SCOPE, NEW_SCOPE, 1); print('OK 5: scope updated')
else:
    print('INFO 5: scope already has Chat or not found (skipping)')
changes += 1

# 6. Backend routes
cal_end = ("        return jsonify({'events': events, 'count': len(events)})\n"
           "    except Exception as e:\n"
           "        app.logger.exception('Teams calendar failed')\n"
           "        return jsonify({'error': str(e)}), 500")
idx6 = text.find(cal_end)
if idx6 != -1:
    pos6 = idx6 + len(cal_end)
    text = text[:pos6] + BACKEND_ROUTES + text[pos6:]
    changes += 1; print('OK 6: backend routes')
else:
    # Try without the except block
    alt = "return jsonify({'events': events, 'count': len(events)})"
    idx_alt = text.find(alt)
    print(f'FAIL 6: full marker not found; simple marker at char {idx_alt}')

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(text)
print(f'\nDone — {changes}/6 patches applied')
