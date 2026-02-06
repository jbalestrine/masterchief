$timeout=900
for ($i=0; $i -lt $timeout; $i++) {
  try {
    $r = Invoke-RestMethod -Uri http://127.0.0.1:8081/api/echo/model_status -TimeoutSec 5 -ErrorAction Stop
    if ($r.model_loaded) { Write-Output "MODEL_LOADED"; break }
    else { Write-Output "NOT_LOADED: $(Get-Date)" }
  } catch { Write-Output "ERR: $($_.Exception.Message)" }
  Start-Sleep -s 5
}
if ($i -ge $timeout) { Write-Output "MODEL_LOAD_TIMEOUT"; exit 1 }
Write-Output "Running smoke test..."
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\smoke_test.ps1
