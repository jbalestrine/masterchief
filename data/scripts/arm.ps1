# Read file directly
Get-Content .\data\install_status\inspircd.json -Raw | ConvertFrom-Json

# Or call the addon status feature
$body = '{"app":"inspircd"}'
Invoke-RestMethod -Uri 'http://127.0.0.1:8080/feature/run/app_installer.feature_install_status' -Method Post -Body $body -ContentType 'application/json'