Write-Host "Hello from PowerShell!"
Write-Host "Current directory: $(Get-Location)"
Write-Host "Today's date: $(Get-Date)"
Get-ChildItem -Path C:\Users\Echo\Downloads | Select-Object Name