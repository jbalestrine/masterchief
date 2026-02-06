IRCSuper.registerModule("PrebuiltBots", {
    init: () => {
        ["AlphaBot","BetaBot","GammaBot"].forEach(name=>{
            IRCSuper.createBot(name,{
                onMessage: m=>{ if(m.includes("hello")) IRCSuper.log(`[${name}] hello human`); },
                commands: {"/say": args=>IRCSuper.log(`[${name}] says: `+args.join(" ")) }
            });
        });
        IRCSuper.log("[PrebuiltBots] AlphaBot, BetaBot, GammaBot created");
    }
});
