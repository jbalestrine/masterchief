# Windows Server Base Configuration
# PowerShell DSC Configuration for MasterChief Platform

Configuration WebServerConfig {
    param (
        [Parameter(Mandatory=$true)]
        [string]$ComputerName,
        
        [Parameter(Mandatory=$false)]
        [string]$Environment = "Production"
    )
    
    Import-DscResource -ModuleName PSDesiredStateConfiguration
    Import-DscResource -ModuleName xWebAdministration
    Import-DscResource -ModuleName xNetworking
    
    Node $ComputerName {
        
        # Install IIS
        WindowsFeature IIS {
            Ensure = "Present"
            Name   = "Web-Server"
        }
        
        WindowsFeature IISManagement {
            Ensure    = "Present"
            Name      = "Web-Mgmt-Console"
            DependsOn = "[WindowsFeature]IIS"
        }
        
        # Install ASP.NET
        WindowsFeature AspNet45 {
            Ensure    = "Present"
            Name      = "Web-Asp-Net45"
            DependsOn = "[WindowsFeature]IIS"
        }
        
        # Configure application pool
        xWebAppPool MasterChiefAppPool {
            Ensure       = "Present"
            Name         = "MasterChiefAppPool"
            State        = "Started"
            autoStart    = $true
            managedRuntimeVersion = "v4.0"
            DependsOn    = "[WindowsFeature]IIS"
        }
        
        # Create website directory
        File WebsiteDirectory {
            Ensure          = "Present"
            Type            = "Directory"
            DestinationPath = "C:\inetpub\wwwroot\masterchief"
        }
        
        # Configure website
        xWebsite MasterChiefWebsite {
            Ensure          = "Present"
            Name            = "MasterChief"
            State           = "Started"
            PhysicalPath    = "C:\inetpub\wwwroot\masterchief"
            ApplicationPool = "MasterChiefAppPool"
            BindingInfo     = @(
                MSFT_xWebBindingInformation {
                    Protocol = "HTTP"
                    Port     = 80
                }
            )
            DependsOn       = @("[WindowsFeature]IIS", "[File]WebsiteDirectory", "[xWebAppPool]MasterChiefAppPool")
        }
        
        # Configure firewall
        xFirewall AllowHTTP {
            Name        = "MasterChief-HTTP"
            DisplayName = "MasterChief HTTP"
            Ensure      = "Present"
            Enabled     = "True"
            Direction   = "Inbound"
            LocalPort   = "80"
            Protocol    = "TCP"
            Action      = "Allow"
        }
        
        xFirewall AllowHTTPS {
            Name        = "MasterChief-HTTPS"
            DisplayName = "MasterChief HTTPS"
            Ensure      = "Present"
            Enabled     = "True"
            Direction   = "Inbound"
            LocalPort   = "443"
            Protocol    = "TCP"
            Action      = "Allow"
        }
        
        # Disable default website
        xWebsite DefaultWebsite {
            Ensure       = "Present"
            Name         = "Default Web Site"
            State        = "Stopped"
            PhysicalPath = "C:\inetpub\wwwroot"
            DependsOn    = "[WindowsFeature]IIS"
        }
        
        # Configure local security policy
        Registry DisableIEESC {
            Ensure    = "Present"
            Key       = "HKLM:\SOFTWARE\Microsoft\Active Setup\Installed Components\{A509B1A7-37EF-4b3f-8CFC-4F3A74704073}"
            ValueName = "IsInstalled"
            ValueData = "0"
            ValueType = "Dword"
        }
        
        # Set timezone
        TimeZone SetTimeZone {
            IsSingleInstance = "Yes"
            TimeZone         = "Eastern Standard Time"
        }
        
        # Configure Windows Update
        Registry AutoUpdateSettings {
            Ensure    = "Present"
            Key       = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
            ValueName = "NoAutoUpdate"
            ValueData = "0"
            ValueType = "Dword"
        }
    }
}

# Generate MOF file
# WebServerConfig -ComputerName "WEB01" -Environment "Production" -OutputPath "C:\DSC\Config"

# Apply configuration
# Start-DscConfiguration -Path "C:\DSC\Config" -Wait -Verbose -Force
