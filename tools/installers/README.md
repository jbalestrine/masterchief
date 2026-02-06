Installer scripts for Windows and Ubuntu

Usage
- Windows (PowerShell):
  - Run from project root or call the script directly.
  - Example (elevated PowerShell):
    powershell -NoProfile -ExecutionPolicy Bypass -File tools/installers/install_app_windows.ps1 -AppName inspircd -ChocoPackage inspircd

- Ubuntu (bash):
  - Example (may prompt for sudo):
    ./tools/installers/install_app_ubuntu.sh --app inspircd --apt inspircd

Integration
- The `app_installer` addon at `data/uploads/extracted/app_installer/addon.py` exposes runtime features:
  - `feature_install_windows` — runs the Windows installer script in background.
  - `feature_install_ubuntu` — runs the Ubuntu installer script in background.
  - `feature_install_status` — returns the last status JSON written to `data/install_status/<app>.json`.

The web UI can call these features (via `/feature/run/<addon>.<feature>`) to start installations and poll status.
