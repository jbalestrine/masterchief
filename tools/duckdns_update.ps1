<#
PowerShell DuckDNS updater
Usage examples:
  .\duckdns_update.ps1 -Domain mysub -Token <your-token>
  .\duckdns_update.ps1 -Domain mysub -Token <your-token> -Ip 1.2.3.4

This script updates DuckDNS with the current public IP (if -Ip not provided).
It returns the DuckDNS service response ("OK" is success).
#>
param(
  [Parameter(Mandatory=$true)] [string] $Domain,
  [Parameter(Mandatory=$true)] [string] $Token,
  [string] $Ip = ''
)

try{
  $url = "https://www.duckdns.org/update?domains=$Domain&token=$Token&ip=$Ip"
  Write-Host "Calling DuckDNS: $url"
  $resp = Invoke-RestMethod -Uri $url -Method Get -UseBasicParsing -TimeoutSec 15
  Write-Host "DuckDNS response:`n$resp"
  if($resp -match 'OK'){
    exit 0
  } else {
    exit 2
  }
}catch{
  Write-Error "DuckDNS update failed: $_"
  exit 1
}
