IRCSuper.registerModule("Dashboard",{
    init:()=>{
        setInterval(async()=>{
            const r=await fetch("/irc/notices").then(r=>r.json().catch(()=>({}))); 
            if(r?.lines) r.lines.forEach(l=>IRCSuper.log("[NOTICE] "+l));
        },3000);
        IRCSuper.log("[Dashboard] Multi-channel notices active");
    }
});
