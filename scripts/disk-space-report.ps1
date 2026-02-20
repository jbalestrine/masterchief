<# .SYNOPSIS Disk Space Report #>
param([int]$WarningThresholdPct = 80)

Write-Host "[MasterChief] Disk Space Report" -ForegroundColor Green
Write-Host ("=" * 60)

Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object {
    $usedPct = [math]::Round((($_.Size - $_.FreeSpace) / $_.Size) * 100, 1)
    $freeGB  = [math]::Round($_.FreeSpace / 1GB, 2)
    $totalGB = [math]::Round($_.Size / 1GB, 2)
    $color   = if ($usedPct -ge $WarningThresholdPct) { "Red" } else { "Green" }

    Write-Host ("
  Drive {0}" -f $_.DeviceID) -ForegroundColor Cyan
    Write-Host ("  Total: {0} GB | Free: {1} GB | Used: {2}%" -f $totalGB, $freeGB, $usedPct) -ForegroundColor $color
    $bar = ('#' * [math]::Floor($usedPct / 2)) + ('-' * (50 - [math]::Floor($usedPct / 2)))
    Write-Host ("  [{0}]" -f $bar)
}