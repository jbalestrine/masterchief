IRCSuper.registerModule("NickServ", {
    init: () => { 
        IRCSuper.Commands["/nick"] = args => IRCSuper.log("[NickServ] "+args.join(" ")); 
        IRCSuper.log("[NickServ] Ready"); 
    }
});
