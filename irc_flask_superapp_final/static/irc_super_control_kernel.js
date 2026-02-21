// Lazy-init variant: create a small launcher button and only build the heavy UI on demand.
(function(){
  if(window.IRCSuper) return;

  const CFG={api: (typeof window!=='undefined' && window.location?window.location.origin:'http://127.0.0.1:8080'), token:"DEV_TOKEN",poll:3000,channels:["#masterchief"]};
  const Modules={},Bots={},Commands={},Wizards={};
  let pollId = null;

  function buildKernel(){
    if(window.IRCSuper && window.IRCSuper._inited) return;

    const root=document.createElement("div");
    root.id = 'ircSuperRoot';
    root.style=`position:fixed;bottom:0;right:0;width:780px;height:520px;
      background:#0b0b0b;color:#ddd;font-family:monospace;border:1px solid #333;
      z-index:999999;display:flex;flex-direction:column`;
    root.innerHTML=`
      <div style="background:#111;padding:6px;font-weight:bold">IRC Super Control Kernel <span id="ircCloseBtn" style="float:right;cursor:pointer;padding:4px 8px;background:#222;border-radius:4px;margin-right:6px;">Close</span></div>
      <div id="tabs" style="display:flex;border-bottom:1px solid #333"></div>
      <div id="out" style="flex:1;overflow:auto;padding:6px;height:420px"></div>
      <div style="display:flex;gap:8px;padding:6px;background:#070">
        <input id="in" placeholder="/help" style="flex:1;border:0;background:#000;color:#0f0;padding:6px">
        <label style="color:#ddd;font-size:12px;margin-left:6px">Auto-register <input id="autoReg" type="checkbox"></label>
        <button id="startSession" style="padding:6px">Start Session</button>
        <button id="openSessions" style="padding:6px">Sessions</button>
      </div>`;

    // do not append until opened
    document.body.appendChild(root);

    const out=root.querySelector("#out"),input=root.querySelector("#in"),tabs=root.querySelector("#tabs");
    let activeChannel=CFG.channels[0];
    function log(m){out.innerHTML+=`<div>${m}</div>`;out.scrollTop=1e9;}

    const noticesDiv = document.createElement('div'); noticesDiv.style.padding='6px';

    CFG.channels.forEach(c=>{
      const t=document.createElement("div");
      t.textContent=c;t.style="padding:6px;cursor:pointer";
      t.onclick=()=>{activeChannel=c;out.innerHTML="";log(`Switched to ${c}`);} 
      tabs.appendChild(t);
    });
    const tNot = document.createElement('div'); tNot.textContent='Notices'; tNot.style="padding:6px;cursor:pointer"; tNot.onclick=()=>{out.innerHTML='';out.appendChild(noticesDiv);}; tabs.appendChild(tNot);

    const api=(p,b)=>fetch(CFG.api + p,{method:(b?'POST':'GET'),headers:{"Content-Type":"application/json","X-BRIDGE-TOKEN":CFG.token},body:b?JSON.stringify(b):null}).then(r=>r.json().catch(()=>({})));
    function route(line){const [cmd,...args]=line.split(" ");if(Commands[cmd]) Commands[cmd](args); else log(`Unknown command: ${cmd}`);} 
    input.onkeydown=e=>{if(e.key==="Enter"){log("> "+input.value);route(input.value);input.value="";}};
    function registerModule(name,mod){Modules[name]=mod;mod.init?.();log(`[MODULE] ${name} loaded`);} 
    function createBot(name,spec){Bots[name]={name,onMessage:spec.onMessage||(()=>{}),commands:spec.commands||{}};log(`[BOT] ${name} created`);} 
    function wizard(name,steps){Wizards[name]=steps;} 
    function runWizard(name){let i=0;const steps=Wizards[name];const next=()=>{if(!steps[i])return log(`[WIZARD] ${name} complete`);steps[i++](next,log);};next();}
    Commands["/help"]=()=>{log("Commands:");Object.keys(Commands).forEach(c=>log(" "+c));};
    Commands["/wizard"]=a=>runWizard(a[0]);
    Commands["/load"]=async a=>{const src=await fetch(a[0]).then(r=>r.text());eval(src);log("Remote script loaded");};

    registerModule("config",{init:()=>{Commands["/conf"]=async a=>{if(a[0]==="enable") await api("/features/inspircd/module/enable",{module:a[1]}),log("Module enabled"); if(a[0]==="disable") await api("/features/inspircd/module/disable",{module:a[1]}),log("Module disabled"); if(a[0]==="apply") await api("/features/inspircd/apply"),log("Config applied"); if(a[0]==="list"){const r=await api("/features/inspircd/config");log(JSON.stringify(r.modules||{},null,2));}}});
    registerModule("ai",{init:()=>{Commands["/ai"]=async a=>{const r=await api("",{session:"super-kernel",module:"qwen_inspircd",args:["--channel",activeChannel,"--prompt",a.join(" ")]});log("[AI] "+(r.output||"ok"));};}});
    registerModule("bot-factory",{init:()=>{Commands["/bot"]=a=>{if(a[0]==="create"){createBot(a[1],{onMessage:(m)=>{if(m.includes("hello"))log(`[${a[1]}] hello human`);}});}};}});
    wizard("botgen",[(n,l)=>{l("BotGen Wizard Starting");n();},(n,l)=>{createBot("BotSmith",{commands:{}});l("BotSmith created");n();}]);

    // periodic notices
    pollId = setInterval(async()=>{const r=await api("/irc/notices"); if(r?.lines){noticesDiv.innerHTML=''; r.lines.slice(-100).forEach(l=>{const d=document.createElement('div');d.textContent=l;noticesDiv.appendChild(d);});}}, CFG.poll);

    // session controls
    const sessionsPanel = document.createElement('div'); sessionsPanel.style.padding='6px';
    function refreshSessions(){api('/irc/sessions').then(r=>{sessionsPanel.innerHTML=''; if(r?.sessions){Object.keys(r.sessions).forEach(n=>{const e=document.createElement('div');e.textContent=n+': '+JSON.stringify(r.sessions[n]); const stop=document.createElement('button');stop.textContent='Stop';stop.style.marginLeft='8px'; stop.onclick=()=>fetch(CFG.api+'/irc/session/stop',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nick:n})}).then(()=>refreshSessions()); e.appendChild(stop);sessionsPanel.appendChild(e);});}});} 
    root.querySelector('#openSessions').onclick=()=>{out.innerHTML='';out.appendChild(sessionsPanel);refreshSessions();};

    // Start session button
    root.querySelector('#startSession').onclick = async ()=>{const nick = prompt('Session nick', 'session_bot'); if(!nick) return; const resp = await fetch(CFG.api + '/irc/register_session',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nick:nick,channels:CFG.channels})}); const j = await resp.json(); if(j.ok) { log('[SESSION] started '+nick); refreshSessions(); } else log('[SESSION] failed: '+(j.error||JSON.stringify(j))); };

    // Close control
    root.querySelector('#ircCloseBtn').addEventListener('click', ()=>{ root.style.display='none'; });

    log("IRC Super Control Kernel ready");

    window.IRCSuper={Modules,Bots,Commands,Wizards,registerModule,createBot,wizard,log,_inited:true,_root:root,_stop:()=>{ try{ if(pollId) clearInterval(pollId); if(root && root.parentElement) root.parentElement.removeChild(root); delete window.IRCSuper; }catch(e){} }};
  }

  // Launcher
  function createLauncher(){ if(document.getElementById('ircLauncherBtn')) return; const btn = document.createElement('button'); btn.id='ircLauncherBtn'; btn.textContent='IRC'; btn.title='Open IRC Super Control Kernel'; btn.style='position:fixed;bottom:16px;right:16px;z-index:999998;border-radius:6px;padding:8px 10px;background:#009688;color:#fff;border:none;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,0.3);'; btn.onclick=()=>{ if(window.IRCSuper && window.IRCSuper._inited){ try{ const r = window.IRCSuper._root; if(r){ r.style.display = (r.style.display === 'none' ? 'flex' : 'flex'); r.style.zIndex = 999999; } }catch(e){} } else { buildKernel(); } }; document.body.appendChild(btn); }

  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', createLauncher); else createLauncher();

})();
