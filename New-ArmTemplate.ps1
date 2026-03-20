<#
.SYNOPSIS
    MasterChief ARM Template Creator – Interactive PowerShell Wizard
.DESCRIPTION
    Generates Azure Resource Manager (ARM) JSON templates via an interactive
    menu-driven wizard.  Covers all major Azure resource categories.
.NOTES
    Author : MasterChief Team
    Version: 1.0.0
    Date   : 2026-03-20
.EXAMPLE
    .\New-ArmTemplate.ps1
    .\New-ArmTemplate.ps1 -OutputPath "C:\templates\my-deployment.json"
#>
[CmdletBinding()]
param(
    [string]$OutputPath = ".\arm_template.json"
)

# ── Colour helpers ───────────────────────────────────────────────────
function Write-Header  { param([string]$Text) Write-Host "`n  $Text" -ForegroundColor Green }
function Write-Prompt  { param([string]$Text) Write-Host "  $Text" -ForegroundColor Cyan -NoNewline }
function Write-Info    { param([string]$Text) Write-Host "  $Text" -ForegroundColor DarkGray }
function Write-Success { param([string]$Text) Write-Host "  ✓ $Text" -ForegroundColor Green }
function Write-Err     { param([string]$Text) Write-Host "  ✗ $Text" -ForegroundColor Red }

# ── Global ARM template scaffold ────────────────────────────────────
$script:ArmTemplate = [ordered]@{
    '$schema'      = 'https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#'
    contentVersion = '1.0.0.0'
    parameters     = [ordered]@{}
    variables      = [ordered]@{}
    resources      = @()
    outputs        = [ordered]@{}
}

# ── Azure resource catalog ──────────────────────────────────────────
# Each entry:  DisplayName, ARM type, apiVersion, required-properties builder
$script:ResourceCatalog = @{
    # ── Compute ──────────────────────────────────────────────────────
    'Virtual Machine'              = @{ type = 'Microsoft.Compute/virtualMachines';              api = '2024-03-01'; category = 'Compute' }
    'VM Scale Set'                 = @{ type = 'Microsoft.Compute/virtualMachineScaleSets';      api = '2024-03-01'; category = 'Compute' }
    'Availability Set'             = @{ type = 'Microsoft.Compute/availabilitySets';             api = '2024-03-01'; category = 'Compute' }
    'Disk'                         = @{ type = 'Microsoft.Compute/disks';                       api = '2024-03-01'; category = 'Compute' }
    'Image'                        = @{ type = 'Microsoft.Compute/images';                      api = '2024-03-01'; category = 'Compute' }
    'Proximity Placement Group'    = @{ type = 'Microsoft.Compute/proximityPlacementGroups';    api = '2024-03-01'; category = 'Compute' }

    # ── Networking ───────────────────────────────────────────────────
    'Virtual Network'              = @{ type = 'Microsoft.Network/virtualNetworks';              api = '2023-11-01'; category = 'Networking' }
    'Subnet'                       = @{ type = 'Microsoft.Network/virtualNetworks/subnets';     api = '2023-11-01'; category = 'Networking' }
    'Network Security Group'       = @{ type = 'Microsoft.Network/networkSecurityGroups';       api = '2023-11-01'; category = 'Networking' }
    'Public IP Address'            = @{ type = 'Microsoft.Network/publicIPAddresses';           api = '2023-11-01'; category = 'Networking' }
    'Load Balancer'                = @{ type = 'Microsoft.Network/loadBalancers';               api = '2023-11-01'; category = 'Networking' }
    'Application Gateway'          = @{ type = 'Microsoft.Network/applicationGateways';         api = '2023-11-01'; category = 'Networking' }
    'VPN Gateway'                  = @{ type = 'Microsoft.Network/vpnGateways';                 api = '2023-11-01'; category = 'Networking' }
    'ExpressRoute Circuit'         = @{ type = 'Microsoft.Network/expressRouteCircuits';        api = '2023-11-01'; category = 'Networking' }
    'Azure Firewall'               = @{ type = 'Microsoft.Network/azureFirewalls';              api = '2023-11-01'; category = 'Networking' }
    'Front Door'                   = @{ type = 'Microsoft.Network/frontDoors';                  api = '2021-06-01'; category = 'Networking' }
    'Traffic Manager Profile'      = @{ type = 'Microsoft.Network/trafficManagerProfiles';      api = '2022-04-01'; category = 'Networking' }
    'Private Endpoint'             = @{ type = 'Microsoft.Network/privateEndpoints';            api = '2023-11-01'; category = 'Networking' }
    'Private DNS Zone'             = @{ type = 'Microsoft.Network/privateDnsZones';             api = '2020-06-01'; category = 'Networking' }
    'DNS Zone'                     = @{ type = 'Microsoft.Network/dnsZones';                    api = '2023-07-01-preview'; category = 'Networking' }
    'NAT Gateway'                  = @{ type = 'Microsoft.Network/natGateways';                 api = '2023-11-01'; category = 'Networking' }
    'Network Interface'            = @{ type = 'Microsoft.Network/networkInterfaces';           api = '2023-11-01'; category = 'Networking' }
    'Route Table'                  = @{ type = 'Microsoft.Network/routeTables';                 api = '2023-11-01'; category = 'Networking' }
    'Bastion Host'                 = @{ type = 'Microsoft.Network/bastionHosts';                api = '2023-11-01'; category = 'Networking' }
    'DDoS Protection Plan'         = @{ type = 'Microsoft.Network/ddosProtectionPlans';         api = '2023-11-01'; category = 'Networking' }
    'Virtual WAN'                  = @{ type = 'Microsoft.Network/virtualWans';                 api = '2023-11-01'; category = 'Networking' }
    'Web Application Firewall'     = @{ type = 'Microsoft.Network/ApplicationGatewayWebApplicationFirewallPolicies'; api = '2023-11-01'; category = 'Networking' }

    # ── Storage ──────────────────────────────────────────────────────
    'Storage Account'              = @{ type = 'Microsoft.Storage/storageAccounts';             api = '2023-05-01'; category = 'Storage' }
    'Blob Container'               = @{ type = 'Microsoft.Storage/storageAccounts/blobServices/containers'; api = '2023-05-01'; category = 'Storage' }
    'File Share'                   = @{ type = 'Microsoft.Storage/storageAccounts/fileServices/shares'; api = '2023-05-01'; category = 'Storage' }
    'NetApp Account'               = @{ type = 'Microsoft.NetApp/netAppAccounts';               api = '2023-11-01'; category = 'Storage' }
    'Data Lake Store'              = @{ type = 'Microsoft.DataLakeStore/accounts';               api = '2016-11-01'; category = 'Storage' }

    # ── Databases ────────────────────────────────────────────────────
    'SQL Server'                   = @{ type = 'Microsoft.Sql/servers';                         api = '2023-08-01-preview'; category = 'Databases' }
    'SQL Database'                 = @{ type = 'Microsoft.Sql/servers/databases';               api = '2023-08-01-preview'; category = 'Databases' }
    'SQL Elastic Pool'             = @{ type = 'Microsoft.Sql/servers/elasticPools';            api = '2023-08-01-preview'; category = 'Databases' }
    'Cosmos DB Account'            = @{ type = 'Microsoft.DocumentDB/databaseAccounts';         api = '2024-02-15-preview'; category = 'Databases' }
    'MySQL Flexible Server'        = @{ type = 'Microsoft.DBforMySQL/flexibleServers';          api = '2023-12-30'; category = 'Databases' }
    'PostgreSQL Flexible Server'   = @{ type = 'Microsoft.DBforPostgreSQL/flexibleServers';     api = '2023-12-01-preview'; category = 'Databases' }
    'Redis Cache'                  = @{ type = 'Microsoft.Cache/redis';                         api = '2024-03-01'; category = 'Databases' }
    'MariaDB Server'               = @{ type = 'Microsoft.DBforMariaDB/servers';                api = '2018-06-01'; category = 'Databases' }

    # ── Web & App Services ───────────────────────────────────────────
    'App Service Plan'             = @{ type = 'Microsoft.Web/serverfarms';                     api = '2023-12-01'; category = 'Web' }
    'Web App'                      = @{ type = 'Microsoft.Web/sites';                           api = '2023-12-01'; category = 'Web' }
    'Function App'                 = @{ type = 'Microsoft.Web/sites';                           api = '2023-12-01'; category = 'Web' }
    'Static Web App'               = @{ type = 'Microsoft.Web/staticSites';                     api = '2023-12-01'; category = 'Web' }
    'API Management'               = @{ type = 'Microsoft.ApiManagement/service';               api = '2023-09-01-preview'; category = 'Web' }

    # ── Containers ───────────────────────────────────────────────────
    'AKS Cluster'                  = @{ type = 'Microsoft.ContainerService/managedClusters';    api = '2024-02-01'; category = 'Containers' }
    'Container Registry'           = @{ type = 'Microsoft.ContainerRegistry/registries';        api = '2023-11-01-preview'; category = 'Containers' }
    'Container Instance'           = @{ type = 'Microsoft.ContainerInstance/containerGroups';   api = '2023-05-01'; category = 'Containers' }
    'Container App'                = @{ type = 'Microsoft.App/containerApps';                   api = '2024-03-01'; category = 'Containers' }
    'Container App Environment'    = @{ type = 'Microsoft.App/managedEnvironments';             api = '2024-03-01'; category = 'Containers' }

    # ── Identity & Security ──────────────────────────────────────────
    'Key Vault'                    = @{ type = 'Microsoft.KeyVault/vaults';                     api = '2023-07-01'; category = 'Security' }
    'Managed Identity'             = @{ type = 'Microsoft.ManagedIdentity/userAssignedIdentities'; api = '2023-01-31'; category = 'Security' }
    'Role Assignment'              = @{ type = 'Microsoft.Authorization/roleAssignments';       api = '2022-04-01'; category = 'Security' }
    'Policy Assignment'            = @{ type = 'Microsoft.Authorization/policyAssignments';     api = '2023-04-01'; category = 'Security' }
    'Policy Definition'            = @{ type = 'Microsoft.Authorization/policyDefinitions';     api = '2023-04-01'; category = 'Security' }

    # ── Monitoring & Management ──────────────────────────────────────
    'Log Analytics Workspace'      = @{ type = 'Microsoft.OperationalInsights/workspaces';      api = '2023-09-01'; category = 'Monitoring' }
    'Application Insights'         = @{ type = 'Microsoft.Insights/components';                 api = '2020-02-02'; category = 'Monitoring' }
    'Action Group'                 = @{ type = 'Microsoft.Insights/actionGroups';               api = '2023-09-01-preview'; category = 'Monitoring' }
    'Metric Alert'                 = @{ type = 'Microsoft.Insights/metricAlerts';               api = '2018-03-01'; category = 'Monitoring' }
    'Diagnostic Setting'           = @{ type = 'Microsoft.Insights/diagnosticSettings';         api = '2021-05-01-preview'; category = 'Monitoring' }
    'Automation Account'           = @{ type = 'Microsoft.Automation/automationAccounts';       api = '2023-11-01'; category = 'Monitoring' }

    # ── Analytics & Big Data ─────────────────────────────────────────
    'Synapse Workspace'            = @{ type = 'Microsoft.Synapse/workspaces';                  api = '2021-06-01'; category = 'Analytics' }
    'Data Factory'                 = @{ type = 'Microsoft.DataFactory/factories';               api = '2018-06-01'; category = 'Analytics' }
    'Databricks Workspace'         = @{ type = 'Microsoft.Databricks/workspaces';               api = '2024-05-01'; category = 'Analytics' }
    'HDInsight Cluster'            = @{ type = 'Microsoft.HDInsight/clusters';                  api = '2023-08-15-preview'; category = 'Analytics' }
    'Event Hub Namespace'          = @{ type = 'Microsoft.EventHub/namespaces';                 api = '2024-01-01'; category = 'Analytics' }
    'Stream Analytics Job'         = @{ type = 'Microsoft.StreamAnalytics/streamingJobs';       api = '2021-10-01-preview'; category = 'Analytics' }

    # ── AI & Machine Learning ────────────────────────────────────────
    'Cognitive Services Account'   = @{ type = 'Microsoft.CognitiveServices/accounts';          api = '2024-04-01-preview'; category = 'AI' }
    'Machine Learning Workspace'   = @{ type = 'Microsoft.MachineLearningServices/workspaces';  api = '2024-04-01'; category = 'AI' }
    'Search Service'               = @{ type = 'Microsoft.Search/searchServices';               api = '2024-03-01-preview'; category = 'AI' }
    'OpenAI Service'               = @{ type = 'Microsoft.CognitiveServices/accounts';          api = '2024-04-01-preview'; category = 'AI' }
    'Bot Service'                  = @{ type = 'Microsoft.BotService/botServices';              api = '2022-09-15'; category = 'AI' }

    # ── Integration ──────────────────────────────────────────────────
    'Service Bus Namespace'        = @{ type = 'Microsoft.ServiceBus/namespaces';               api = '2022-10-01-preview'; category = 'Integration' }
    'Logic App'                    = @{ type = 'Microsoft.Logic/workflows';                     api = '2019-05-01'; category = 'Integration' }
    'Event Grid Topic'             = @{ type = 'Microsoft.EventGrid/topics';                    api = '2024-06-01-preview'; category = 'Integration' }
    'Event Grid Subscription'      = @{ type = 'Microsoft.EventGrid/eventSubscriptions';        api = '2024-06-01-preview'; category = 'Integration' }
    'Notification Hub'             = @{ type = 'Microsoft.NotificationHubs/namespaces/notificationHubs'; api = '2023-10-01-preview'; category = 'Integration' }
    'SignalR Service'              = @{ type = 'Microsoft.SignalRService/signalR';               api = '2024-03-01'; category = 'Integration' }

    # ── IoT ──────────────────────────────────────────────────────────
    'IoT Hub'                      = @{ type = 'Microsoft.Devices/IotHubs';                     api = '2023-06-30'; category = 'IoT' }
    'IoT Central App'              = @{ type = 'Microsoft.IoTCentral/IoTApps';                  api = '2021-06-01'; category = 'IoT' }
    'Digital Twins'                = @{ type = 'Microsoft.DigitalTwins/digitalTwinsInstances';  api = '2023-01-31'; category = 'IoT' }
    'Device Provisioning Service'  = @{ type = 'Microsoft.Devices/provisioningServices';        api = '2022-12-12'; category = 'IoT' }

    # ── DevOps ───────────────────────────────────────────────────────
    'DevTest Lab'                  = @{ type = 'Microsoft.DevTestLab/labs';                     api = '2018-09-15'; category = 'DevOps' }
    'Deployment Script'            = @{ type = 'Microsoft.Resources/deploymentScripts';         api = '2023-08-01'; category = 'DevOps' }

    # ── Governance ───────────────────────────────────────────────────
    'Resource Group'               = @{ type = 'Microsoft.Resources/resourceGroups';            api = '2024-03-01'; category = 'Governance' }
    'Management Group'             = @{ type = 'Microsoft.Management/managementGroups';         api = '2023-04-01'; category = 'Governance' }
    'Lock'                         = @{ type = 'Microsoft.Authorization/locks';                 api = '2020-05-01'; category = 'Governance' }
    'Budget'                       = @{ type = 'Microsoft.Consumption/budgets';                 api = '2023-11-01'; category = 'Governance' }
    'Blueprint'                    = @{ type = 'Microsoft.Blueprint/blueprints';                api = '2018-11-01-preview'; category = 'Governance' }
    'Subscription'                 = @{ type = 'Microsoft.Subscription/aliases';                api = '2021-10-01'; category = 'Governance' }
}

# ── Azure locations ─────────────────────────────────────────────────
$script:AzureLocations = @(
    'eastus', 'eastus2', 'westus', 'westus2', 'westus3',
    'centralus', 'northcentralus', 'southcentralus', 'westcentralus',
    'northeurope', 'westeurope', 'uksouth', 'ukwest',
    'francecentral', 'germanywestcentral', 'switzerlandnorth', 'norwayeast',
    'swedencentral', 'polandcentral', 'italynorth', 'spaincentral',
    'southeastasia', 'eastasia', 'japaneast', 'japanwest',
    'koreacentral', 'koreasouth',
    'australiaeast', 'australiasoutheast', 'australiacentral',
    'canadacentral', 'canadaeast',
    'brazilsouth', 'southafricanorth', 'uaenorth',
    'centralindia', 'southindia', 'westindia',
    'qatarcentral', 'israelcentral', 'mexicocentral'
)

$script:VMSizes = @(
    'Standard_B1s', 'Standard_B2s', 'Standard_B2ms', 'Standard_B4ms',
    'Standard_D2s_v5', 'Standard_D4s_v5', 'Standard_D8s_v5', 'Standard_D16s_v5',
    'Standard_E2s_v5', 'Standard_E4s_v5', 'Standard_E8s_v5',
    'Standard_F2s_v2', 'Standard_F4s_v2', 'Standard_F8s_v2',
    'Standard_DS1_v2', 'Standard_DS2_v2', 'Standard_DS3_v2'
)

$script:StorageSKUs = @('Standard_LRS', 'Standard_GRS', 'Standard_ZRS', 'Standard_RAGRS', 'Premium_LRS', 'Premium_ZRS')
$script:AppServiceSKUs = @('F1', 'D1', 'B1', 'B2', 'B3', 'S1', 'S2', 'S3', 'P1v3', 'P2v3', 'P3v3')

# ═════════════════════════════════════════════════════════════════════
# MENU HELPERS
# ═════════════════════════════════════════════════════════════════════
function Show-Menu {
    param(
        [string]$Title,
        [string[]]$Options,
        [switch]$AllowMultiple,
        [switch]$AllowBack
    )
    Write-Header $Title
    for ($i = 0; $i -lt $Options.Count; $i++) {
        $num = $i + 1
        Write-Host "    [$num] $($Options[$i])" -ForegroundColor Yellow
    }
    if ($AllowBack) { Write-Host "    [B] Back" -ForegroundColor DarkGray }
    Write-Host "    [Q] Quit" -ForegroundColor DarkGray
    Write-Host ""

    if ($AllowMultiple) {
        Write-Prompt "Select (comma-separated, e.g. 1,3,5): "
        $raw = Read-Host
        if ($raw -match '^[Qq]$') { return $null }
        if ($raw -match '^[Bb]$' -and $AllowBack) { return 'BACK' }
        $indices = $raw -split ',' | ForEach-Object { ($_.Trim()) -as [int] } | Where-Object { $_ -ge 1 -and $_ -le $Options.Count }
        return $indices | ForEach-Object { $Options[$_ - 1] }
    }
    else {
        Write-Prompt "Select [1-$($Options.Count)]: "
        $raw = Read-Host
        if ($raw -match '^[Qq]$') { return $null }
        if ($raw -match '^[Bb]$' -and $AllowBack) { return 'BACK' }
        $idx = ($raw -as [int])
        if ($idx -ge 1 -and $idx -le $Options.Count) { return $Options[$idx - 1] }
        Write-Err "Invalid selection"; return Show-Menu -Title $Title -Options $Options -AllowMultiple:$AllowMultiple -AllowBack:$AllowBack
    }
}

function Read-Value {
    param([string]$Label, [string]$Default, [switch]$Required)
    if ($Default) {
        Write-Prompt "$Label [$Default]: "
    } else {
        Write-Prompt "${Label}: "
    }
    $val = Read-Host
    if ([string]::IsNullOrWhiteSpace($val)) { $val = $Default }
    if ($Required -and [string]::IsNullOrWhiteSpace($val)) {
        Write-Err "Value required"
        return Read-Value -Label $Label -Default $Default -Required
    }
    return $val
}

function Read-YesNo {
    param([string]$Label, [bool]$Default = $false)
    $hint = if ($Default) { 'Y/n' } else { 'y/N' }
    Write-Prompt "$Label [$hint]: "
    $raw = Read-Host
    if ([string]::IsNullOrWhiteSpace($raw)) { return $Default }
    return $raw -match '^[Yy]'
}

# ═════════════════════════════════════════════════════════════════════
# PARAMETER BUILDER
# ═════════════════════════════════════════════════════════════════════
function Add-TemplateParameter {
    param([string]$Name, [string]$Type = 'string', $DefaultValue, [string]$Description, [string[]]$AllowedValues)
    $p = [ordered]@{ type = $Type }
    if ($DefaultValue -ne $null)       { $p.defaultValue  = $DefaultValue }
    if ($Description)                  { $p.metadata      = @{ description = $Description } }
    if ($AllowedValues.Count -gt 0)    { $p.allowedValues = $AllowedValues }
    $script:ArmTemplate.parameters[$Name] = $p
}

# ═════════════════════════════════════════════════════════════════════
# RESOURCE-SPECIFIC WIZARDS
# ═════════════════════════════════════════════════════════════════════
function New-VMResource {
    Write-Header "Virtual Machine Configuration"
    $name     = Read-Value 'VM Name'            -Default 'myVM'     -Required
    $location = Show-Menu  'Azure Location'     -Options $script:AzureLocations
    if (-not $location) { return $null }
    $size     = Show-Menu  'VM Size'            -Options $script:VMSizes
    $osType   = Show-Menu  'OS Type'            -Options @('Windows','Linux')
    $adminUser = Read-Value 'Admin Username'    -Default 'azureadmin' -Required

    if ($osType -eq 'Windows') {
        $publisher = 'MicrosoftWindowsServer'; $offer = 'WindowsServer'; $sku = '2022-datacenter-g2'
    } else {
        $publisher = 'Canonical'; $offer = '0001-com-ubuntu-server-jammy'; $sku = '22_04-lts-gen2'
    }

    # Add parameters
    Add-TemplateParameter -Name 'adminPassword' -Type 'securestring' -Description "Admin password for $name"

    $enableBD = Read-YesNo 'Enable Boot Diagnostics?'
    $enableMI = Read-YesNo 'Enable Managed Identity?'

    $resource = [ordered]@{
        type       = 'Microsoft.Compute/virtualMachines'
        apiVersion = '2024-03-01'
        name       = $name
        location   = $location
        properties = [ordered]@{
            hardwareProfile = @{ vmSize = $size }
            storageProfile  = [ordered]@{
                imageReference = [ordered]@{ publisher = $publisher; offer = $offer; sku = $sku; version = 'latest' }
                osDisk         = [ordered]@{ createOption = 'FromImage'; managedDisk = @{ storageAccountType = 'Premium_LRS' } }
            }
            osProfile = [ordered]@{
                computerName  = $name
                adminUsername = $adminUser
                adminPassword = "[parameters('adminPassword')]"
            }
            networkProfile = @{ networkInterfaces = @(@{ id = "[resourceId('Microsoft.Network/networkInterfaces','${name}-nic')]" }) }
        }
    }
    if ($enableBD) { $resource.properties.diagnosticsProfile = @{ bootDiagnostics = @{ enabled = $true } } }
    if ($enableMI) { $resource['identity'] = @{ type = 'SystemAssigned' } }

    return $resource
}

function New-VNetResource {
    Write-Header "Virtual Network Configuration"
    $name     = Read-Value 'VNet Name'      -Default 'myVNet'       -Required
    $location = Show-Menu  'Azure Location' -Options $script:AzureLocations
    if (-not $location) { return $null }
    $cidr     = Read-Value 'Address Space'  -Default '10.0.0.0/16'  -Required

    $subnets = @()
    $addSub = $true
    while ($addSub) {
        $sName = Read-Value 'Subnet Name'    -Default "subnet$($subnets.Count + 1)"
        $sCidr = Read-Value 'Subnet CIDR'    -Default "10.0.$($subnets.Count).0/24"
        $subnets += @{ name = $sName; properties = @{ addressPrefix = $sCidr } }
        $addSub = Read-YesNo 'Add another subnet?'
    }

    $enableDDoS = Read-YesNo 'Enable DDoS Protection?'

    return [ordered]@{
        type       = 'Microsoft.Network/virtualNetworks'
        apiVersion = '2023-11-01'
        name       = $name
        location   = $location
        properties = [ordered]@{
            addressSpace      = @{ addressPrefixes = @($cidr) }
            subnets           = $subnets
            enableDdosProtection = $enableDDoS
        }
    }
}

function New-NSGResource {
    Write-Header "Network Security Group Configuration"
    $name     = Read-Value 'NSG Name'       -Default 'myNSG'        -Required
    $location = Show-Menu  'Azure Location' -Options $script:AzureLocations
    if (-not $location) { return $null }

    $rules  = @()
    $addRule = Read-YesNo 'Add security rule?' -Default $true
    $priority = 100
    while ($addRule) {
        $rName  = Read-Value 'Rule Name'       -Default "rule$($rules.Count + 1)"
        $dir    = Show-Menu  'Direction'       -Options @('Inbound','Outbound')
        $access = Show-Menu  'Access'          -Options @('Allow','Deny')
        $proto  = Show-Menu  'Protocol'        -Options @('Tcp','Udp','Icmp','*')
        $srcPort = Read-Value 'Source Port Range'      -Default '*'
        $dstPort = Read-Value 'Destination Port Range' -Default '443'
        $srcAddr = Read-Value 'Source Address Prefix'   -Default '*'
        $dstAddr = Read-Value 'Dest Address Prefix'     -Default '*'

        $rules += @{
            name = $rName
            properties = [ordered]@{
                priority                 = $priority
                direction                = $dir
                access                   = $access
                protocol                 = $proto
                sourcePortRange          = $srcPort
                destinationPortRange     = $dstPort
                sourceAddressPrefix      = $srcAddr
                destinationAddressPrefix = $dstAddr
            }
        }
        $priority += 10
        $addRule = Read-YesNo 'Add another rule?'
    }

    return [ordered]@{
        type       = 'Microsoft.Network/networkSecurityGroups'
        apiVersion = '2023-11-01'
        name       = $name
        location   = $location
        properties = @{ securityRules = $rules }
    }
}

function New-StorageResource {
    Write-Header "Storage Account Configuration"
    $name     = Read-Value 'Storage Account Name (3-24 lowercase alphanum)' -Default 'mystorageacct' -Required
    $location = Show-Menu  'Azure Location' -Options $script:AzureLocations
    if (-not $location) { return $null }
    $sku      = Show-Menu  'SKU'            -Options $script:StorageSKUs
    $kind     = Show-Menu  'Account Kind'   -Options @('StorageV2','BlobStorage','BlockBlobStorage','FileStorage')
    $tls      = Show-Menu  'Min TLS Version'-Options @('TLS1_2','TLS1_0','TLS1_1')
    $https    = Read-YesNo 'Require HTTPS?' -Default $true
    $hns      = Read-YesNo 'Enable Hierarchical Namespace (Data Lake)?' -Default $false
    $blob     = Read-YesNo 'Enable Blob Public Access?' -Default $false

    return [ordered]@{
        type       = 'Microsoft.Storage/storageAccounts'
        apiVersion = '2023-05-01'
        name       = $name
        location   = $location
        sku        = @{ name = $sku }
        kind       = $kind
        properties = [ordered]@{
            supportsHttpsTrafficOnly  = $https
            minimumTlsVersion         = $tls
            isHnsEnabled              = $hns
            allowBlobPublicAccess     = $blob
        }
    }
}

function New-KeyVaultResource {
    Write-Header "Key Vault Configuration"
    $name     = Read-Value 'Key Vault Name' -Default 'myKeyVault' -Required
    $location = Show-Menu  'Azure Location' -Options $script:AzureLocations
    if (-not $location) { return $null }
    $skuName  = Show-Menu  'SKU'            -Options @('standard','premium')
    $enableRbac   = Read-YesNo 'Enable RBAC Authorization?' -Default $true
    $enablePurge  = Read-YesNo 'Enable Purge Protection?'   -Default $true
    $softDelete   = Read-Value 'Soft Delete Retention Days' -Default '90'
    $enableDeploy = Read-YesNo 'Enable for Deployment?'     -Default $false
    $enableDisk   = Read-YesNo 'Enable for Disk Encryption?'

    Add-TemplateParameter -Name 'tenantId' -Type 'string' -Description 'Azure AD Tenant ID'

    return [ordered]@{
        type       = 'Microsoft.KeyVault/vaults'
        apiVersion = '2023-07-01'
        name       = $name
        location   = $location
        properties = [ordered]@{
            tenantId                    = "[parameters('tenantId')]"
            sku                         = @{ family = 'A'; name = $skuName }
            enableRbacAuthorization     = $enableRbac
            enablePurgeProtection       = $enablePurge
            softDeleteRetentionInDays   = [int]$softDelete
            enabledForDeployment        = $enableDeploy
            enabledForDiskEncryption    = $enableDisk
        }
    }
}

function New-AKSResource {
    Write-Header "AKS Cluster Configuration"
    $name      = Read-Value 'Cluster Name'   -Default 'myAKS'       -Required
    $location  = Show-Menu  'Azure Location' -Options $script:AzureLocations
    if (-not $location) { return $null }
    $k8sVer    = Read-Value 'Kubernetes Version' -Default '1.29'
    $nodeCount = Read-Value 'Node Count'     -Default '3'
    $nodeSize  = Show-Menu  'Node VM Size'   -Options $script:VMSizes
    $maxPods   = Read-Value 'Max Pods per Node' -Default '110'
    $netPlugin = Show-Menu  'Network Plugin' -Options @('azure','kubenet','none')
    $enableRBAC = Read-YesNo 'Enable Kubernetes RBAC?' -Default $true
    $enableAAD  = Read-YesNo 'Enable Azure AD Integration?' -Default $false

    $resource = [ordered]@{
        type       = 'Microsoft.ContainerService/managedClusters'
        apiVersion = '2024-02-01'
        name       = $name
        location   = $location
        identity   = @{ type = 'SystemAssigned' }
        properties = [ordered]@{
            kubernetesVersion = $k8sVer
            dnsPrefix         = $name
            enableRBAC        = $enableRBAC
            agentPoolProfiles = @(
                [ordered]@{
                    name    = 'nodepool1'
                    count   = [int]$nodeCount
                    vmSize  = $nodeSize
                    maxPods = [int]$maxPods
                    mode    = 'System'
                    osType  = 'Linux'
                    type    = 'VirtualMachineScaleSets'
                }
            )
            networkProfile = @{ networkPlugin = $netPlugin; loadBalancerSku = 'standard' }
        }
    }
    if ($enableAAD) {
        $resource.properties.aadProfile = @{ managed = $true; enableAzureRBAC = $true }
    }
    return $resource
}

function New-AppServiceResource {
    Write-Header "App Service Configuration"
    $planName = Read-Value 'App Service Plan Name' -Default 'myAppPlan' -Required
    $appName  = Read-Value 'Web App Name'          -Default 'myWebApp'  -Required
    $location = Show-Menu  'Azure Location' -Options $script:AzureLocations
    if (-not $location) { return $null }
    $sku      = Show-Menu  'Plan SKU' -Options $script:AppServiceSKUs
    $os       = Show-Menu  'OS' -Options @('Linux','Windows')
    $runtime  = Show-Menu  'Runtime Stack' -Options @('DOTNETCORE|8.0','NODE|20-lts','PYTHON|3.12','JAVA|17-java17','PHP|8.3','RUBY|3.2','GO|1.22')
    $alwaysOn = Read-YesNo 'Always On?' -Default ($sku -notmatch '^[FD]')
    $httpsOnly = Read-YesNo 'HTTPS Only?' -Default $true

    $resources = @()
    # Plan
    $resources += [ordered]@{
        type       = 'Microsoft.Web/serverfarms'
        apiVersion = '2023-12-01'
        name       = $planName
        location   = $location
        kind       = if ($os -eq 'Linux') { 'linux' } else { 'app' }
        sku        = @{ name = $sku }
        properties = @{ reserved = ($os -eq 'Linux') }
    }
    # Site
    $rtParts = $runtime -split '\|',2
    $siteProps = [ordered]@{
        serverFarmId = "[resourceId('Microsoft.Web/serverfarms','$planName')]"
        httpsOnly    = $httpsOnly
        siteConfig   = [ordered]@{
            alwaysOn         = $alwaysOn
            linuxFxVersion   = if ($os -eq 'Linux') { "$($rtParts[0])|$($rtParts[1])" } else { $null }
            minTlsVersion    = '1.2'
            ftpsState        = 'Disabled'
            http20Enabled    = $true
        }
    }
    $resources += [ordered]@{
        type       = 'Microsoft.Web/sites'
        apiVersion = '2023-12-01'
        name       = $appName
        location   = $location
        dependsOn  = @("[resourceId('Microsoft.Web/serverfarms','$planName')]")
        identity   = @{ type = 'SystemAssigned' }
        properties = $siteProps
    }
    return $resources
}

function New-SQLResource {
    Write-Header "SQL Server + Database Configuration"
    $serverName = Read-Value 'SQL Server Name'   -Default 'mysqlserver' -Required
    $dbName     = Read-Value 'Database Name'     -Default 'mydb'        -Required
    $location   = Show-Menu  'Azure Location'    -Options $script:AzureLocations
    if (-not $location) { return $null }
    $adminUser  = Read-Value 'Admin Login'       -Default 'sqladmin'    -Required
    $tier       = Show-Menu  'Service Tier'      -Options @('Basic','Standard','Premium','GeneralPurpose','Hyperscale','BusinessCritical')
    $enableAD   = Read-YesNo 'Enable Azure AD Auth?' -Default $true
    $publicNet  = Read-YesNo 'Allow Public Network Access?' -Default $false

    Add-TemplateParameter -Name 'sqlAdminPassword' -Type 'securestring' -Description "SQL Admin password"

    $resources = @()
    $resources += [ordered]@{
        type       = 'Microsoft.Sql/servers'
        apiVersion = '2023-08-01-preview'
        name       = $serverName
        location   = $location
        properties = [ordered]@{
            administratorLogin         = $adminUser
            administratorLoginPassword = "[parameters('sqlAdminPassword')]"
            publicNetworkAccess        = if ($publicNet) { 'Enabled' } else { 'Disabled' }
            minimalTlsVersion          = '1.2'
        }
    }
    $resources += [ordered]@{
        type       = 'Microsoft.Sql/servers/databases'
        apiVersion = '2023-08-01-preview'
        name       = "$serverName/$dbName"
        location   = $location
        dependsOn  = @("[resourceId('Microsoft.Sql/servers','$serverName')]")
        sku        = @{ name = $tier; tier = $tier }
        properties = @{}
    }
    return $resources
}

function New-CosmosDBResource {
    Write-Header "Cosmos DB Configuration"
    $name     = Read-Value 'Account Name'   -Default 'mycosmosdb' -Required
    $location = Show-Menu  'Azure Location' -Options $script:AzureLocations
    if (-not $location) { return $null }
    $apiType  = Show-Menu  'API Type' -Options @('SQL (Core)','MongoDB','Cassandra','Gremlin','Table')
    $capacity = Show-Menu  'Capacity Mode' -Options @('Provisioned','Serverless')
    $multiWrite = Read-YesNo 'Enable Multi-Region Writes?' -Default $false
    $freeTier   = Read-YesNo 'Apply Free Tier Discount?' -Default $false

    $kind = switch ($apiType) { 'MongoDB' { 'MongoDB' } default { 'GlobalDocumentDB' } }
    $capabilities = switch ($apiType) {
        'Cassandra' { @(@{ name = 'EnableCassandra' }) }
        'Gremlin'   { @(@{ name = 'EnableGremlin' }) }
        'Table'     { @(@{ name = 'EnableTable' }) }
        default     { @() }
    }
    if ($capacity -eq 'Serverless') { $capabilities += @(@{ name = 'EnableServerless' }) }

    return [ordered]@{
        type       = 'Microsoft.DocumentDB/databaseAccounts'
        apiVersion = '2024-02-15-preview'
        name       = $name
        location   = $location
        kind       = $kind
        properties = [ordered]@{
            databaseAccountOfferType     = 'Standard'
            enableFreeTier               = $freeTier
            enableMultipleWriteLocations = $multiWrite
            capabilities                 = $capabilities
            locations                    = @(@{ locationName = $location; failoverPriority = 0 })
            consistencyPolicy            = @{ defaultConsistencyLevel = 'Session' }
        }
    }
}

function New-LogAnalyticsResource {
    Write-Header "Log Analytics Workspace Configuration"
    $name      = Read-Value 'Workspace Name' -Default 'myLogAnalytics' -Required
    $location  = Show-Menu 'Azure Location'  -Options $script:AzureLocations
    if (-not $location) { return $null }
    $sku       = Show-Menu 'SKU'             -Options @('PerGB2018','Free','Standalone','PerNode','Standard','Premium')
    $retention = Read-Value 'Retention Days'  -Default '30'

    return [ordered]@{
        type       = 'Microsoft.OperationalInsights/workspaces'
        apiVersion = '2023-09-01'
        name       = $name
        location   = $location
        properties = [ordered]@{
            sku             = @{ name = $sku }
            retentionInDays = [int]$retention
        }
    }
}

function New-ContainerRegistryResource {
    Write-Header "Container Registry Configuration"
    $name     = Read-Value 'Registry Name (alphanumeric)' -Default 'myregistry' -Required
    $location = Show-Menu 'Azure Location' -Options $script:AzureLocations
    if (-not $location) { return $null }
    $sku      = Show-Menu 'SKU' -Options @('Basic','Standard','Premium')
    $adminEnabled = Read-YesNo 'Enable Admin User?' -Default $false
    $publicNet    = Read-YesNo 'Allow Public Network Access?' -Default $true

    $resource = [ordered]@{
        type       = 'Microsoft.ContainerRegistry/registries'
        apiVersion = '2023-11-01-preview'
        name       = $name
        location   = $location
        sku        = @{ name = $sku }
        properties = [ordered]@{
            adminUserEnabled      = $adminEnabled
            publicNetworkAccess   = if ($publicNet) { 'Enabled' } else { 'Disabled' }
        }
    }
    if ($sku -eq 'Premium') {
        $zoneRedundancy = Read-YesNo 'Enable Zone Redundancy?'
        if ($zoneRedundancy) { $resource.properties.zoneRedundancy = 'Enabled' }
    }
    return $resource
}

function New-GenericResource {
    param([string]$DisplayName, [hashtable]$CatalogEntry)
    Write-Header "$DisplayName Configuration"
    $name     = Read-Value 'Resource Name' -Default ('my' + ($DisplayName -replace ' ','')) -Required
    $location = Show-Menu 'Azure Location' -Options $script:AzureLocations
    if (-not $location) { return $null }

    $tags = @{}
    if (Read-YesNo 'Add tags?') {
        $addTag = $true
        while ($addTag) {
            $tKey = Read-Value 'Tag Key' -Required
            $tVal = Read-Value 'Tag Value' -Required
            $tags[$tKey] = $tVal
            $addTag = Read-YesNo 'Add another tag?'
        }
    }

    $resource = [ordered]@{
        type       = $CatalogEntry.type
        apiVersion = $CatalogEntry.api
        name       = $name
        location   = $location
        properties = @{}
    }
    if ($tags.Count) { $resource.tags = $tags }
    return $resource
}

# ═════════════════════════════════════════════════════════════════════
# RESOURCE WIZARD DISPATCHER
# ═════════════════════════════════════════════════════════════════════
function Invoke-ResourceWizard {
    param([string]$DisplayName)
    $entry = $script:ResourceCatalog[$DisplayName]
    $result = switch ($DisplayName) {
        'Virtual Machine'         { New-VMResource }
        'Virtual Network'         { New-VNetResource }
        'Network Security Group'  { New-NSGResource }
        'Storage Account'         { New-StorageResource }
        'Key Vault'               { New-KeyVaultResource }
        'AKS Cluster'             { New-AKSResource }
        'App Service Plan'        { New-AppServiceResource }
        'Web App'                 { New-AppServiceResource }
        'Function App'            { New-AppServiceResource }
        'SQL Server'              { New-SQLResource }
        'SQL Database'            { New-SQLResource }
        'Cosmos DB Account'       { New-CosmosDBResource }
        'Log Analytics Workspace' { New-LogAnalyticsResource }
        'Container Registry'      { New-ContainerRegistryResource }
        default                   { New-GenericResource -DisplayName $DisplayName -CatalogEntry $entry }
    }
    return $result
}

# ═════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ═════════════════════════════════════════════════════════════════════
function Start-ArmWizard {
    Clear-Host
    Write-Host ""
    Write-Host "  ╔══════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "  ║   MasterChief ARM Template Creator                  ║" -ForegroundColor Green
    Write-Host "  ║   Interactive Azure Resource Manager Wizard         ║" -ForegroundColor Green
    Write-Host "  ╚══════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""

    $categories = $script:ResourceCatalog.Values | ForEach-Object { $_.category } | Sort-Object -Unique
    $continue = $true

    while ($continue) {
        Write-Header "─── Main Menu ───────────────────────────"
        Write-Host "    Resources added: $($script:ArmTemplate.resources.Count)" -ForegroundColor Magenta
        Write-Host ""

        $action = Show-Menu 'What would you like to do?' -Options @(
            'Add Resource',
            'Add Parameter',
            'Add Variable',
            'Add Output',
            'View Current Template',
            'Validate Template',
            'Save Template',
            'Exit'
        )

        switch ($action) {
            'Add Resource' {
                $cat = Show-Menu 'Select Resource Category' -Options $categories -AllowBack
                if ($cat -eq 'BACK' -or -not $cat) { continue }
                $catResources = $script:ResourceCatalog.GetEnumerator() |
                    Where-Object { $_.Value.category -eq $cat } |
                    ForEach-Object { $_.Key } | Sort-Object
                $resChoice = Show-Menu "Select $cat Resource" -Options $catResources -AllowBack
                if ($resChoice -eq 'BACK' -or -not $resChoice) { continue }
                $newRes = Invoke-ResourceWizard -DisplayName $resChoice
                if ($newRes) {
                    if ($newRes -is [System.Array]) {
                        $script:ArmTemplate.resources += $newRes
                        Write-Success "Added $($newRes.Count) resources"
                    } else {
                        $script:ArmTemplate.resources += $newRes
                        Write-Success "Added: $resChoice"
                    }
                }
            }
            'Add Parameter' {
                $pName = Read-Value 'Parameter Name' -Required
                $pType = Show-Menu 'Type' -Options @('string','securestring','int','bool','object','array')
                $pDesc = Read-Value 'Description'
                $pDef  = Read-Value 'Default Value'
                if ($pType -eq 'int' -and $pDef) { $pDef = [int]$pDef }
                if ($pType -eq 'bool' -and $pDef) { $pDef = $pDef -match '^(true|1|yes)$' }
                Add-TemplateParameter -Name $pName -Type $pType -DefaultValue $pDef -Description $pDesc
                Write-Success "Parameter '$pName' added"
            }
            'Add Variable' {
                $vName = Read-Value 'Variable Name' -Required
                $vVal  = Read-Value 'Value (expression or literal)' -Required
                $script:ArmTemplate.variables[$vName] = $vVal
                Write-Success "Variable '$vName' added"
            }
            'Add Output' {
                $oName  = Read-Value 'Output Name' -Required
                $oType  = Show-Menu 'Type' -Options @('string','int','bool','object','array')
                $oValue = Read-Value 'Value (ARM expression)' -Required
                $script:ArmTemplate.outputs[$oName] = [ordered]@{ type = $oType; value = $oValue }
                Write-Success "Output '$oName' added"
            }
            'View Current Template' {
                Write-Header "Current ARM Template Preview"
                $json = $script:ArmTemplate | ConvertTo-Json -Depth 20
                Write-Host $json -ForegroundColor Gray
                Write-Host ""
                Read-Value 'Press Enter to continue'
            }
            'Validate Template' {
                $errors = @()
                if ($script:ArmTemplate.resources.Count -eq 0) { $errors += 'No resources defined' }
                # Check for duplicate resource names
                $names = $script:ArmTemplate.resources | ForEach-Object { $_.name }
                $dupes = $names | Group-Object | Where-Object { $_.Count -gt 1 }
                if ($dupes) { $errors += "Duplicate resource names: $($dupes.Name -join ', ')" }
                # Check parameter references
                $json = $script:ArmTemplate | ConvertTo-Json -Depth 20
                $refs = [regex]::Matches($json, "parameters\('([^']+)'\)") | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
                foreach ($ref in $refs) {
                    if (-not $script:ArmTemplate.parameters.ContainsKey($ref)) { $errors += "Missing parameter: $ref" }
                }
                if ($errors.Count -eq 0) {
                    Write-Success "Template is valid ($($script:ArmTemplate.resources.Count) resources, $($script:ArmTemplate.parameters.Count) parameters)"
                } else {
                    Write-Err "Validation issues:"
                    $errors | ForEach-Object { Write-Err "  - $_" }
                }
            }
            'Save Template' {
                $path = Read-Value 'Output Path' -Default $OutputPath
                $json = $script:ArmTemplate | ConvertTo-Json -Depth 20
                $json | Out-File -FilePath $path -Encoding utf8
                Write-Success "Template saved to: $path"
                Write-Info "  Resources: $($script:ArmTemplate.resources.Count)"
                Write-Info "  Parameters: $($script:ArmTemplate.parameters.Count)"
                Write-Info "  File size: $((Get-Item $path).Length) bytes"
            }
            'Exit' { $continue = $false }
            $null  { $continue = $false }
        }
    }
    Write-Host "`n  Goodbye!`n" -ForegroundColor Green
}

# ── Entry point ─────────────────────────────────────────────────────
Start-ArmWizard
