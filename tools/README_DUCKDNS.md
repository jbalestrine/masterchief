DuckDNS setup (Windows)

1) Create a DuckDNS token
   - Sign in at https://www.duckdns.org
   - Add a subdomain (e.g. `myhost`) and copy the provided token

2) Quick manual update (PowerShell)
   ```powershell
   Invoke-RestMethod "https://www.duckdns.org/update?domains=your-sub&token=YOURTOKEN&ip="
   ```

3) Automated updater (this repo)
   - `tools/duckdns_update.ps1` — updates DuckDNS for a supplied `-Domain` and `-Token`.
   - `tools/setup_duckdns_task.ps1` — creates a scheduled task to run the updater every N minutes and optionally creates a `MasterChiefApp` scheduled task to start `main.py` at system startup.

Usage example (Run as Administrator from repo root):
```powershell
# create a venv and install requirements first
python -m venv .\venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# create periodic DuckDNS updater and autostart task for app
.\tools\setup_duckdns_task.ps1 -Domain myhost -Token YOURTOKEN -IntervalMinutes 5 -InstallAppTask
```

Security
- Do not commit tokens into git. Use Windows Credential Manager or environment variables for long-term security.

Port forwarding / firewall
- If you expose ports directly (8080, 6667), ensure your router forwards those ports to this Windows host and Windows Firewall allows them.
- Alternatively use a tunnel like `cloudflared` to avoid port-forwarding.
