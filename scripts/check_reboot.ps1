# Check if a reboot is pending in Windows
# Works on Windows 7/10/11 and Windows Server

function Test-PendingReboot {
    [CmdletBinding()]
    param()

    $pending = $false

    try {
        # 1. Check Component Based Servicing (Windows Updates)
        if (Test-Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending") {
            $pending = $true
        }

        # 2. Check Windows Update Auto Update
        if (Test-Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired") {
            $pending = $true
        }

        # 3. Check Pending File Rename Operations
        $pendingFileRename = Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager" -Name "PendingFileRenameOperations" -ErrorAction SilentlyContinue
        if ($pendingFileRename -and $pendingFileRename.PendingFileRenameOperations) {
            $pending = $true
        }

        # 4. Check WMI for pending reboot (for some server roles)
        $ccm = Get-WmiObject -Namespace "ROOT\ccm\ClientSDK" -Class CCM_ClientUtilities -ErrorAction SilentlyContinue
        if ($ccm) {
            $result = $ccm.DetermineIfRebootPending()
            if ($result.RebootPending -or $result.IsHardRebootPending) {
                $pending = $true
            }
        }
    }
    catch {
        Write-Warning "Error checking reboot status: $_"
    }

    return $pending
}

# Run the check
if (Test-PendingReboot) {
    Write-Host "A reboot is pending." -ForegroundColor Yellow
} else {
    Write-Host "No reboot is pending." -ForegroundColor Green
}
