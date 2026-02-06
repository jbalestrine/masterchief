$sv = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest 'http://127.0.0.1:8080/web_ide/login' -WebSession $sv -UseBasicParsing | Out-Null
Invoke-WebRequest -Uri 'http://127.0.0.1:8080/web_ide/login' -Method Post -Body @{username='ide';password='x'} -WebSession $sv -UseBasicParsing | Out-Null
Write-Output '---addons (auth)---'
try {
    Invoke-RestMethod -Uri 'http://127.0.0.1:8080/api/addons/list' -WebSession $sv -Method Get | ConvertTo-Json -Depth 4 | Write-Output
} catch {
    Write-Output 'ERR addons auth:'
    Write-Output $_.Exception.Message
}
Write-Output '---ado_projects (auth)---'
try {
    Invoke-RestMethod -Uri 'http://127.0.0.1:8080/api/ide/ado/projects' -WebSession $sv -Method Get | ConvertTo-Json -Depth 4 | Write-Output
} catch {
    Write-Output 'ERR projects auth:'
    Write-Output $_.Exception.Message
}
Write-Output '---ado_pipelines (auth)---'
try {
    Invoke-RestMethod -Uri 'http://127.0.0.1:8080/api/ide/ado/pipelines' -WebSession $sv -Method Get | ConvertTo-Json -Depth 4 | Write-Output
} catch {
    Write-Output 'ERR pipelines auth:'
    Write-Output $_.Exception.Message
}
Write-Output '---az_info (auth)---'
try {
    Invoke-RestMethod -Uri 'http://127.0.0.1:8080/api/debug/az_info' -WebSession $sv -Method Get | ConvertTo-Json -Depth 4 | Write-Output
} catch {
    Write-Output 'ERR az_info auth:'
    Write-Output $_.Exception.Message
}
