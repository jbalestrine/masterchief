/**
 * MODULE TEMPLATE CONFIGURATION GUIDE
 * 
 * This file demonstrates how to create custom module templates
 * for the DevOps Master Suite.
 */

// ==================== MODULE TYPES ====================

const MODULE_TEMPLATES = {
  
  // Web Application Module
  webapp: {
    name: 'Web Application',
    description: 'Full-stack web application with frontend and backend',
    structure: {
      files: [
        'index.html',
        'style.css',
        'script.js',
        'package.json',
        'server.js',
        'README.md'
      ],
      directories: [
        'public',
        'src',
        'assets',
        'config'
      ]
    },
    scripts: [
      'Install-WebApp.ps1',
      'Start-WebApp.ps1',
      'Stop-WebApp.ps1',
      'Deploy-WebApp.ps1',
      'Configure-IIS.ps1'
    ],
    config: {
      port: 3000,
      server: 'nodejs',
      autoStart: true,
      installDeps: true
    }
  },

  // Scale-Out File Server (SOFS) Module
  sofs: {
    name: 'Scale-Out File Server',
    description: 'High-availability clustered file server',
    structure: {
      files: [
        'setup.ps1',
        'config.xml',
        'cluster-config.json',
        'shares.json',
        'README.md'
      ],
      directories: [
        'scripts',
        'logs',
        'config'
      ]
    },
    scripts: [
      'Install-SOFS.ps1',
      'Configure-Cluster.ps1',
      'Add-ClusterNode.ps1',
      'Create-FileShares.ps1',
      'Set-Permissions.ps1',
      'Test-Cluster.ps1',
      'Backup-Config.ps1'
    ],
    config: {
      clusterName: 'SOFSCluster',
      nodes: ['Node1', 'Node2', 'Node3'],
      clusterIP: '10.0.0.100',
      fileShareWitness: '\\\\FileServer\\Witness',
      shares: [
        { name: 'Share1', path: 'C:\\ClusterStorage\\Volume1\\Share1' },
        { name: 'Share2', path: 'C:\\ClusterStorage\\Volume1\\Share2' }
      ]
    },
    requirements: [
      'Windows Server 2016+',
      'Failover Clustering Feature',
      'File Server Role',
      'Active Directory'
    ]
  },

  // IRC Server Module
  irc: {
    name: 'IRC Chat Server',
    description: 'InspIRCd-based chat server with modules',
    structure: {
      files: [
        'inspircd.conf',
        'motd.txt',
        'rules.txt',
        'opers.conf',
        'modules.conf',
        'start.sh',
        'stop.sh'
      ],
      directories: [
        'modules',
        'logs',
        'data',
        'ssl'
      ]
    },
    scripts: [
      'Install-InspIRCd.ps1',
      'Configure-IRC.ps1',
      'Add-Channel.ps1',
      'Add-Operator.ps1',
      'Enable-SSL.ps1',
      'Manage-Modules.ps1'
    ],
    config: {
      serverName: 'irc.example.com',
      port: 6667,
      sslPort: 6697,
      maxUsers: 1000,
      channels: ['#general', '#support', '#dev'],
      operators: []
    }
  },

  // Shoutcast Server Module
  shoutcast: {
    name: 'Shoutcast Media Server',
    description: 'Audio streaming server for internet radio',
    structure: {
      files: [
        'sc_serv.conf',
        'sc_serv_simple.conf',
        'start.sh',
        'playlist.lst',
        'README.md'
      ],
      directories: [
        'playlists',
        'logs',
        'music',
        'backups'
      ]
    },
    scripts: [
      'Install-Shoutcast.ps1',
      'Configure-Server.ps1',
      'Add-DJ.ps1',
      'Manage-Playlists.ps1',
      'Monitor-Listeners.ps1'
    ],
    config: {
      port: 8000,
      adminPassword: 'changeme',
      djPassword: 'changeme',
      maxUsers: 100,
      bitrate: 128
    }
  },

  // Docusaurus Documentation Module
  docusaurus: {
    name: 'Docusaurus Documentation Site',
    description: 'Modern documentation website',
    structure: {
      files: [
        'docusaurus.config.js',
        'sidebars.js',
        'package.json',
        'README.md'
      ],
      directories: [
        'docs',
        'blog',
        'src',
        'static',
        'i18n'
      ]
    },
    scripts: [
      'Install-Docusaurus.ps1',
      'Build-Docs.ps1',
      'Deploy-Docs.ps1',
      'Update-Content.ps1'
    ],
    config: {
      title: 'My Documentation',
      tagline: 'Documentation made easy',
      url: 'https://docs.example.com',
      baseUrl: '/',
      port: 3001
    }
  },

  // Node.js API Server Module
  api: {
    name: 'REST API Service',
    description: 'RESTful API server with Express.js',
    structure: {
      files: [
        'server.js',
        'routes.js',
        'controllers.js',
        'models.js',
        'middleware.js',
        'package.json',
        '.env.example'
      ],
      directories: [
        'routes',
        'controllers',
        'models',
        'middleware',
        'utils',
        'tests'
      ]
    },
    scripts: [
      'Install-API.ps1',
      'Start-API.ps1',
      'Test-API.ps1',
      'Deploy-API.ps1'
    ],
    config: {
      port: 3000,
      database: 'mongodb',
      auth: 'jwt',
      cors: true
    }
  }
};

// ==================== SCRIPT TEMPLATES ====================

const SCRIPT_TEMPLATES = {
  
  // SOFS Installation Script
  SOFS_INSTALL: `
# Scale-Out File Server Installation Script
param(
    [Parameter(Mandatory=$true)]
    [string]$ClusterName,
    
    [Parameter(Mandatory=$true)]
    [string[]]$Nodes,
    
    [Parameter(Mandatory=$true)]
    [string]$ClusterIP,
    
    [string]$FileShareWitness,
    
    [string]$StoragePath = "C:\\ClusterStorage"
)

Write-Host "Installing Scale-Out File Server Cluster: $ClusterName" -ForegroundColor Green

# Install required Windows features
Write-Host "Installing required features..." -ForegroundColor Yellow
Install-WindowsFeature -Name Failover-Clustering, FS-FileServer -IncludeManagementTools -Verbose

# Test cluster prerequisites
Write-Host "Testing cluster configuration..." -ForegroundColor Yellow
Test-Cluster -Node $Nodes -Include "Storage Spaces Direct", "Inventory", "Network", "System Configuration"

# Create the cluster
Write-Host "Creating cluster..." -ForegroundColor Yellow
New-Cluster -Name $ClusterName -Node $Nodes -StaticAddress $ClusterIP -NoStorage

# Configure File Share Witness (if provided)
if ($FileShareWitness) {
    Write-Host "Configuring File Share Witness..." -ForegroundColor Yellow
    Set-ClusterQuorum -FileShareWitness $FileShareWitness
}

# Enable Storage Spaces Direct (optional)
Write-Host "Enabling Storage Spaces Direct..." -ForegroundColor Yellow
Enable-ClusterStorageSpacesDirect -PoolFriendlyName "SOFSPool" -Confirm:$false

# Create Scale-Out File Server role
Write-Host "Creating SOFS role..." -ForegroundColor Yellow
Add-ClusterScaleOutFileServerRole -Name "$ClusterName-SOFS"

# Create volumes and shares
Write-Host "Creating volumes and shares..." -ForegroundColor Yellow
$shares = @("Share1", "Share2", "Share3")
foreach ($share in $shares) {
    $sharePath = "$StoragePath\\Volume1\\$share"
    New-Item -Path $sharePath -ItemType Directory -Force
    New-SmbShare -Name $share -Path $sharePath -FullAccess Everyone -ContinuouslyAvailable $true
}

Write-Host "SOFS installation completed successfully!" -ForegroundColor Green
Write-Host "Cluster Name: $ClusterName" -ForegroundColor Cyan
Write-Host "SOFS Name: $ClusterName-SOFS" -ForegroundColor Cyan
Write-Host "Shares created: $($shares -join ', ')" -ForegroundColor Cyan
`,

  // IRC Server Installation
  IRC_INSTALL: `
# InspIRCd Installation Script
param(
    [string]$ServerName = "irc.example.com",
    [int]$Port = 6667,
    [int]$SSLPort = 6697,
    [string]$AdminEmail = "admin@example.com",
    [string]$InstallPath = "C:\\InspIRCd"
)

Write-Host "Installing InspIRCd Server: $ServerName" -ForegroundColor Green

# Create installation directory
New-Item -Path $InstallPath -ItemType Directory -Force

# Download InspIRCd (Windows build)
Write-Host "Downloading InspIRCd..." -ForegroundColor Yellow
$downloadUrl = "https://github.com/inspircd/inspircd/releases/latest/download/inspircd-windows.zip"
$zipPath = "$env:TEMP\\inspircd.zip"
Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath

# Extract
Expand-Archive -Path $zipPath -DestinationPath $InstallPath -Force

# Generate configuration
Write-Host "Generating configuration..." -ForegroundColor Yellow
$config = @"
<config format="xml">
<server name="$ServerName" description="InspIRCd Server" network="MyNetwork">
<admin name="Admin" nick="Admin" email="$AdminEmail">
<bind address="" port="$Port" type="clients">
<bind address="" port="$SSLPort" type="clients" ssl="openssl">
<connect allow="*" timeout="60" pingfreq="120">
<log method="file" type="*" level="default" target="logs/ircd.log">
<module name="spanningtree">
<module name="ssl_openssl">
<module name="channels">
<module name="oper">
"@

Set-Content -Path "$InstallPath\\inspircd.conf" -Value $config

# Create startup script
$startScript = @"
@echo off
cd /d "$InstallPath"
inspircd.exe --nofork
"@
Set-Content -Path "$InstallPath\\start.bat" -Value $startScript

Write-Host "InspIRCd installed successfully!" -ForegroundColor Green
Write-Host "Server: $ServerName" -ForegroundColor Cyan
Write-Host "Port: $Port" -ForegroundColor Cyan
Write-Host "SSL Port: $SSLPort" -ForegroundColor Cyan
Write-Host "Start: $InstallPath\\start.bat" -ForegroundColor Cyan
`,

  // Web App Deployment
  WEBAPP_DEPLOY: `
# Web Application Deployment Script
param(
    [Parameter(Mandatory=$true)]
    [string]$SourcePath,
    
    [Parameter(Mandatory=$true)]
    [string]$TargetPath,
    
    [ValidateSet('IIS', 'Apache', 'XAMPP', 'NodeJS')]
    [string]$ServerType = 'IIS',
    
    [string]$SiteName = "MyWebApp",
    
    [int]$Port = 80,
    
    [switch]$InstallDependencies
)

Write-Host "Deploying Web Application: $SiteName" -ForegroundColor Green

# Create target directory
Write-Host "Creating target directory..." -ForegroundColor Yellow
New-Item -Path $TargetPath -ItemType Directory -Force

# Copy files
Write-Host "Copying files..." -ForegroundColor Yellow
Copy-Item -Path "$SourcePath\\*" -Destination $TargetPath -Recurse -Force

# Install dependencies if requested
if ($InstallDependencies -and (Test-Path "$TargetPath\\package.json")) {
    Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
    Push-Location $TargetPath
    npm install
    Pop-Location
}

# Configure web server
Write-Host "Configuring $ServerType..." -ForegroundColor Yellow
switch ($ServerType) {
    'IIS' {
        Import-Module WebAdministration
        
        # Ensure IIS is installed
        $iisFeature = Get-WindowsFeature -Name Web-Server
        if (-not $iisFeature.Installed) {
            Write-Host "Installing IIS..." -ForegroundColor Yellow
            Install-WindowsFeature -Name Web-Server -IncludeManagementTools
        }
        
        # Create website
        New-WebSite -Name $SiteName -Port $Port -PhysicalPath $TargetPath -Force
        Start-Website -Name $SiteName
        
        Write-Host "Website created in IIS: $SiteName" -ForegroundColor Cyan
    }
    
    'NodeJS' {
        # Create PM2 ecosystem file
        $ecosystem = @{
            apps = @(
                @{
                    name = $SiteName
                    script = "server.js"
                    cwd = $TargetPath
                    instances = 1
                    autorestart = $true
                    watch = $false
                    env = @{
                        NODE_ENV = "production"
                        PORT = $Port
                    }
                }
            )
        } | ConvertTo-Json -Depth 10
        
        Set-Content -Path "$TargetPath\\ecosystem.config.json" -Value $ecosystem
        
        # Start with PM2
        pm2 start "$TargetPath\\ecosystem.config.json"
        pm2 save
        
        Write-Host "Node.js app started with PM2: $SiteName" -ForegroundColor Cyan
    }
    
    'Apache' {
        # Ensure Apache is installed
        if (-not (Get-Service -Name 'Apache2.4' -ErrorAction SilentlyContinue)) {
            Write-Host "Installing Apache via Chocolatey..." -ForegroundColor Yellow
            choco install apache-httpd -y
        }
        
        # Create virtual host config
        $vhostConfig = @"
<VirtualHost *:$Port>
    ServerName $SiteName
    DocumentRoot "$TargetPath"
    <Directory "$TargetPath">
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
"@
        $apacheConf = "C:\\Apache24\\conf\\extra\\httpd-vhosts.conf"
        Add-Content -Path $apacheConf -Value $vhostConfig
        
        Restart-Service -Name 'Apache2.4'
        
        Write-Host "Virtual host created in Apache: $SiteName" -ForegroundColor Cyan
    }
    
    'XAMPP' {
        if (-not (Test-Path "C:\\xampp")) {
            Write-Host "Installing XAMPP via Chocolatey..." -ForegroundColor Yellow
            choco install xampp-81 -y
        }
        
        # Copy to htdocs
        $htdocsPath = "C:\\xampp\\htdocs\\$SiteName"
        Copy-Item -Path "$TargetPath\\*" -Destination $htdocsPath -Recurse -Force
        
        Write-Host "Files copied to XAMPP htdocs: $htdocsPath" -ForegroundColor Cyan
    }
}

Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "Application: $SiteName" -ForegroundColor Cyan
Write-Host "Path: $TargetPath" -ForegroundColor Cyan
Write-Host "Server: $ServerType" -ForegroundColor Cyan
Write-Host "Port: $Port" -ForegroundColor Cyan
`
};

// ==================== CONFIGURATION TEMPLATES ====================

const CONFIG_TEMPLATES = {
  
  // InspIRCd Configuration
  INSPIRCD_CONF: (config) => `
<config format="xml">
  <server name="${config.serverName}" description="${config.description}" network="${config.network}">
  <admin name="${config.adminName}" nick="${config.adminNick}" email="${config.adminEmail}">
  
  <bind address="" port="${config.port}" type="clients">
  ${config.sslEnabled ? `<bind address="" port="${config.sslPort}" type="clients" ssl="openssl">` : ''}
  
  <connect allow="*" timeout="60" pingfreq="120" recvq="8192" sendq="8192" threshold="10" commandrate="1000">
  
  <power diepass="${config.diePassword}" restartpass="${config.restartPassword}">
  
  ${config.channels.map(ch => `<channel name="${ch}" modes="+nt">`).join('\\n')}
  
  <log method="file" type="*" level="default" target="logs/ircd.log">
  
  <module name="spanningtree">
  <module name="channels">
  <module name="oper">
  ${config.sslEnabled ? '<module name="ssl_openssl">' : ''}
</config>
  `,

  // Shoutcast Configuration
  SHOUTCAST_CONF: (config) => `
; Shoutcast Server Configuration
MaxUser=${config.maxUsers}
Password=${config.password}
PortBase=${config.port}
LogFile=logs/sc_serv.log
RealTime=1
ScreenLog=1
ShowLastSongs=10
TchLog=logs/TS_Content.log
W3CLog=logs/sc_w3c.log
Hostname=${config.hostname}
PublicServer=Never
AllowRelay=1
AllowMaxBitrate=${config.maxBitrate}
  `,

  // Package.json for Node.js modules
  PACKAGE_JSON: (config) => ({
    name: config.name,
    version: '1.0.0',
    description: config.description,
    main: 'server.js',
    scripts: {
      start: 'node server.js',
      dev: 'nodemon server.js',
      test: 'jest'
    },
    dependencies: {
      express: '^4.18.2',
      ...config.dependencies
    },
    devDependencies: {
      nodemon: '^3.0.2',
      jest: '^29.0.0'
    }
  })
};

// ==================== EXPORT ====================

module.exports = {
  MODULE_TEMPLATES,
  SCRIPT_TEMPLATES,
  CONFIG_TEMPLATES
};