# MasterChief DevOps — Roku Channel

A SceneGraph/BrightScript channel that displays your MasterChief DevOps
dashboard live on any Roku device.

---

## Layout

```
┌─────────────────────────────────────────────────────┐
│  ⬛ MasterChief DevOps                    HH:MM:SS  │  ← header
├──────────┬──────────┬──────────┬──────────┬─────────┤
│ Pipelines│  Cloud   │  Notifs  │ Echo AI  │  Diag   │  ← tabs
├──────────┴──────────┴──────────┴──────────┴─────────┤
│                                                     │
│           Current panel content (scrollable)        │
│                                                     │
├─────────────────────────────────────────────────────┤
│  ◀ ▶ Switch tab   ▲▼ Scroll   * Refresh   Back/Home │
└─────────────────────────────────────────────────────┘
```

### Panels

| Tab | API endpoint | Data shown |
|-----|-------------|-----------|
| Pipelines | `GET /api/pipelines` | Name, status, branch, last run |
| Cloud | `GET /api/cloud/accounts` | Account, provider, region, health |
| Notifs | `GET /api/notifications` | Severity, title, source, time |
| Echo AI | `GET /api/echo/status` | Model, status, capabilities, hooks |
| Diagnostics | `GET /sys/diagnostics` | Route/function counts, issue list |

Auto-refreshes every **30 seconds**.

---

## Quick Start

### 1. Generate images (one-time)

Requires Pillow (already in requirements.txt):

```powershell
cd roku
python make_images.py
cd ..
```

### 2. Set your server IP

> **Important:** A real Roku device cannot reach `127.0.0.1` on your PC.
> You must use your machine's LAN IP address.

Find your IP:
```powershell
(Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notmatch "Loopback"} | Select-Object -First 1).IPAddress
```

Then replace `127.0.0.1` with that IP in **all 5 panel XML files**:

```powershell
# PowerShell one-liner — replace before packaging
$ip = "192.168.1.50"   # <-- your actual IP
Get-ChildItem roku\components\*Panel.xml | ForEach-Object {
    (Get-Content $_.FullName) -replace "127\.0\.0\.1", $ip |
    Set-Content $_.FullName
}
```

### 3. Package the channel (zip it)

Roku channels are deployed as `.zip` archives with the
`manifest` at the root:

```powershell
Push-Location roku
Compress-Archive -Path manifest,source,components,images -DestinationPath ..\masterchief-roku.zip -Force
Pop-Location
Write-Host "Packaged: masterchief-roku.zip"
```

### 4. Enable Developer Mode on the Roku

1. On the Roku remote press: **Home × 3, Up × 2, Right, Left, Right, Left, Right**
2. Write down the **Dev server IP** shown on screen (e.g. `192.168.1.x:8080`)
3. Open `http://<roku-dev-ip>` in a browser on your PC

### 5. Sideload the channel

1. Browse to your Roku's developer web UI: `http://<roku-dev-ip>`
2. Log in with username `rokudev` and the password you set
3. Click **"Upload Channel Zip"** → select `masterchief-roku.zip`
4. Click **"Install"**

The **MasterChief DevOps** channel will appear in your Roku home screen.

---

## Remote Controls

| Button | Action |
|--------|--------|
| ◀ Left | Previous tab |
| ▶ Right | Next tab |
| ▲ Up | Scroll panel up |
| ▼ Down | Scroll panel down |
| ⭐ Replay (*) | Force refresh current panel |
| Back / Home | Exit channel |

---

## Adding CORS headers (if needed)

If the Roku reports HTTP errors, add this to your Flask routes in `main.py`:

```python
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
```

---

## File Structure

```
roku/
├── manifest                  — Roku channel metadata
├── make_images.py            — One-time image generator
├── images/
│   ├── icon_focus_hd.png     — 336×210 focused icon
│   ├── icon_side_hd.png      — 108×69 side icon
│   └── splash_hd.png         — 1280×720 launch splash
├── source/
│   ├── main.brs              — Entry point
│   └── panelUtils.brs        — Shared helpers (colour, formatting)
└── components/
    ├── ApiTask.xml            — Background HTTP task node
    ├── MainScene.xml          — Root scene, tabs, timer, key handling
    ├── PipelinesPanel.xml     — CI/CD pipelines list
    ├── CloudPanel.xml         — Cloud account health
    ├── NotifsPanel.xml        — Notifications / alerts
    ├── EchoPanel.xml          — Echo AI status + capabilities
    └── DiagPanel.xml          — System diagnostics + issue list
```
