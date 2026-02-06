@echo off
REM Run MasterChief after-reboot helper, then delete this shortcut script
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\Echo\masterchief\tools\after_reboot_rerun.ps1"
timeout /t 5 /nobreak > nul
del "%~f0" > nul 2>&1