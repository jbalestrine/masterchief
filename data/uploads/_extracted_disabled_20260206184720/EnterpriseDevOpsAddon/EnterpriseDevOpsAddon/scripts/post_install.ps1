
Write-Host "Starting post-install automation"

$log = "C:\EnterpriseSetup\install.log"
New-Item -ItemType Directory -Force -Path (Split-Path $log)

winget install --id Microsoft.VisualStudioCode -e --silent | Out-File $log -Append
winget install --id Git.Git -e --silent | Out-File $log -Append
winget install --id Notepad++.Notepad++ -e --silent | Out-File $log -Append

Write-Host "Post-install complete"
