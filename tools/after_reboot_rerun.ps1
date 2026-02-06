# After-reboot helper for MasterChief
# Starts main.py, waits for webserver, loads app_installer, registers features,
# and triggers the Windows installer feature for inspircd once the server is ready.

$ROOT = 'C:\Users\Echo\masterchief'
$Python = Join-Path $ROOT 'venv\Scripts\python.exe'
$MainPy = Join-Path $ROOT 'main.py'
$BaseUrl = 'http://127.0.0.1:8080'

Write-Output "[after_reboot] Starting main.py via $Python"
Start-Process -FilePath $Python -ArgumentList '-u', $MainPy -WorkingDirectory $ROOT

function Wait-Url([string]$url,[int]$timeoutSeconds=120) {
    $end = (Get-Date).AddSeconds($timeoutSeconds)
    while((Get-Date) -lt $end) {
        try {
            Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5 | Out-Null
            return $true
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    return $false
}

Write-Output "[after_reboot] Waiting for webserver to become available..."
if (Wait-Url "$BaseUrl/" 120) {
    Write-Output "[after_reboot] Server available — loading addon and invoking installer."
    try { Invoke-RestMethod -Uri "$BaseUrl/addons/load/app_installer" -Method Get -TimeoutSec 60 } catch { Write-Output "load failed: $_" }
    Start-Sleep -Seconds 1
    try { Invoke-RestMethod -Uri "$BaseUrl/addons/register_features/app_installer" -Method Get -TimeoutSec 60 } catch { Write-Output "register failed: $_" }
    Start-Sleep -Seconds 1
    try {
        $body = @{app='inspircd'} | ConvertTo-Json -Compress
        Invoke-RestMethod -Uri "$BaseUrl/feature/run/app_installer.feature_install_windows" -Method Post -Body $body -ContentType 'application/json' -TimeoutSec 120
        Write-Output "[after_reboot] Installer POSTed"
    } catch { Write-Output "installer POST failed: $_" }
} else {
    Write-Output "[after_reboot] Server never became available within timeout."
}

# Clean up scheduled task (if present)
try { schtasks /Delete /TN "MasterChiefAfterReboot" /F | Out-Null; Write-Output "[after_reboot] Scheduled task removed." } catch { }

Write-Output "[after_reboot] Done."
