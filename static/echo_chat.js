// Minimal, robust chat UI JS (modeled after static chat.html)
let sessionId = localStorage.getItem('echo_session_id') || ('web_' + Date.now());
localStorage.setItem('echo_session_id', sessionId);
let messageCount = 0;
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
function addUserMessage(text) {
    const container = document.getElementById('chatMessages');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-message user';
    msgDiv.innerHTML = '<div class="chat-icon">👤</div><div class="chat-bubble">' + escapeHtml(text) + '</div>';
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
    messageCount++;
}
function addEchoMessage(text) {
    const container = document.getElementById('chatMessages');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-message echo';
    msgDiv.innerHTML = '<div class="chat-icon">🌙</div><div class="chat-bubble">' + escapeHtml(text) + '</div>';
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}
function setStatus(msg, ok) {
    const statusBox = document.getElementById('clientJsStatus');
    if (!statusBox) return;
    statusBox.style.display = 'block';
    statusBox.textContent = msg;
    statusBox.style.background = ok ? '#072' : '#220';
    statusBox.style.color = ok ? '#cfc' : '#f88';
}
function sendMessage() {
    const input = document.getElementById('chatInput');
    let message = input.value.trim();
    if (!message) return;
    // If command mode is enabled, ensure message begins with '!'
    const cmdToggle = document.getElementById('cmdToggle');
    if (cmdToggle && cmdToggle.checked) {
        if (!message.startsWith('!')) message = '!' + message;
    }
    addUserMessage(message);
    input.value = '';
    setStatus('Sending...', true);
    fetch('/api/echo/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message, session_id: sessionId })
    }).then(r => r.json()).then(data => {
        setStatus('Response received', true);
        addEchoMessage(data.response || 'No response');
        // Forward the Echo response to the selected bridged IRC channel when enabled
        try{
            const enabled = (localStorage.getItem('ircBridgeEnabled') === '1');
            const target = localStorage.getItem('ircBridgeChannel') || '';
            if(enabled && window.ircSessionId && target && window.ircBridges && window.ircBridges[target]){
                fetch('/irc/bridge_send',{
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-BRIDGE-TOKEN': (window.ircBridgeToken||'') },
                    body: JSON.stringify({ session: window.ircSessionId, channel: target, message: (data.response||''), bridge_token: (window.ircBridgeToken||'') })
                }).then(r=>r.json()).then(j=>{
                    if(!j || !j.success) setStatus('Bridge failed: '+(j && j.error || ''), false);
                    else setStatus('Bridged to '+target, true);
                }).catch(err=>{ setStatus('Bridge error: '+err, false); });
            }
        }catch(e){}
    }).catch(err => {
        setStatus('Error: ' + err, false);
        addEchoMessage('Sorry... something went wrong... 💜');
    });
}
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('sendBtn').onclick = sendMessage;
    document.getElementById('chatInput').addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });
    document.getElementById('clearBtn').onclick = function() {
        document.getElementById('chatMessages').innerHTML = '<div class="chat-message echo"><div class="chat-icon">🌙</div><div class="chat-bubble">Hello... I am Echo 🌙<br>I\'m here to help with DevOps tasks and learn from our conversations... 💜</div></div>';
        sessionId = 'web_' + Date.now();
        localStorage.setItem('echo_session_id', sessionId);
        messageCount = 0;
        setStatus('Chat cleared', true);
    };

    // Load persisted conversation history for this session
    try{
        fetch('/api/echo/history?session_id=' + encodeURIComponent(sessionId) + '&limit=200').then(r=>r.json()).then(j=>{
            if(j && j.history){
                const container = document.getElementById('chatMessages');
                container.innerHTML = '';
                j.history.reverse().forEach(h => {
                    if(h.user === 'web_user') addUserMessage(h.message);
                    else addEchoMessage(h.message || h.echo_response || '');
                });
            }
        }).catch(e=>{ console.debug('Failed to load history', e); });
    }catch(e){ console.debug('History fetch failed', e); }
    // Bridge controls UI: chooser + enable toggle
    try{
        const tools = document.createElement('div'); tools.id = 'ircBridgeControls'; tools.style.display='flex'; tools.style.gap='8px'; tools.style.alignItems='center'; tools.style.marginTop='8px';
        const lbl = document.createElement('label'); lbl.style.color='#ccc'; lbl.textContent = 'IRC Bridge:'; tools.appendChild(lbl);
        const toggle = document.createElement('input'); toggle.type='checkbox'; toggle.id='ircBridgeToggle'; toggle.checked = (localStorage.getItem('ircBridgeEnabled') === '1'); tools.appendChild(toggle);
        const sel = document.createElement('select'); sel.id = 'ircBridgeSelect'; sel.style.padding='6px'; sel.style.minWidth='180px'; tools.appendChild(sel);
        const hint = document.createElement('small'); hint.style.color='#999'; hint.textContent=' Forward Echo replies to selected bridged channel'; tools.appendChild(hint);
        const container = document.getElementById('chatMessages') || document.body;
        container.parentElement.insertBefore(tools, container.nextSibling);

        function updateBridgeOptions(){
            try{
                const map = window.ircBridges || {};
                const keys = Object.keys(map).filter(k=>map[k]);
                // preserve selection
                const prev = localStorage.getItem('ircBridgeChannel') || '';
                sel.innerHTML = '';
                const none = document.createElement('option'); none.value = ''; none.textContent = '-- none --'; sel.appendChild(none);
                keys.forEach(ch=>{ const o = document.createElement('option'); o.value = ch; o.textContent = ch; sel.appendChild(o); });
                if(prev){ try{ sel.value = prev; }catch(e){} }
            }catch(e){}
        }
        // wire toggle/select
        toggle.addEventListener('change', (e)=>{ localStorage.setItem('ircBridgeEnabled', e.target.checked ? '1' : '0'); setStatus('Bridge '+(e.target.checked ? 'enabled' : 'disabled'), true); });
        sel.addEventListener('change', (e)=>{ localStorage.setItem('ircBridgeChannel', e.target.value || ''); setStatus('Bridge target set', true); });
        // initial populate and periodic refresh (keeps in sync with IRC modal)
        updateBridgeOptions();
        setInterval(updateBridgeOptions, 1500);
    }catch(e){ console.debug('irc bridge controls init failed', e); }
    setStatus('Client JS loaded', true);
});
