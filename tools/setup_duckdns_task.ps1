<#
Create scheduled tasks for DuckDNS updater and optionally start the MasterChief app at boot.

Usage:
  Run as Administrator in PowerShell.
  .\setup_duckdns_task.ps1 -Domain mysub -Token <your-duck-token> -InstallAppTask

Parameters:
  -Domain: DuckDNS subdomain (eg 'myhost' for myhost.duckdns.org)
  -Token:  DuckDNS token from duckdns.org
  -IntervalMinutes: how often to run updater (default 5)
  -InstallAppTask: if specified, will create a scheduled task `MasterChiefApp` that runs on system startup.
  -PythonExe: optional full path to python executable to run the app (defaults to .\venv\Scripts\python.exe inside repo)

This script creates two scheduled tasks:
  - DuckDNSUpdater (runs every N minutes)
  - MasterChiefApp (optional) runs at system startup

Security: Do NOT commit tokens to source control. Prefer using Windows Credential Manager or environment variables.
#>
param(
  [Parameter(Mandatory=$true)] [string] $Domain,
  [Parameter(Mandatory=$true)] [string] $Token,
  [int] $IntervalMinutes = 5,
  [switch] $InstallAppTask,
  [string] $PythonExe = ""
)

function Quote($s){ return '"' + $s + '"' }

$repo = (Get-Location).Path
$duckScript = Join-Path $repo 'tools\duckdns_update.ps1'
if(-not (Test-Path $duckScript)){
  Write-Error "duckdns_update.ps1 not found at $duckScript"
  exit 2
}

# Build action for DuckDNS task
$action = "powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File $duckScript -Domain $Domain -Token $Token"
$taskName = "DuckDNSUpdater_$Domain"

# create scheduled task to run every $IntervalMinutes
schtasks /Delete /TN $taskName /F | Out-Null
$create = "schtasks /Create /SC MINUTE /MO $IntervalMinutes /TN $taskName /TR $action /F /RL HIGHEST"
Write-Host "Creating scheduled task: $taskName (every $IntervalMinutes minutes)"
Write-Host $create
Invoke-Expression $create

if($InstallAppTask){
  if(-not $PythonExe){
    $candidate = Join-Path $repo 'venv\Scripts\python.exe'
    if(Test-Path $candidate){ $PythonExe = $candidate } else { $PythonExe = 'python' }
  }
  $mainScript = Join-Path $repo 'main.py'
  $appAction = "`"$PythonExe`" `"$mainScript`""
  $appTask = 'MasterChiefApp'
  schtasks /Delete /TN $appTask /F | Out-Null
  $createApp = "schtasks /Create /SC ONSTART /TN $appTask /TR $appAction /F /RL HIGHEST"
  Write-Host "Creating MasterChief autostart task: $appTask"
  Write-Host $createApp
  Invoke-Expression $createApp
}

Write-Host "Done. Verify tasks in Task Scheduler or with `schtasks /Query`."
