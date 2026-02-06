IRCSuper.registerModule("ChanServ", {
    init: () => { 
        IRCSuper.Commands["/chan"] = args => IRCSuper.log("[ChanServ] "+args.join(" ")); 
        IRCSuper.log("[ChanServ] Ready"); 
    }
});
