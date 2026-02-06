InspIRCd modules and command discovery

- InspIRCd modules (loaded on the IRC server) can register commands, modes, and features when they are loaded by the server administrator.
- A normal IRC client cannot reliably enumerate all module-provided commands remotely. Discovery typically requires one of:
  - Server admin access to inspect the server configuration (modules.conf) or module directory.
  - Reading module documentation shipped with the server or on the module project's website.
  - Using administrative protocols or server-control interfaces (services, WebAdmin) if provided.

Recommendations for this repo:
- The `modules/` directory in this project exposes local helper scripts (server-side) that the web UI can invoke (see `/irc/modules` and `/irc/module`). These are not the same as InspIRCd modules running inside an IRC server process.
- If you need to query an InspIRCd instance for commands, consider one of:
  - Enabling and using a server web-admin/API (if available).
  - SSH/console access to read the server's config and modules.
  - Adding a custom admin endpoint in this webapp that can run privileged server-side queries (requires admin credentials and careful access control).

Security note: executing or exposing server-side module scripts from a web endpoint is powerful but risky. Restrict access (bridge tokens, ACLs) and consider sandboxing long-running or untrusted modules.
