try {
    Get-WinEvent -FilterHashtable @{LogName='Application','System','Security'; Level=2} `
                 -MaxEvents 10 `
                 -ErrorAction Stop |
    Select-Object TimeCreated, Id, LevelDisplayName, ProviderName, Message |
    Format-Table -AutoSize
}
catch {
    Write-Host "Error retrieving logs: $($_.Exception.Message)" -ForegroundColor Red
}
