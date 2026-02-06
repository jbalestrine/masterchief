(function(){
  if(window.IRCSuper) return;

  const CFG={api:"http://127.0.0.1:8080",token:"DEV_TOKEN",poll:3000,channels:["#masterchief"]};
  const Modules={},Bots={},Commands={},Wizards={};

  /* UI */
  const root=document.createElement("div");
  root.style=`position:fixed;bottom:0;right:0;width:780px;height:500px;background:#0b0b0b;color:#ddd;font-family:monospace;border:1px solid #333;z-index:999999;display:flex;flex-direction:column`;
  root.innerHTML=`
    <div style="background:#111;padding:6px;font-weight:bold">IRC Super Control Kernel</div>
    <div id="tabs" style="display:flex;border-bottom:1px solid #333"></div>
    <div id="out" style="flex:1;overflow:auto;padding:6px"></div>
    <input id="in" placeholder="/help" style="border:0;border-top:1px solid #333;background:#000;color:#0f0;padding:6px">`;
  document.body.appendChild(root);

  const out=root.querySelector("#out"),input=root.querySelector("#in"),tabs=root.querySelector("#tabs");
  let activeChannel=CFG.channels[0];
  function log(m){const e=document.createElement('div');e.textContent=m;out.appendChild(e);out.scrollTop=1e9;}

  /* Tabs */
  CFG.channels.forEach(c=>{const t=document.createElement("div");t.textContent=c;t.style="padding:6px;cursor:pointer";t.onclick=()=>{activeChannel=c;out.innerHTML="";log(`Switched to ${c}`);};tabs.appendChild(t);});

  /* API helper */
  const api=(p,b)=>fetch(CFG.api+p,{method:"POST",headers:{"Content-Type":"application/json","X-BRIDGE-TOKEN":CFG.token},body:b?JSON.stringify(b):null}).then(r=>r.json()).catch(()=>({}));

  /* Command router */
  function route(line){const [cmd,...args]=line.trim().split(/\s+/); if(!cmd) return; if(Commands[cmd]) Commands[cmd](args); else log(`Unknown command: ${cmd}`);}
  input.onkeydown=e=>{if(e.key==="Enter"){log(`> ${input.value}`);route(input.value);input.value="";}};

  /* Module system */
  function registerModule(name,mod){Modules[name]=mod; mod.init?.(); log(`[MODULE] ${name} loaded`);} 

  /* Bot runtime */
  function createBot(name,spec){Bots[name]={name,onMessage:spec.onMessage||(()=>{}),commands:spec.commands||{}}; log(`[BOT] ${name} created`);} 

  /* Wizards */
  function wizard(name,steps){Wizards[name]=steps;} 
  function runWizard(name){let i=0; const steps=Wizards[name]; const next=()=>{ if(!steps||!steps[i]) return log(`[WIZARD] ${name} complete`); steps[i++](next,log); }; next(); }

  /* Built-in commands */
  Commands["/help"] = ()=>{log("Commands:"); Object.keys(Commands).forEach(c=>log(' '+c));};
  Commands["/wizard"] = a=> runWizard(a[0]);
  Commands["/load"] = async a=>{ try{ const src = await fetch(a[0]).then(r=>r.text()); eval(src); log('Remote script loaded'); } catch(e){ log('Load error: '+e.message); } };

  /* Core modules */
  registerModule("config",{ init(){ Commands["/conf"] = async a=>{ try{ if(a[0]==="enable") await api('/features/inspircd/module/enable',{module:a[1]}),log('Module enabled'); if(a[0]==="disable") await api('/features/inspircd/module/disable',{module:a[1]}),log('Module disabled'); if(a[0]==="apply") await api('/features/inspircd/apply'),log('Config applied'); if(a[0]==="list"){ const r=await api('/features/inspircd/config'); log(JSON.stringify(r.modules||{},null,2)); } }catch(e){log('conf error: '+e.message);} }; }});

  registerModule("ai",{ init(){ Commands["/ai"] = async a=>{ try{ const r = await api('/irc/module/stream',{session:'super-kernel',module:'qwen_inspircd',args:['--channel',activeChannel,'--prompt',a.join(' ')]}); log('[AI] '+(r.output||r.result||'ok')); }catch(e){log('AI error: '+e.message);} }; }});

  registerModule("bot-factory",{ init(){ Commands["/bot"] = a=>{ try{ if(a[0]==='create'){ createBot(a[1],{ onMessage: m=>{ if(m.includes('hello')) log(`[${a[1]}] hello human`); } }); } }catch(e){log('bot error: '+e.message);} }; }});

  wizard("botgen",[(n,l)=>{l('BotGen Wizard Starting'); n();}, (n,l)=>{ createBot('BotSmith',{commands:{}}); l('BotSmith created'); n(); }]);

  /* Notices polling */
  setInterval(async ()=>{ try{ const r = await api('/irc/notices'); if(r?.lines) r.lines.forEach(l=>log('[NOTICE] '+l)); }catch(e){/*ignore*/} }, CFG.poll);

  log('IRC Super Control Kernel loaded. Try /help | /wizard botgen | /bot create Alpha | /ai ... | /conf list');
  window.IRCSuper={Modules,Bots,Commands,Wizards,registerModule,createBot,wizard};
})();
