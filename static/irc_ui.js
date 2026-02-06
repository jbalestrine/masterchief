(function(){
// Modal-based IRC UI with per-channel panes, user lists, nick persistence, and bridge support
function createUI(){
  if(document.getElementById('miniIrcModal')) return;
  const modal = document.createElement('div'); modal.id='miniIrcModal';
  modal.style.position='fixed'; modal.style.left='0'; modal.style.top='0'; modal.style.width='100%'; modal.style.height='100%'; modal.style.background='rgba(0,0,0,0.6)'; modal.style.zIndex=99999; modal.style.display='flex'; modal.style.alignItems='center'; modal.style.justifyContent='center';
  const panel = document.createElement('div'); panel.style.width='900px'; panel.style.maxWidth='calc(100% - 40px)'; panel.style.height='640px'; panel.style.background='#0f0f12'; panel.style.border='1px solid #222'; panel.style.borderRadius='10px'; panel.style.boxShadow='0 12px 40px rgba(0,0,0,0.7)'; panel.style.display='flex'; panel.style.flexDirection='column'; modal.appendChild(panel);

  panel.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 14px;border-bottom:1px solid #141414;">
      <div style="font-weight:700;color:#e6e6fa">MasterChief IRC</div>
      <div style="display:flex;gap:8px;align-items:center">
        <button id="miniIrcScripts" class="btn">Scripts</button>
        <button id="miniIrcClose" class="btn">Close</button>
      </div>
    </div>
    <div style="display:flex;gap:12px;flex:1;padding:12px;">
      <div style="width:260px;display:flex;flex-direction:column;gap:8px;">
        <div style="display:flex;gap:8px;align-items:center;">
          <input id="miniIrcHost" placeholder="host" value="127.0.0.1" style="flex:1;padding:8px;background:#0b0b0b;color:#ddd;border:1px solid #222;border-radius:6px" />
          <input id="miniIrcPort" placeholder="port" value="6667" style="width:72px;padding:8px;background:#0b0b0b;color:#ddd;border:1px solid #222;border-radius:6px" />
        </div>
        <div style="display:flex;gap:8px;align-items:center;">
          <input id="miniIrcNick" placeholder="nick" style="flex:1;padding:8px;background:#0b0b0b;color:#ddd;border:1px solid #222;border-radius:6px" />
          <label style="color:#aaa;font-size:12px"><input type="checkbox" id="miniIrcSaveNick" style="margin-right:6px">Save</label>
        </div>
        <div style="display:flex;gap:8px;">
          <button id="miniIrcConnect" class="btn">Connect</button>
          <div id="miniIrcStatus" style="color:#aaa;font-size:13px;margin-left:6px;align-self:center">Disconnected</div>
        </div>

        <div style="margin-top:8px;font-size:13px;color:#bbb">Channels</div>
        <div id="miniIrcChannelsList" style="flex:1;overflow:auto;background:#080808;padding:8px;border-radius:6px;border:1px solid #222;font-family:monospace;color:#cfe;">
        </div>
        <div style="display:flex;gap:6px;align-items:center;">
          <input id="miniIrcJoin" placeholder="#channel" style="flex:1;padding:8px;background:#0b0b0b;color:#ddd;border:1px solid #222;border-radius:6px" />
          <button id="miniIrcJoinBtn" class="btn">Join</button>
        </div>
        <div style="margin-top:8px;font-size:12px;color:#aaa">Bridge</div>
        <div style="display:flex;gap:6px;align-items:center;">
          <button id="miniIrcEnableBridge" class="btn">Enable Bridge</button>
          <button id="miniIrcBridgeSend" class="btn">Bridge Send</button>
        </div>
      </div>

      <div style="flex:1;display:flex;flex-direction:column;gap:8px;">
        <div id="miniIrcTabs" style="display:flex;gap:8px;align-items:center"></div>
        <div style="flex:1;display:flex;gap:8px;overflow:hidden;">
          <div id="miniIrcMessages" style="flex:1;background:#070707;border-radius:6px;padding:10px;overflow:auto;font-family:monospace;color:#cfc;font-size:13px"></div>
          <div id="miniIrcUsers" style="width:180px;background:#0b0b0b;border-radius:6px;padding:8px;overflow:auto;border:1px solid #222;color:#9bd;font-family:monospace;font-size:13px">Users</div>
        </div>
        <div style="display:flex;gap:8px;align-items:center;">
          <input id="miniIrcInput" placeholder="Message" style="flex:1;padding:10px;background:#0b0b0b;color:#ddd;border:1px solid #222;border-radius:6px" />
          <button id="miniIrcSend" class="btn">Send</button>
          <div id="miniIrcQueued" style="color:#FFA500;display:none;font-size:13px">Queued until registration</div>
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  // state
  const state = { session:null, last:0, pollId:null, channels: {}, active:null, bridgeToken:null, bridgeEnabled: false, deaf: false, channelControls: {} };

  // elements
  const elHost = modal.querySelector('#miniIrcHost');
  const elPort = modal.querySelector('#miniIrcPort');
  const elNick = modal.querySelector('#miniIrcNick');
  const elSaveNick = modal.querySelector('#miniIrcSaveNick');
  const elConnect = modal.querySelector('#miniIrcConnect');
  const elStatus = modal.querySelector('#miniIrcStatus');
  const elChannelsList = modal.querySelector('#miniIrcChannelsList');
  const elJoinInput = modal.querySelector('#miniIrcJoin');
  const elJoinBtn = modal.querySelector('#miniIrcJoinBtn');
  const elEnableBridge = modal.querySelector('#miniIrcEnableBridge');
  const elBridgeSend = modal.querySelector('#miniIrcBridgeSend');
  const elMessages = modal.querySelector('#miniIrcMessages');
  const elUsers = modal.querySelector('#miniIrcUsers');
  const elInput = modal.querySelector('#miniIrcInput');
  const elSend = modal.querySelector('#miniIrcSend');
  const elQueued = modal.querySelector('#miniIrcQueued');
  const elClose = modal.querySelector('#miniIrcClose');
  const elScriptsBtn = modal.querySelector('#miniIrcScripts');

  // preload saved nick
  try{ const saved = localStorage.getItem('miniIrcNick'); if(saved) elNick.value = saved; }catch(e){}

  // --- Scripts manager modal ---
  function openScriptsManager(selectName){
    // if already present, show
    let sm = document.getElementById('miniIrcScriptsModal');
    if(sm){ sm.style.display='block'; return; }
    sm = document.createElement('div'); sm.id='miniIrcScriptsModal';
    sm.style.position='absolute'; sm.style.left='50%'; sm.style.top='50%'; sm.style.transform='translate(-50%,-50%)'; sm.style.width='720px'; sm.style.height='520px'; sm.style.background='#0b0b0b'; sm.style.border='1px solid #222'; sm.style.borderRadius='8px'; sm.style.padding='12px'; sm.style.zIndex=100000;
    sm.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <div style="font-weight:700;color:#e6e6fa">Scripts Manager</div>
        <div style="display:flex;gap:8px"><button id="miniIrcScriptsNew" class="btn">New</button><button id="miniIrcScriptsClose" class="btn">Close</button></div>
      </div>
      <div style="display:flex;gap:8px;height:calc(100% - 48px);">
        <div style="width:240px;overflow:auto;border-right:1px solid #222;padding-right:8px;" id="miniIrcScriptsList">Loading...</div>
        <div style="flex:1;display:flex;flex-direction:column;gap:6px;">
          <input id="miniIrcScriptsName" placeholder="script name" style="padding:6px;background:#070707;color:#ddd;border:1px solid #222;border-radius:4px;" />
          <textarea id="miniIrcScriptsEditor" style="flex:1;background:#070707;color:#cfc;border:1px solid #222;border-radius:4px;padding:8px;font-family:monospace;resize:none"></textarea>
          <div style="display:flex;gap:8px;justify-content:flex-end;"><button id="miniIrcScriptsSave" class="btn">Save</button></div>
        </div>
      </div>`;
    modal.appendChild(sm);

    const listEl = sm.querySelector('#miniIrcScriptsList');
    const nameEl = sm.querySelector('#miniIrcScriptsName');
    const editor = sm.querySelector('#miniIrcScriptsEditor');
    const saveBtn = sm.querySelector('#miniIrcScriptsSave');
    const newBtn = sm.querySelector('#miniIrcScriptsNew');
    const closeBtn = sm.querySelector('#miniIrcScriptsClose');

    async function loadList(){ listEl.textContent='Loading...'; try{ const r = await fetch('/irc/mirc/list'); const j = await r.json().catch(()=>null); if(r.ok && j && j.success){ listEl.innerHTML=''; (j.scripts||[]).forEach(s=>{ const rdiv = document.createElement('div'); rdiv.textContent = s; rdiv.style.padding='6px'; rdiv.style.cursor='pointer'; rdiv.onclick = ()=>{ openScript(s); }; listEl.appendChild(rdiv); }); } else { listEl.textContent='(no scripts or fetch failed)'; } }catch(e){ listEl.textContent='Error loading list'; }}

    async function openScript(name){ try{ const r = await fetch('/irc/mirc/get?name='+encodeURIComponent(name)); const j = await r.json().catch(()=>null); if(r.ok && j && j.success){ nameEl.value = name; editor.value = j.content||''; } else { alert('Failed to fetch: '+(j?j.error:r.status)); } }catch(e){ alert('Fetch error '+e); }}

    async function saveScript(){ const name = (nameEl.value||'').trim(); if(!name){ alert('Name required'); return; } let fname = name; if(!fname.endsWith('.mrc')) fname = fname + '.mrc'; const content = editor.value || '';
      try{ const headers={'Content-Type':'application/json'}; if(state.bridgeToken) headers['X-BRIDGE-TOKEN']=state.bridgeToken; const r = await fetch('/irc/mirc/upload',{method:'POST',headers:headers,body:JSON.stringify({name: fname, content: content})}); const j = await r.json().catch(()=>null); if(r.ok && j && j.success){ alert('Saved'); loadList(); } else { alert('Save failed: '+(j?j.error:r.status)); } }catch(e){ alert('Save error '+e); } }

    newBtn.addEventListener('click', ()=>{ nameEl.value='new-script.mrc'; editor.value=''; nameEl.focus(); });
    saveBtn.addEventListener('click', saveScript);
    closeBtn.addEventListener('click', ()=>{ sm.style.display='none'; });
    loadList().then(()=>{ if(selectName) try{ openScript(selectName); }catch(e){ console.error('openScript',e); } });
  }


  function renderChannels(){ elChannelsList.innerHTML = ''; Object.keys(state.channels).forEach(ch=>{
    const row = document.createElement('div'); row.style.display='flex'; row.style.justifyContent='space-between'; row.style.alignItems='center'; row.style.padding='6px'; row.style.borderBottom='1px solid #101010';
    const left = document.createElement('div'); left.style.cursor='pointer'; left.textContent = ch; left.onclick = ()=>{ setActiveChannel(ch); };
    const right = document.createElement('div'); right.style.display='flex'; right.style.gap='6px';
    const bridgeCb = document.createElement('input'); bridgeCb.type='checkbox'; bridgeCb.checked = !!state.channels[ch].bridge; bridgeCb.onclick = (e)=>{ state.channels[ch].bridge = e.target.checked; };
    const btn = document.createElement('button'); btn.textContent = '×'; btn.title='Close'; btn.onclick = ()=>{ delete state.channels[ch]; if(state.active===ch) state.active = Object.keys(state.channels)[0] || null; renderChannels(); renderActive(); };
    right.appendChild(bridgeCb); right.appendChild(btn);
    row.appendChild(left); row.appendChild(right); elChannelsList.appendChild(row);
  }); }

  function appendToChannel(ch, text){ state.channels[ch] = state.channels[ch] || { messages: [], users: [], bridge: false }; // normalize text
    if(typeof text === 'string') text = text.replace(/\r?\n$/,'');
    state.channels[ch].messages.push(text);
    if(state.active===ch) renderActive(); }

  function renderActive(){ elMessages.innerHTML=''; elUsers.innerHTML=''; if(!state.active){ elMessages.textContent='No channel selected'; return; } const ch = state.active;
    // render controls (stop button for runs etc)
    const ctrl = state.channelControls[ch];
    if(ctrl){ const cdiv = document.createElement('div'); cdiv.style.marginBottom='8px'; if(ctrl.run_id){ const stopBtn = document.createElement('button'); stopBtn.textContent='Stop'; stopBtn.className='btn'; stopBtn.onclick = async function(){ try{ const headers={'Content-Type':'application/json'}; if(state.bridgeToken) headers['X-BRIDGE-TOKEN']=state.bridgeToken; const resp = await fetch('/irc/module/stop',{method:'POST',headers:headers,body:JSON.stringify({session: state.session, run_id: ctrl.run_id})}); const j = await resp.json().catch(()=>null); if(resp.ok && j && j.success){ appendToChannel(ch,'[STOP SENT]'); } else { appendToChannel(ch,'[STOP FAIL] '+(j?JSON.stringify(j):resp.status)); } }catch(e){ appendToChannel(ch,'[STOP ERROR] '+e); } }; cdiv.appendChild(stopBtn); }
      elMessages.appendChild(cdiv);
    }
    // render messages with simple formatting: show PRIVMSG as '<nick> text' when possible
    (state.channels[ch].messages||[]).forEach(m=>{
      const d=document.createElement('div');
      let out = m;
      try{
        const pm = String(m||'').match(/^:([^!\s]+)!.*\sPRIVMSG\s+(#[^\s:]+|[^\s:]+)\s*:(.*)$/i);
        if(pm){ const nick = pm[1]; const txt = pm[3] || ''; out = `<${nick}> ${txt.replace(/\r?\n$/,'')}`; }
      }catch(e){}
      d.textContent = out; elMessages.appendChild(d);
    });
    (state.channels[ch].users||[]).forEach(u=>{ const d=document.createElement('div'); d.textContent = u; elUsers.appendChild(d); }); elMessages.scrollTop = elMessages.scrollHeight; }
  function setActiveChannel(ch){ state.active = ch; renderChannels(); renderActive(); }

  function setQueued(on){ elQueued.style.display = on ? 'block' : 'none'; elSend.disabled = on; }

  async function connect(){
    try{
      elStatus.textContent = 'Connecting...';
      const r = await fetch('/irc/connect',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({host:elHost.value,port:parseInt(elPort.value||6667),nick:elNick.value})});
      const j = await r.json();
      if(j && j.success){ state.session = j.session; state.bridgeToken = j.bridge_token || null; elStatus.textContent = 'Connected'; startPoll(); if(elSaveNick.checked){ try{ localStorage.setItem('miniIrcNick', elNick.value); }catch(e){} } renderChannels(); } else { elStatus.textContent = 'Connect failed'; }
    }catch(e){ elStatus.textContent='Error'; }
  }

  // auto-join default channel after connect to ensure we see others' messages
  const DEFAULT_CHANNEL = '#masterchief';
  const AUTO_JOIN_DELAY_MS = 1200;

  async function startPoll(){ if(state.pollId) clearInterval(state.pollId); state.pollId = setInterval(async ()=>{
    if(!state.session) return;
    try{
      const rr = await fetch('/irc/recv?session='+encodeURIComponent(state.session)+'&last='+state.last);
      const jj = await rr.json();
      if(jj && jj.success){ const msgs = jj.messages||[]; if(msgs.length){ msgs.forEach(m=>{ try{
            // NAMES / 353 numeric parsing
            const mstr = String(m||'');
            const re353 = /\b353\b\s+\S+\s+\S+\s+(#[^\s]+)\s*:(.*)/i;
            const mm353 = mstr.match(re353);
            if(mm353){ const ch = mm353[1]; const raw = (mm353[2]||'').trim(); const users = raw.split(/\s+/).map(u=>u.replace(/^[@+%~&]/,'')); state.channels[ch] = state.channels[ch] || {messages:[],users:[],bridge:false}; state.channels[ch].users = users; }
            // JOIN/PART handlers
            const jm = mstr.match(/^:([^!\s]+)!.*\sJOIN\s+:?(#[^\s]+)/i);
            if(jm){ const who=jm[1]; const ch=jm[2]; state.channels[ch] = state.channels[ch] || {messages:[],users:[],bridge:false}; if(!state.channels[ch].users.includes(who)) state.channels[ch].users.push(who); }
            const pmPart = mstr.match(/^:([^!\s]+)!.*\sPART\s+(#[^\s]+)/i);
            if(pmPart){ const who=pmPart[1]; const ch=pmPart[2]; if(state.channels[ch]) state.channels[ch].users = (state.channels[ch].users||[]).filter(x=>x!==who); }
            // PRIVMSG mapping
            const pm = mstr.match(/\bPRIVMSG\b\s+(#[^\s:]+|[^\s:]+)\s*:(.*)/i);
            if(pm){ const ch = pm[1]; const txt = pm[2]||''; // respect deaf mode: when deaf, suppress channel PRIVMSG display
              if(state.deaf){ appendToChannel('_global', '[DEAF] suppressed PRIVMSG to '+ch+' from server'); }
              else { appendToChannel(ch, mstr); }
            }
            // registration numerics clear queued UI
            if(/\s001\s/.test(mstr) || /\s376\s/.test(mstr) || /\s422\s/.test(mstr)){ setQueued(false); }
            // always append to global log under _global
            appendToChannel('_global', mstr);
        }catch(e){ console.error('parse message',e); } }); state.last = jj.total; }
        if(!jj.alive){ elStatus.textContent = 'Reconnecting'; } else { elStatus.textContent = 'Connected'; }
      }
    }catch(e){ console.error('poll error', e); }
  },800); }

    // open SSE stream for realtime updates (per-session)
    try{
      if(state.sse){ try{ state.sse.close(); }catch(e){} state.sse = null; }
      const streamUrl = '/irc/stream?session='+encodeURIComponent(state.session||'')+'&last='+state.last;
      const src = new EventSource(streamUrl);
      state.sse = src;
      src.onmessage = function(ev){ try{
          const data = JSON.parse(ev.data||'{}');
          const line = data.line || data.text || '';
          if(line){ const mstr = String(line||''); const pm = mstr.match(/\bPRIVMSG\b\s+(#[^\s:]+|[^\s:]+)\s*:(.*)/i);
              if(pm){ appendToChannel(pm[1], mstr); }
              else { appendToChannel('_global', mstr); }
              if(/\s001\s/.test(mstr) || /\s376\s/.test(mstr) || /\s422\s/.test(mstr)){ setQueued(false); }
          }
          if(typeof data.index !== 'undefined'){ state.last = Math.max(state.last, data.index); }
      }catch(e){ console.error('SSE parse', e); } };
      src.onerror = function(e){ console.warn('SSE error', e); try{ src.close(); }catch(_){} state.sse = null; };
    }catch(e){ console.error('Failed to open SSE', e); }

  // after connecting, try to auto-join the default channel so UI receives channel traffic
  (function watchConnectAutoJoin(){
    const origConnect = connect;
    connect = async function(){
      await origConnect();
      // if connected, join default channel after brief delay to allow registration
      try{
        if(state.session){ setTimeout(()=>{ try{ joinChannel(DEFAULT_CHANNEL); setActiveChannel(DEFAULT_CHANNEL); }catch(e){ console.error('auto-join error',e); } }, AUTO_JOIN_DELAY_MS); }
      }catch(e){ console.error('post-connect auto-join', e); }
    };
  })();

  async function joinChannel(ch){ if(!state.session) return; try{ await fetch('/irc/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session:state.session,message:'JOIN '+ch})}); state.channels[ch] = state.channels[ch] || {messages:[],users:[],bridge:false}; renderChannels(); setActiveChannel(ch); }catch(e){ console.error('join failed',e); } }

  async function partChannel(ch){ if(!state.session) return; try{ const target = ch || state.active; if(!target) return; await fetch('/irc/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session:state.session,message:'PART '+target})}); appendToChannel('_global','[INFO] Sent PART '+target); if(state.channels[target]){ delete state.channels[target]; if(state.active===target) state.active = Object.keys(state.channels)[0] || null; renderChannels(); renderActive(); } }catch(e){ console.error('part failed',e); } }

  async function listModules(){ try{ const r = await fetch('/irc/modules'); const j = await r.json().catch(()=>null); if(j && j.success){ appendToChannel('_global','[MODULES]'); (j.modules||[]).forEach(m=> appendToChannel('_global', JSON.stringify(m))); } else { appendToChannel('_global','[MODULES] fetch failed'); } }catch(e){ appendToChannel('_global','[MODULES] error '+e); } }

  async function sendMessage(){ if(!state.session) return; const raw = (elInput.value||'').trim(); if(!raw) return; // support slash-commands
    if(raw.startsWith('/')){
      const parts = raw.slice(1).trim().split(/\s+/); const cmd = (parts[0]||'').toLowerCase(); const args = parts.slice(1);
      switch(cmd){
        case 'raw':
          // send raw IRC line
          if(!args.length){ appendToChannel('_global','Usage: /raw RAW_LINE'); }
          else { try{ await fetch('/irc/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session:state.session,message:args.join(' ')})}); appendToChannel('_global','[RAW SENT] '+args.join(' ')); }catch(e){ appendToChannel('_global','[RAW ERROR] '+e); } }
          elInput.value=''; return;
        case 'notice':
          if(!args[0]){ appendToChannel('_global','Usage: /notice target message'); }
          else { const target = args[0]; const msg = args.slice(1).join(' '); try{ await fetch('/irc/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session:state.session,message:'NOTICE '+target+' :'+msg})}); appendToChannel('_global','[NOTICE] -> '+target+' : '+msg); }catch(e){ appendToChannel('_global','[NOTICE ERROR] '+e); } }
          elInput.value=''; return;
        case 'ctcp':
          if(args.length<2){ appendToChannel('_global','Usage: /ctcp target TYPE [text]'); }
          else { const target=args[0]; const type=args[1]; const text=args.slice(2).join(' '); const payload='\x01'+type+(text?(' '+text):'')+'\x01'; try{ await fetch('/irc/msg',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session:state.session,channel:target,message:payload})}); appendToChannel('_global','[CTCP] '+type+' -> '+target); }catch(e){ appendToChannel('_global','[CTCP ERROR] '+e); } }
          elInput.value=''; return;
        case 'timer':
          // /timer 5 /raw PING :abc
          if(args.length<2){ appendToChannel('_global','Usage: /timer seconds command...'); }
          else { const secs = parseFloat(args[0]); const cmdstr = args.slice(1).join(' '); appendToChannel('_global','[TIMER] scheduling in '+secs+'s: '+cmdstr); setTimeout(async ()=>{ elInput.value = cmdstr; await sendMessage(); }, Math.max(0,secs*1000)); }
          elInput.value=''; return;
        case 'repeat':
          // /repeat 5 /raw PONG :x
          if(args.length<3){ appendToChannel('_global','Usage: /repeat count interval_seconds command...'); }
          else { const count = parseInt(args[0])||1; const interval = parseFloat(args[1])||1; const cmdstr = args.slice(2).join(' '); appendToChannel('_global','[REPEAT] '+count+' times every '+interval+'s: '+cmdstr); let i=0; const id = setInterval(async ()=>{ if(i>=count){ clearInterval(id); return; } elInput.value=cmdstr; await sendMessage(); i++; }, Math.max(100,interval*1000)); }
          elInput.value=''; return;
        case 'deaf':
          if(args[0] && args[0].toLowerCase()==='on'){ state.deaf = true; appendToChannel('_global','[INFO] Deaf mode ON'); }
          else { state.deaf = false; appendToChannel('_global','[INFO] Deaf mode OFF'); }
          elStatus.textContent = state.deaf ? 'Connected (DEAF)' : 'Connected';
          elInput.value=''; return;
        case 'join':
          if(!args[0]){ appendToChannel('_global','Usage: /join #channel'); } else { await joinChannel(args[0]); }
          elInput.value=''; return;
        case 'part':
          await partChannel(args[0]||null); elInput.value=''; return;
        case 'nick':
          if(!args[0]){ appendToChannel('_global','Usage: /nick newnick'); } else { try{ await fetch('/irc/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session:state.session,message:'NICK '+args[0]})}); elNick.value = args[0]; appendToChannel('_global','[INFO] Sent NICK '+args[0]); if(elSaveNick.checked){ try{ localStorage.setItem('miniIrcNick', args[0]); }catch(e){} } }catch(e){ appendToChannel('_global','[ERROR] nick change failed '+e); } elInput.value=''; return; }
        case 'modules':
          await listModules(); elInput.value=''; return;
          case 'mrc':
            // /mrc list | run name | upload name | edit name
            if(!args[0]){ try{ openScriptsManager(); appendToChannel('_global','[MRC] opened script manager'); }catch(e){ appendToChannel('_global','[MRC OPEN ERROR] '+e); } }
            else if(args[0].toLowerCase()==='list'){
              try{ const r = await fetch('/irc/mirc/list'); const j = await r.json().catch(()=>null); if(j && j.success){ appendToChannel('_global','[MRC LIST]'); (j.scripts||[]).forEach(s=> appendToChannel('_global', s)); } else appendToChannel('_global','[MRC LIST FAIL]'); }catch(e){ appendToChannel('_global','[MRC LIST ERROR] '+e); }
            } else if(args[0].toLowerCase()==='run'){
              if(!args[1]) appendToChannel('_global','Usage: /mrc run <name>'); else {
                const name = args[1]; try{ const payload = {session: state.session, script: name}; const headers={'Content-Type':'application/json'}; if(state.bridgeToken) headers['X-BRIDGE-TOKEN']=state.bridgeToken; const r = await fetch('/irc/mirc/run',{method:'POST',headers:headers,body:JSON.stringify(payload)}); const j=await r.json().catch(()=>null); if(r.ok && j && j.success){ appendToChannel('_global','[MRC RUN STARTED] run_id='+j.run_id); } else { appendToChannel('_global','[MRC RUN FAIL] '+(j?JSON.stringify(j):r.status)); } }catch(e){ appendToChannel('_global','[MRC RUN ERROR] '+e); } }
            } else if(args[0].toLowerCase()==='edit'){
              const sel = args[1] || null; try{ openScriptsManager(sel); appendToChannel('_global','[MRC EDIT] opening script manager'); }catch(e){ appendToChannel('_global','[MRC EDIT ERROR] '+e); }
            } else if(args[0].toLowerCase()==='upload'){
              if(!args[1]){ appendToChannel('_global','Usage: /mrc upload <name>'); }
              else {
                const name = args[1]; const content = prompt('Paste .mrc script content for '+name+'.mrc'); if(!content) { appendToChannel('_global','[MRC UPLOAD CANCEL]'); } else {
                  try{ const payload = {name: name, content: content}; const headers={'Content-Type':'application/json'}; if(state.bridgeToken) headers['X-BRIDGE-TOKEN']=state.bridgeToken; const r = await fetch('/irc/mirc/upload',{method:'POST',headers:headers,body:JSON.stringify(payload)}); const j = await r.json().catch(()=>null); if(r.ok && j && j.success) appendToChannel('_global','[MRC UPLOAD OK]'); else appendToChannel('_global','[MRC UPLOAD FAIL] '+(j?JSON.stringify(j):r.status)); }catch(e){ appendToChannel('_global','[MRC UPLOAD ERROR] '+e); }
                }
              }
            } else { appendToChannel('_global','Unknown /mrc subcommand'); }
            elInput.value=''; return;
        case 'module':
          if(!args[0]){ appendToChannel('_global','Usage: /module name [args]'); }
          else {
            try{
              // if first arg is 'stream' use streaming API: /module stream name [args...]
              if(args[0].toLowerCase()==='stream'){
                if(!args[1]){ appendToChannel('_global','Usage: /module stream name [args]'); }
                else {
                  const mname = args[1]; const margs = args.slice(2);
                  const payload = { session: state.session, module: mname, args: margs };
                  const headers = {'Content-Type':'application/json'};
                  if(state.bridgeToken) headers['X-BRIDGE-TOKEN'] = state.bridgeToken;
                  const rstart = await fetch('/irc/module/stream',{method:'POST',headers:headers,body:JSON.stringify(payload)});
                  const jstart = await rstart.json().catch(()=>null);
                  if(!rstart.ok || !jstart || !jstart.success){ appendToChannel('_global','[MODULE START FAIL] '+(jstart?JSON.stringify(jstart):rstart.status)); }
                  else {
                    const run_id = jstart.run_id;
                    const run_ch = '_run_'+run_id;
                    state.channels[run_ch] = state.channels[run_ch] || {messages:[],users:[],bridge:false};
                    // add run controls (Stop)
                    state.channelControls[run_ch] = { run_id: run_id };
                    appendToChannel('_global','[MODULE STARTED] run_id='+run_id+' module='+mname);
                    renderChannels(); setActiveChannel(run_ch);
                    // subscribe to SSE
                    const src = new EventSource('/irc/module/stream/'+encodeURIComponent(run_id));
                    src.onmessage = function(ev){ try{ const data = JSON.parse(ev.data||'{}'); if(data.type==='line'){ appendToChannel(run_ch, data.text); } else if(data.type==='done' || data.type==='finished'){ appendToChannel(run_ch, '[MODULE FINISHED] return='+String(data.returncode)); src.close(); } else if(data.type==='error'){ appendToChannel(run_ch, '[MODULE ERROR] '+String(data.error)); src.close(); } else { appendToChannel(run_ch, JSON.stringify(data)); } }catch(e){ appendToChannel(run_ch, '[STREAM PARSE ERROR] '+e); } };
                    src.onerror = function(e){ appendToChannel(run_ch, '[STREAM ERROR] connection closed or failed'); src.close(); };
                  }
                }
              } else {
                const payload = { session: state.session, module: args[0], args: args.slice(1) };
                const headers = {'Content-Type':'application/json'};
                if(state.bridgeToken) headers['X-BRIDGE-TOKEN'] = state.bridgeToken;
                const rr = await fetch('/irc/module',{method:'POST',headers:headers,body:JSON.stringify(payload)});
                const jj = await rr.json().catch(()=>null);
                if(rr.ok && jj && jj.success){ appendToChannel('_global','[MODULE OUT] return='+jj.returncode); appendToChannel('_global','stdout:\n'+(jj.stdout||'')); if(jj.stderr) appendToChannel('_global','stderr:\n'+jj.stderr); }
                else { appendToChannel('_global','[MODULE FAIL] '+(jj?JSON.stringify(jj):rr.status)); }
              }
            }catch(e){ appendToChannel('_global','[MODULE ERROR] '+e); }
          }
          elInput.value=''; return;
        case 'help':
          appendToChannel('_global','Available commands: /join /part /nick /deaf on|off /modules /module /help'); elInput.value=''; return;
        case 'me':
          // send action as PRIVMSG with CTCP ACTION wrapper
          if(!state.active){ appendToChannel('_global','Select a channel for /me'); elInput.value=''; return; }
          try{ const action = args.join(' '); const msg = '\u0001ACTION '+action+'\u0001'; await fetch('/irc/msg',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session:state.session,channel:state.active,message:msg})}); appendToChannel(state.active,'[OUT] * '+elNick.value+' '+action); }catch(e){ appendToChannel('_global','[ERROR] /me failed '+e); } elInput.value=''; return;
        default:
          appendToChannel('_global','Unknown command: /'+cmd+' (try /help)'); elInput.value=''; return;
      }
    }

    const msg = raw;
    const ch = state.active;
    if(!ch){ alert('Select or join a channel'); return; }
    try{
      setQueued(false);
      const resp = await fetch('/irc/msg',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session:state.session,channel:ch,message:msg})});
      if(resp.status===409){ setQueued(true); appendToChannel(ch, '[QUEUED] '+msg); }
      else if(!resp.ok){ const j=await resp.json().catch(()=>null); appendToChannel(ch,'[SEND FAIL] '+(j?JSON.stringify(j):resp.status)); }
      else { appendToChannel(ch,'[OUT] '+msg); }
    }catch(e){ appendToChannel(ch,'[SEND ERROR] '+e); setQueued(true); }
    elInput.value=''; }

  async function bridgeSend(){ if(!state.session) return; const msg = (elInput.value||'').trim(); if(!msg) return; const ch = state.active; if(!ch){ alert('Select channel to bridge'); return; }
    try{
      const headers = {'Content-Type':'application/json'};
      if(state.bridgeToken) headers['X-BRIDGE-TOKEN'] = state.bridgeToken;
      // include bridge token in body under expected key `bridge_token` as well as header
      const body = { session: state.session, channel: ch, message: msg };
      if(state.bridgeToken) body.bridge_token = state.bridgeToken;
      const resp = await fetch('/irc/bridge_send',{method:'POST',headers: headers, body: JSON.stringify(body)});
      const j = await resp.json().catch(()=>null);
      if(resp.ok && j && j.success) appendToChannel(ch,'[BRIDGE OUT] '+msg);
      else appendToChannel(ch,'[BRIDGE FAIL] '+(j?JSON.stringify(j):resp.status));
    }catch(e){ appendToChannel(ch,'[BRIDGE ERROR] '+e); }
    elInput.value=''; }

  elConnect.addEventListener('click', connect);
  elJoinBtn.addEventListener('click', ()=>{ const ch=(elJoinInput.value||'').trim(); if(!ch) return; joinChannel(ch); });
  elChannelsList.addEventListener('click', (ev)=>{ const t = ev.target; if(t && t.tagName==='DIV' && t.textContent){ const ch = t.textContent.trim(); setActiveChannel(ch); } });
  elSend.addEventListener('click', sendMessage);
  elInput.addEventListener('keydown', (e)=>{ if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); sendMessage(); } });
  elBridgeSend.addEventListener('click', bridgeSend);
  elEnableBridge.addEventListener('click', ()=>{ state.bridgeEnabled = !state.bridgeEnabled; elEnableBridge.textContent = state.bridgeEnabled ? 'Bridge: ON' : 'Enable Bridge'; });
  elScriptsBtn.addEventListener('click', ()=>{ try{ openScriptsManager(); }catch(e){ console.error('open scripts',e); } });
  elClose.addEventListener('click', ()=>{ modal.style.display='none'; });

  // expose API
  window.miniIrc = { addChannel: (c)=>{ state.channels[c]=state.channels[c]||{messages:[],users:[],bridge:false}; renderChannels(); }, setQueued: setQueued };
  renderChannels();
}

// auto-init on DOM ready
if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', createUI); else createUI();
})();
