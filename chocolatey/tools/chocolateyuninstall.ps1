$ErrorActionPreference = 'Stop'

$packageName = 'masterchief'
$installDir = Join-Path $env:ChocolateyInstall 'lib\masterchief\masterchief'

Write-Host "Uninstalling MasterChief DevOps Platform..."

# Try to find the Python command used during installation
$pythonCmd = 'python'
$pythonPathFile = Join-Path $installDir '.python_cmd'
if (Test-Path $pythonPathFile) {
    $pythonCmd = Get-Content $pythonPathFile -Raw
    $pythonCmd = $pythonCmd.Trim()
}

# Uninstall the Python package
try {
    & $pythonCmd.Split()[0] ($pythonCmd.Split() | Select-Object -Skip 1) -m pip uninstall masterchief -y --quiet 2>$null
} catch {
    Write-Warning "Could not uninstall Python package: $_"
}

# Remove the shim
$shimPath = Join-Path $env:ChocolateyInstall 'bin\masterchief.cmd'
if (Test-Path $shimPath) {
    Remove-Item -Path $shimPath -Force
}

# Remove installation directory
if (Test-Path $installDir) {
    Remove-Item -Path $installDir -Recurse -Force
}

Write-Host "MasterChief has been uninstalled."
