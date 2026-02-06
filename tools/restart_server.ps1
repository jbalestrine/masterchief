$procs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and $_.CommandLine -match 'main.py' }
if($procs){
    foreach($p in $procs){
        Write-Host "Killing PID: $($p.ProcessId) -> $($p.CommandLine)";
        taskkill /PID $p.ProcessId /F
    }
} else {
    Write-Host 'No main.py processes'
}
Start-Sleep -Seconds 1
$env:SKIP_MODEL_LOAD='1'
Set-Location -Path 'C:/Users/Echo/masterchief'
Start-Process -FilePath .\venv\Scripts\python.exe -ArgumentList 'main.py','--port','8081' -WindowStyle Hidden
Write-Host 'restart_server.ps1 completed'