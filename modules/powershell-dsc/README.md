# PowerShell DSC Configurations for MasterChief Platform

This directory contains PowerShell Desired State Configuration (DSC) configurations for Windows server management.

## Directory Structure

```
powershell-dsc/
├── configurations/    # DSC configuration scripts
│   ├── WebServer.ps1  # Web server configuration
│   ├── AppServer.ps1  # Application server configuration
│   └── Database.ps1   # Database server configuration
├── resources/         # Custom DSC resources
└── scripts/           # Helper and compilation scripts
    ├── Compile-Configuration.ps1
    └── Deploy-Configuration.ps1
```

## Requirements

- PowerShell 7.0+
- DSC modules:
  - PSDesiredStateConfiguration
  - xPSDesiredStateConfiguration
  - NetworkingDsc
  - ComputerManagementDsc

## Installation

Install required DSC modules:

```powershell
# Install DSC modules
Install-Module -Name PSDesiredStateConfiguration -Force
Install-Module -Name xPSDesiredStateConfiguration -Force
Install-Module -Name NetworkingDsc -Force
Install-Module -Name ComputerManagementDsc -Force
```

## Usage

### Compile Configuration

```powershell
# Compile DSC configuration
.\scripts\Compile-Configuration.ps1 -ConfigurationName "WebServer" -OutputPath "C:\DSC\MOF"
```

### Apply Configuration

```powershell
# Apply DSC configuration
Start-DscConfiguration -Path "C:\DSC\MOF" -Wait -Verbose -Force
```

### Check Configuration Status

```powershell
# Get DSC configuration status
Get-DscConfigurationStatus
```

### Test Configuration

```powershell
# Test if system is in desired state
Test-DscConfiguration -Path "C:\DSC\MOF"
```

## Configuration Structure

Each DSC configuration follows this pattern:

```powershell
Configuration MyConfiguration
{
    param(
        [string]$ComputerName = "localhost",
        [hashtable]$ConfigurationData
    )
    
    Import-DscResource -ModuleName PSDesiredStateConfiguration
    
    Node $ComputerName
    {
        # DSC resources here
    }
}
```

## Integration with CI/CD

DSC configurations are compiled during CI/CD pipeline execution:

1. Configuration scripts are validated
2. MOF files are generated
3. MOF files are deployed to target servers
4. Configuration is applied and verified

## Best Practices

1. **Idempotency**: Ensure configurations can be applied multiple times
2. **Modularity**: Break complex configurations into reusable resources
3. **Testing**: Test configurations in dev before production
4. **Versioning**: Version control DSC configurations
5. **Monitoring**: Monitor DSC compliance regularly
