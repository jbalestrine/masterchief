IRCSuper.wizard("BotSetup", [
    (next, log) => { log("Step 1: Create DeltaBot"); next(); },
    (next, log) => { IRCSuper.createBot("DeltaBot",{onMessage:m=>log("[DeltaBot] Got: "+m)}); log("DeltaBot created"); next(); },
    (next, log) => { log("Step 2: Create EpsilonBot"); IRCSuper.createBot("EpsilonBot",{onMessage:m=>log("[EpsilonBot] Got: "+m)}); next(); },
    (next, log) => { log("Wizard Complete!"); next(); }
]);
