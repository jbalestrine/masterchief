# IRC + Anope Setup

This document describes how to bring up an InspIRCd + Anope stack and link them so you have NickServ/ChanServ available.

1) Generate configs and start the stack

From PowerShell (Git Bash or WSL recommended):
```bash
bash tools/setup_irc_stack.sh
```

The script will generate random service passwords and write them to `data/irc_service_passwords.json`, write Anope config to `data/anope_conf/services.conf` and a link fragment to `data/inspircd_conf/link.conf`, then start the docker-compose stack defined in `tools/irc_stack_compose.yml`.

2) Verify

- Check InspIRCd logs: `docker logs -f inspircd`
- Check Anope logs: `docker logs -f anope`
- Use `mIRC` or `irssi` to connect to `localhost:6667` and test `/msg nickserv help` or `/msg chanserv help`.

3) Notes

- The script assumes `docker` and `docker compose` are installed and available.
- Adjust templates in `templates/` if you need custom configuration before starting.
