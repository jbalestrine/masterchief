<#
.SYNOPSIS
    Deploys DSC configurations to target nodes

.DESCRIPTION
    This script applies compiled MOF files to target nodes and verifies the configuration.

.PARAMETER MOFPath
    Path to the directory containing MOF files

.PARAMETER ComputerName
    Target computer name(s) to deploy configuration to

.PARAMETER Credential
    Credentials for remote deployment

.PARAMETER Force
    Force application of configuration

.EXAMPLE
    .\Deploy-Configuration.ps1 -MOFPath "C:\DSC\MOF" -ComputerName "WEB01"

.EXAMPLE
    $cred = Get-Credential
    .\Deploy-Configuration.ps1 -MOFPath "C:\DSC\MOF" -ComputerName "WEB01","WEB02" -Credential $cred -Force
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$MOFPath,
    
    [Parameter(Mandatory=$false)]
    [string[]]$ComputerName = @("localhost"),
    
    [Parameter(Mandatory=$false)]
    [PSCredential]$Credential,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Verify MOF path exists
if (-not (Test-Path $MOFPath)) {
    throw "MOF path not found: $MOFPath"
}

Write-Host "Deploying DSC Configurations" -ForegroundColor Cyan
Write-Host "MOF Path: $MOFPath" -ForegroundColor Gray

foreach ($computer in $ComputerName) {
    $mofFile = Join-Path $MOFPath "$computer.mof"
    
    if (-not (Test-Path $mofFile)) {
        Write-Warning "MOF file not found for $computer at $mofFile"
        continue
    }
    
    Write-Host "`nDeploying to: $computer" -ForegroundColor Yellow
    
    try {
        # Build parameters
        $params = @{
            Path = $MOFPath
            Wait = $true
            Verbose = $true
        }
        
        if ($Force) {
            $params.Add("Force", $true)
        }
        
        if ($computer -ne "localhost") {
            $params.Add("ComputerName", $computer)
        }
        
        if ($Credential) {
            $params.Add("Credential", $Credential)
        }
        
        # Apply configuration
        Write-Host "Applying configuration..." -ForegroundColor Gray
        Start-DscConfiguration @params
        
        # Get configuration status
        Start-Sleep -Seconds 5
        $status = Get-DscConfigurationStatus
        
        Write-Host "Configuration Status: $($status.Status)" -ForegroundColor $(if ($status.Status -eq "Success") { "Green" } else { "Red" })
        
        # Test configuration
        Write-Host "Testing configuration compliance..." -ForegroundColor Gray
        $testResult = Test-DscConfiguration -Detailed
        
        if ($testResult.InDesiredState) {
            Write-Host "✓ System is in desired state" -ForegroundColor Green
        } else {
            Write-Warning "System is not in desired state"
            Write-Host "Resources not in desired state:" -ForegroundColor Yellow
            $testResult.ResourcesNotInDesiredState | ForEach-Object {
                Write-Host "  - $($_.ResourceId)" -ForegroundColor Red
            }
        }
    }
    catch {
        Write-Error "Failed to deploy configuration to ${computer}: $_"
    }
}

Write-Host "`nDeployment completed!" -ForegroundColor Cyan
