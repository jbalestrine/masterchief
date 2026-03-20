
// ── Teams Calendar state ────────────────────────────────────────────────────
let _teamsToken = null;
let _teamsEvents = [];  // raw from API
let _teamsFiltered = []; // after filter
let _calYear = new Date().getFullYear();
let _calMonth = new Date().getMonth();

// Init date range defaults
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
  if(!tenant||!clientId||!clientSecret){ st.textContent='\u26A0 Fill in Tenant ID, Client ID and Secret.'; return; }
  st.textContent='Connecting…';
  fetch('/api/teams/connect',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({tenant_id:tenant,client_id:clientId,client_secret:clientSecret,upn})})
  .then(r=>r.json()).then(j=>{
    if(j.token){
      _teamsToken = j.token;
      st.innerHTML='<span style="color:#4caf50;">\u2705 Connected — '+j.scope+'</span>';
      document.getElementById('teams-connected-banner').style.display='flex';
      // Save non-secret creds
      localStorage.setItem('tm_creds', JSON.stringify({tenant,client_id:clientId,upn}));
    } else {
      st.innerHTML='<span style="color:#f55;">\u274C '+(j.error||JSON.stringify(j))+'</span>';
    }
  }).catch(e=>{ st.innerHTML='<span style="color:#f55;">Error: '+e+'</span>'; });
}

function teamsDisconnect(){
  _teamsToken = null;
  _teamsEvents = [];
  _teamsFiltered = [];
  calRender();
  document.getElementById('teams-connected-banner').style.display='none';
  document.getElementById('tm-conn-status').textContent='Disconnected.';
  document.getElementById('tm-client-secret').value='';
}

function teamsLoadRange(){
  const st = document.getElementById('tm-load-status');
  if(!_teamsToken){ st.innerHTML='<span style="color:#f55;">\u26A0 Connect first.</span>'; return; }
  const start = document.getElementById('tm-range-start').value;
  const end   = document.getElementById('tm-range-end').value;
  const upn   = _teamsUpn || (_tmMode==='app' ? document.getElementById('tm-upn').value.trim() : '');
  if(!start||!end){ st.textContent='\u26A0 Set start and end date.'; return; }
  st.textContent='Loading events…';
  fetch('/api/teams/calendar',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({token:_teamsToken,start_date:start,end_date:end,upn,use_me:_tmMode==='upw'})})
  .then(r=>r.json()).then(j=>{
    if(j.events){
      _teamsEvents = j.events;
      teamsApplyFilter();
      st.innerHTML='<span style="color:#4caf50;">\u2705 Loaded '+j.events.length+' events.</span>';
      document.getElementById('cal-empty').style.display='none';
      calRender();
    } else {
      st.innerHTML='<span style="color:#f55;">\u274C '+(j.error||JSON.stringify(j))+'</span>';
    }
  }).catch(e=>{ st.innerHTML='<span style="color:#f55;">Error: '+e+'</span>'; });
}

function teamsApplyFilter(){
  const txt  = (document.getElementById('tm-filter-text').value||'').toLowerCase();
  const type = document.getElementById('tm-filter-type').value;
  _teamsFiltered = _teamsEvents.filter(ev=>{
    if(txt && !(ev.subject||'').toLowerCase().includes(txt) && !(ev.bodyPreview||'').toLowerCase().includes(txt)) return false;
    if(type==='online' && !ev.isOnlineMeeting) return false;
    if(type==='busy'   && ev.showAs!=='busy') return false;
    if(type==='tentative' && ev.showAs!=='tentative') return false;
    if(type==='free'   && ev.showAs!=='free') return false;
    return true;
  });
  calRender();
}

// ── Calendar rendering ───────────────────────────────────────────────────────
const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];

function calMove(dir){
  _calMonth += dir;
  if(_calMonth < 0){ _calMonth=11; _calYear--; }
  if(_calMonth > 11){ _calMonth=0; _calYear++; }
  calRender();
}

function calRender(){
  document.getElementById('cal-month-title').textContent = MONTHS[_calMonth]+' '+_calYear;
  const today = new Date();
  const firstDay = new Date(_calYear, _calMonth, 1).getDay();
  const daysInMonth = new Date(_calYear, _calMonth+1, 0).getDate();
  const prevDays = new Date(_calYear, _calMonth, 0).getDate();
  const cells = document.getElementById('cal-cells');
  cells.innerHTML='';

  // Build a day→events map for fast lookup
  const dayMap = {};
  (_teamsFiltered.length ? _teamsFiltered : []).forEach(ev=>{
    const d = new Date(ev.start.dateTime||ev.start.date);
    if(d.getFullYear()===_calYear && d.getMonth()===_calMonth){
      const key = d.getDate();
      if(!dayMap[key]) dayMap[key]=[];
      dayMap[key].push(ev);
    }
  });

  // Leading cells from previous month
  for(let i=0;i<firstDay;i++){
    const c=document.createElement('div');
    c.className='cal-cell other-month';
    c.innerHTML=`<div class="cal-num">${prevDays-firstDay+1+i}</div>`;
    cells.appendChild(c);
  }
  // Current month cells
  for(let d=1;d<=daysInMonth;d++){
    const c=document.createElement('div');
    const isToday = d===today.getDate()&&_calMonth===today.getMonth()&&_calYear===today.getFullYear();
    c.className='cal-cell'+(isToday?' today':'');
    let inner=`<div class="cal-num">${d}</div>`;
    const evs=dayMap[d]||[];
    evs.slice(0,3).forEach(ev=>{
      const cls=ev.isOnlineMeeting?'ev-teams':ev.showAs==='tentative'?'ev-tentative':ev.showAs==='busy'?'ev-busy':'';
      const time=ev.start.dateTime?new Date(ev.start.dateTime).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'}):'';
      inner+=`<div class="cal-event ${cls}" title="${(ev.subject||'').replace(/"/g,'&quot;')}" onclick="calShowEvent(${JSON.stringify(JSON.stringify(ev))})"> ${time?time+' ':''}${ev.subject||'(no title)'}</div>`;
    });
    if(evs.length>3) inner+=`<div style="font-size:.65rem;color:#666;">${evs.length-3} more…</div>`;
    c.innerHTML=inner;
    cells.appendChild(c);
  }
  // Trailing cells
  const total=firstDay+daysInMonth;
  const trailing=(total%7===0)?0:7-(total%7);
  for(let i=1;i<=trailing;i++){
    const c=document.createElement('div');
    c.className='cal-cell other-month';
    c.innerHTML=`<div class="cal-num">${i}</div>`;
    cells.appendChild(c);
  }
}

function calShowEvent(jsonStr){
  const ev = JSON.parse(jsonStr);
  const panel = document.getElementById('tm-event-detail');
  panel.style.display='';
  document.getElementById('tm-ev-title').textContent = ev.subject||'(no title)';
  const fmt=(dt)=>{ if(!dt) return '—'; try{ return new Date(dt).toLocaleString(); }catch(e){ return dt; } };
  document.getElementById('tm-ev-when').textContent = fmt(ev.start&&ev.start.dateTime)+' – '+fmt(ev.end&&ev.end.dateTime);
  document.getElementById('tm-ev-where').textContent = (ev.location&&ev.location.displayName)||'—';
  document.getElementById('tm-ev-org').textContent = (ev.organizer&&ev.organizer.emailAddress&&ev.organizer.emailAddress.name)||'—';
  document.getElementById('tm-ev-status').textContent = ev.showAs||'—';
  document.getElementById('tm-ev-type').innerHTML = ev.isOnlineMeeting
    ? '<span class="tag-online">Teams Meeting</span>'
    : '<span class="tag-offline">In-person / Other</span>';
  const linkRow = document.getElementById('tm-ev-link-row');
  if(ev.onlineMeetingUrl||ev.teams_join_url){
    linkRow.style.display='';
    document.getElementById('tm-ev-link').href = ev.onlineMeetingUrl||ev.teams_join_url;
  } else { linkRow.style.display='none'; }
  document.getElementById('tm-ev-body').textContent = ev.bodyPreview||'(no preview)';
  panel.scrollIntoView({behavior:'smooth',block:'nearest'});
}
