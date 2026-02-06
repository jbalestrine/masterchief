#!/usr/bin/env pwsh
# Restart MasterChief Flask app under the venv and show recent log output
$repo = 'C:\Users\Echo\masterchief'
Push-Location $repo
try {
    $lines = netstat -ano | findstr ':8080'
    if ($lines) {
        $pids = $lines | ForEach-Object { ($_ -split '\s+')[-1] } | Sort-Object -Unique
        foreach ($pid in $pids) {
            Write-Host "KILLING PID $pid"
            taskkill /PID $pid /F | Out-Null
        }
    }
} catch {
    Write-Host "No existing listeners found or failed to enumerate: $_"
}

# Activate venv then start the app in background, redirecting output to a log
if (Test-Path "$repo\venv\Scripts\Activate.ps1") {
    & "$repo\venv\Scripts\Activate.ps1"
}

$cmd = 'python "' + $repo + '\\main.py" --port 8080 > "' + $repo + '\\masterchief_restart.log" 2>&1'
Start-Process -FilePath cmd.exe -ArgumentList '/c', $cmd -WorkingDirectory $repo -NoNewWindow

Start-Sleep -s 2
Write-Host "Processes (python):"
Get-Process python -ErrorAction SilentlyContinue | Select-Object Id,Path,StartTime

Write-Host "Netstat :8080 entries:"
netstat -ano | findstr ':8080'

if (Test-Path "$repo\masterchief_restart.log") {
    Write-Host "\n--- Last 200 lines of masterchief_restart.log ---\n"
    Get-Content "$repo\masterchief_restart.log" -Tail 200
}

Pop-Location
