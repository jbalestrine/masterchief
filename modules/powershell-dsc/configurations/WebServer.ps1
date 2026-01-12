# Web Server DSC Configuration
# Configures IIS web server with common settings

Configuration WebServer
{
    param(
        [Parameter(Mandatory=$false)]
        [string]$ComputerName = "localhost",
        
        [Parameter(Mandatory=$false)]
        [string]$WebsiteName = "Default Web Site",
        
        [Parameter(Mandatory=$false)]
        [string]$WebsitePath = "C:\inetpub\wwwroot",
        
        [Parameter(Mandatory=$false)]
        [int]$Port = 80,
        
        [Parameter(Mandatory=$false)]
        [hashtable]$ConfigurationData
    )
    
    Import-DscResource -ModuleName PSDesiredStateConfiguration
    Import-DscResource -ModuleName xWebAdministration
    
    Node $ComputerName
    {
        # Install IIS
        WindowsFeature IIS
        {
            Ensure = "Present"
            Name = "Web-Server"
        }
        
        WindowsFeature IISManagementTools
        {
            Ensure = "Present"
            Name = "Web-Mgmt-Tools"
            DependsOn = "[WindowsFeature]IIS"
        }
        
        WindowsFeature ASPNet45
        {
            Ensure = "Present"
            Name = "Web-Asp-Net45"
            DependsOn = "[WindowsFeature]IIS"
        }
        
        # Configure Default App Pool
        xWebAppPool DefaultAppPool
        {
            Name = "DefaultAppPool"
            Ensure = "Present"
            State = "Started"
            managedRuntimeVersion = "v4.0"
            managedPipelineMode = "Integrated"
            DependsOn = "[WindowsFeature]IIS"
        }
        
        # Ensure website directory exists
        File WebsiteDirectory
        {
            Ensure = "Present"
            Type = "Directory"
            DestinationPath = $WebsitePath
        }
        
        # Configure Website
        xWebsite DefaultWebSite
        {
            Ensure = "Present"
            Name = $WebsiteName
            State = "Started"
            PhysicalPath = $WebsitePath
            ApplicationPool = "DefaultAppPool"
            BindingInfo = @(
                MSFT_xWebBindingInformation
                {
                    Protocol = "HTTP"
                    Port = $Port
                    IPAddress = "*"
                }
            )
            DependsOn = "[WindowsFeature]IIS","[File]WebsiteDirectory"
        }
        
        # Configure Firewall
        Firewall AllowHTTP
        {
            Name = "IIS-WebServerRole-HTTP-In-TCP"
            DisplayName = "Allow HTTP (80)"
            Ensure = "Present"
            Enabled = "True"
            Direction = "Inbound"
            Protocol = "TCP"
            LocalPort = $Port
            Action = "Allow"
        }
        
        # Configure logging
        Registry IISLogging
        {
            Ensure = "Present"
            Key = "HKLM:\SOFTWARE\Microsoft\InetStp"
            ValueName = "LoggingEnabled"
            ValueData = "1"
            ValueType = "Dword"
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
