<#
.SYNOPSIS
    Compiles DSC configurations to MOF files

.DESCRIPTION
    This script compiles DSC configuration scripts into MOF files
    that can be applied to target nodes.

.PARAMETER ConfigurationName
    Name of the DSC configuration to compile

.PARAMETER ConfigurationPath
    Path to the configuration script file

.PARAMETER OutputPath
    Path where MOF files will be generated

.PARAMETER ComputerName
    Target computer name(s) for the configuration

.EXAMPLE
    .\Compile-Configuration.ps1 -ConfigurationName "WebServer" -OutputPath "C:\DSC\MOF"

.EXAMPLE
    .\Compile-Configuration.ps1 -ConfigurationPath ".\WebServer.ps1" -OutputPath "C:\DSC\MOF" -ComputerName "WEB01","WEB02"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$ConfigurationName,
    
    [Parameter(Mandatory=$false)]
    [string]$ConfigurationPath,
    
    [Parameter(Mandatory=$true)]
    [string]$OutputPath,
    
    [Parameter(Mandatory=$false)]
    [string[]]$ComputerName = @("localhost"),
    
    [Parameter(Mandatory=$false)]
    [hashtable]$ConfigurationData
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Resolve configuration path
if ($ConfigurationPath) {
    $configFile = Get-Item $ConfigurationPath
} elseif ($ConfigurationName) {
    $configFile = Get-Item "$PSScriptRoot\..\configurations\$ConfigurationName.ps1"
} else {
    throw "Either ConfigurationName or ConfigurationPath must be specified"
}

Write-Host "Compiling DSC Configuration: $($configFile.Name)" -ForegroundColor Cyan

# Load the configuration
. $configFile.FullName

# Create output directory if it doesn't exist
if (-not (Test-Path $OutputPath)) {
    New-Item -Path $OutputPath -ItemType Directory -Force | Out-Null
    Write-Host "Created output directory: $OutputPath" -ForegroundColor Green
}

# Compile configuration for each computer
foreach ($computer in $ComputerName) {
    Write-Host "Compiling configuration for: $computer" -ForegroundColor Yellow
    
    try {
        # Get configuration name from file
        $configurationFunctionName = $configFile.BaseName
        
        # Invoke the configuration
        if ($ConfigurationData) {
            & $configurationFunctionName -ComputerName $computer -OutputPath $OutputPath -ConfigurationData $ConfigurationData
        } else {
            & $configurationFunctionName -ComputerName $computer -OutputPath $OutputPath
        }
        
        Write-Host "Successfully compiled configuration for $computer" -ForegroundColor Green
        Write-Host "MOF file location: $OutputPath\$computer.mof" -ForegroundColor Gray
    }
    catch {
        Write-Error "Failed to compile configuration for ${computer}: $_"
    }
}

Write-Host "`nCompilation completed!" -ForegroundColor Cyan
Write-Host "MOF files are ready in: $OutputPath" -ForegroundColor Green
