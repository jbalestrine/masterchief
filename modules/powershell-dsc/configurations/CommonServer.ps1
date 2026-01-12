# Common Windows Server Configuration
# Base configuration for all Windows servers

Configuration CommonServer
{
    param(
        [Parameter(Mandatory=$false)]
        [string]$ComputerName = "localhost",
        
        [Parameter(Mandatory=$false)]
        [string]$TimeZone = "Eastern Standard Time",
        
        [Parameter(Mandatory=$false)]
        [hashtable]$ConfigurationData
    )
    
    Import-DscResource -ModuleName PSDesiredStateConfiguration
    Import-DscResource -ModuleName ComputerManagementDsc
    Import-DscResource -ModuleName NetworkingDsc
    
    Node $ComputerName
    {
        # Set Time Zone
        TimeZone SetTimeZone
        {
            IsSingleInstance = "Yes"
            TimeZone = $TimeZone
        }
        
        # Configure Windows Firewall
        FirewallProfile DomainFirewall
        {
            Name = "Domain"
            Enabled = "True"
        }
        
        FirewallProfile PrivateFirewall
        {
            Name = "Private"
            Enabled = "True"
        }
        
        FirewallProfile PublicFirewall
        {
            Name = "Public"
            Enabled = "True"
        }
        
        # Install common Windows features
        WindowsFeature TelnetClient
        {
            Ensure = "Absent"
            Name = "Telnet-Client"
        }
        
        WindowsFeature NetFramework48
        {
            Ensure = "Present"
            Name = "NET-Framework-45-Core"
        }
        
        # Configure Windows Update
        Registry DisableAutoUpdate
        {
            Ensure = "Present"
            Key = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
            ValueName = "NoAutoUpdate"
            ValueData = "1"
            ValueType = "Dword"
        }
        
        # Configure Power Plan
        PowerPlan HighPerformance
        {
            IsSingleInstance = "Yes"
            Name = "High performance"
        }
        
        # Disable unnecessary services
        Service XboxLive
        {
            Name = "XblAuthManager"
            State = "Stopped"
            StartupType = "Disabled"
        }
        
        # Configure Event Logs
        Registry EventLogSize
        {
            Ensure = "Present"
            Key = "HKLM:\SYSTEM\CurrentControlSet\Services\EventLog\Application"
            ValueName = "MaxSize"
            ValueData = "104857600"  # 100 MB
            ValueType = "Dword"
        }
        
        # Enable Remote Desktop
        Registry EnableRDP
        {
            Ensure = "Present"
            Key = "HKLM:\System\CurrentControlSet\Control\Terminal Server"
            ValueName = "fDenyTSConnections"
            ValueData = "0"
            ValueType = "Dword"
        }
        
        Firewall AllowRDP
        {
            Name = "RemoteDesktop-UserMode-In-TCP"
            DisplayName = "Allow RDP (3389)"
            Ensure = "Present"
            Enabled = "True"
            Direction = "Inbound"
            Protocol = "TCP"
            LocalPort = "3389"
            Action = "Allow"
        }
    }
}

# Configuration data
$ConfigData = @{
    AllNodes = @(
        @{
            NodeName = "localhost"
            PSDscAllowPlainTextPassword = $true
        }
    )
}
