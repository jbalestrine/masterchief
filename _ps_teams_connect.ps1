Import-Module MicrosoftTeams -ErrorAction Stop
$conn = Connect-MicrosoftTeams -ErrorAction Stop
Write-Host ("Signed in as: " + $conn.Account + "  Tenant: " + $conn.TenantId)
Write-Host ""
Write-Host "--- Your Teams ---"
$teams = Get-Team -ErrorAction SilentlyContinue
if ($teams) {
    $teams | Select-Object DisplayName, Visibility, GroupId | Format-Table -AutoSize
} else {
    Write-Host "(No teams found or insufficient permissions)"
}
