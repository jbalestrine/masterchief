# Spoke Module Variables

variable "spoke_resource_group_name" {
  description = "Name of the spoke resource group"
  type        = string
}

variable "location" {
  description = "Azure region for resources"
  type        = string
}

variable "spoke_vnet_name" {
  description = "Name of the spoke virtual network"
  type        = string
}

variable "spoke_address_space" {
  description = "Address space for the spoke VNET"
  type        = list(string)
  default     = ["10.1.0.0/16"]
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# Hub References
variable "hub_vnet_id" {
  description = "ID of the hub virtual network"
  type        = string
}

variable "hub_resource_group_name" {
  description = "Name of the hub resource group"
  type        = string
}

variable "hub_vnet_name" {
  description = "Name of the hub virtual network"
  type        = string
}

variable "firewall_private_ip" {
  description = "Private IP of the hub firewall"
  type        = string
}

# VNET Peering Configuration
variable "use_remote_gateways" {
  description = "Use remote gateways for VNET peering"
  type        = bool
  default     = true
}

variable "allow_gateway_transit" {
  description = "Allow gateway transit for hub-to-spoke peering"
  type        = bool
  default     = true
}

# AKS Configuration
variable "enable_aks" {
  description = "Enable AKS cluster in spoke"
  type        = bool
  default     = true
}

variable "aks_cluster_name" {
  description = "Name of the AKS cluster"
  type        = string
}

variable "aks_dns_prefix" {
  description = "DNS prefix for AKS cluster"
  type        = string
}

variable "aks_kubernetes_version" {
  description = "Kubernetes version for AKS"
  type        = string
  default     = "1.27.0"
}

variable "aks_sku_tier" {
  description = "SKU tier for AKS (Free or Paid)"
  type        = string
  default     = "Free"
}

variable "aks_default_node_pool_name" {
  description = "Name of the default node pool"
  type        = string
  default     = "default"
}

variable "aks_node_count" {
  description = "Initial node count for default pool"
  type        = number
  default     = 3
}

variable "aks_vm_size" {
  description = "VM size for AKS nodes"
  type        = string
  default     = "Standard_D2_v2"
}

variable "aks_enable_auto_scaling" {
  description = "Enable auto scaling for default node pool"
  type        = bool
  default     = true
}

variable "aks_min_node_count" {
  description = "Minimum node count for auto scaling"
  type        = number
  default     = 1
}

variable "aks_max_node_count" {
  description = "Maximum node count for auto scaling"
  type        = number
  default     = 10
}

variable "aks_max_pods_per_node" {
  description = "Maximum pods per node"
  type        = number
  default     = 30
}

variable "aks_os_disk_size_gb" {
  description = "OS disk size in GB"
  type        = number
  default     = 128
}

variable "aks_os_disk_type" {
  description = "OS disk type"
  type        = string
  default     = "Managed"
}

variable "aks_node_pool_type" {
  description = "Type of node pool"
  type        = string
  default     = "VirtualMachineScaleSets"
}

variable "aks_availability_zones" {
  description = "Availability zones for nodes"
  type        = list(string)
  default     = ["1", "2", "3"]
}

variable "aks_network_plugin" {
  description = "Network plugin for AKS"
  type        = string
  default     = "azure"
}

variable "aks_network_policy" {
  description = "Network policy for AKS"
  type        = string
  default     = "azure"
}

variable "aks_load_balancer_sku" {
  description = "Load balancer SKU"
  type        = string
  default     = "standard"
}

variable "aks_outbound_type" {
  description = "Outbound type for AKS"
  type        = string
  default     = "loadBalancer"
}

variable "aks_dns_service_ip" {
  description = "DNS service IP"
  type        = string
  default     = "10.0.0.10"
}

variable "aks_docker_bridge_cidr" {
  description = "Docker bridge CIDR"
  type        = string
  default     = "172.17.0.1/16"
}

variable "aks_service_cidr" {
  description = "Service CIDR"
  type        = string
  default     = "10.0.0.0/16"
}

variable "aks_admin_group_object_ids" {
  description = "Azure AD group object IDs for AAD RBAC"
  type        = list(string)
  default     = []
}

variable "enable_monitoring" {
  description = "Enable Azure Monitor for AKS"
  type        = bool
  default     = true
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics workspace ID for monitoring"
  type        = string
}

variable "enable_azure_policy" {
  description = "Enable Azure Policy for AKS"
  type        = bool
  default     = true
}

variable "enable_key_vault_secrets_provider" {
  description = "Enable Key Vault secrets provider"
  type        = bool
  default     = true
}

variable "additional_node_pools" {
  description = "Additional node pools configuration"
  type = map(object({
    vm_size             = string
    node_count          = number
    enable_auto_scaling = bool
    min_count           = optional(number)
    max_count           = optional(number)
    max_pods            = number
    os_disk_size_gb     = number
    os_disk_type        = string
    node_taints         = optional(list(string))
    node_labels         = optional(map(string))
    zones               = optional(list(string))
  }))
  default = {}
}

# Application Gateway Configuration
variable "enable_app_gateway" {
  description = "Enable Application Gateway with WAF"
  type        = bool
  default     = false
}

variable "appgw_name" {
  description = "Name of the Application Gateway"
  type        = string
}

variable "appgw_sku_name" {
  description = "SKU name for Application Gateway"
  type        = string
  default     = "WAF_v2"
}

variable "appgw_sku_tier" {
  description = "SKU tier for Application Gateway"
  type        = string
  default     = "WAF_v2"
}

variable "appgw_capacity" {
  description = "Capacity for Application Gateway"
  type        = number
  default     = 2
}

variable "waf_firewall_mode" {
  description = "WAF firewall mode"
  type        = string
  default     = "Prevention"
}

variable "waf_rule_set_type" {
  description = "WAF rule set type"
  type        = string
  default     = "OWASP"
}

variable "waf_rule_set_version" {
  description = "WAF rule set version"
  type        = string
  default     = "3.2"
}

# Subnet Configuration
variable "aks_subnet_name" {
  description = "Name of the AKS subnet"
  type        = string
  default     = "aks"
}

variable "aks_subnet_prefixes" {
  description = "Address prefixes for AKS subnet"
  type        = list(string)
  default     = ["10.1.0.0/22"]
}

variable "appgw_subnet_name" {
  description = "Name of the Application Gateway subnet"
  type        = string
  default     = "appgw"
}

variable "appgw_subnet_prefixes" {
  description = "Address prefixes for Application Gateway subnet"
  type        = list(string)
  default     = ["10.1.4.0/24"]
}

variable "enable_private_endpoints" {
  description = "Enable private endpoints subnet"
  type        = bool
  default     = true
}

variable "private_endpoints_subnet_name" {
  description = "Name of the private endpoints subnet"
  type        = string
  default     = "private-endpoints"
}

variable "private_endpoints_subnet_prefixes" {
  description = "Address prefixes for private endpoints subnet"
  type        = list(string)
  default     = ["10.1.5.0/24"]
}

# Storage Configuration
variable "enable_storage" {
  description = "Enable storage account"
  type        = bool
  default     = true
}

variable "storage_account_name" {
  description = "Name of the storage account"
  type        = string
}

variable "storage_account_tier" {
  description = "Storage account tier"
  type        = string
  default     = "Standard"
}

variable "storage_account_replication_type" {
  description = "Storage account replication type"
  type        = string
  default     = "GRS"
}

variable "storage_account_kind" {
  description = "Storage account kind"
  type        = string
  default     = "StorageV2"
}

variable "enable_static_website" {
  description = "Enable static website hosting"
  type        = bool
  default     = false
}

variable "static_website_index_document" {
  description = "Index document for static website"
  type        = string
  default     = "index.html"
}

variable "static_website_error_document" {
  description = "Error document for static website"
  type        = string
  default     = "error.html"
}

variable "storage_network_default_action" {
  description = "Default action for storage network rules"
  type        = string
  default     = "Deny"
}

variable "storage_network_bypass" {
  description = "Services to bypass for storage network rules"
  type        = list(string)
  default     = ["AzureServices"]
}

variable "storage_allowed_subnet_ids" {
  description = "Allowed subnet IDs for storage"
  type        = list(string)
  default     = []
}

variable "storage_allowed_ip_rules" {
  description = "Allowed IP rules for storage"
  type        = list(string)
  default     = []
}

variable "storage_containers" {
  description = "Storage containers configuration"
  type = map(object({
    access_type = string
  }))
  default = {}
}

# Key Vault Configuration
variable "enable_key_vault" {
  description = "Enable Key Vault"
  type        = bool
  default     = true
}

variable "key_vault_name" {
  description = "Name of the Key Vault"
  type        = string
}

variable "tenant_id" {
  description = "Azure tenant ID"
  type        = string
}

variable "key_vault_disk_encryption" {
  description = "Enable disk encryption for Key Vault"
  type        = bool
  default     = true
}

variable "key_vault_soft_delete_retention_days" {
  description = "Soft delete retention days"
  type        = number
  default     = 90
}

variable "key_vault_purge_protection" {
  description = "Enable purge protection"
  type        = bool
  default     = true
}

variable "key_vault_sku" {
  description = "Key Vault SKU"
  type        = string
  default     = "standard"
}

variable "key_vault_network_default_action" {
  description = "Default action for Key Vault network rules"
  type        = string
  default     = "Deny"
}

variable "key_vault_network_bypass" {
  description = "Services to bypass for Key Vault network rules"
  type        = list(string)
  default     = ["AzureServices"]
}

variable "key_vault_allowed_ip_rules" {
  description = "Allowed IP rules for Key Vault"
  type        = list(string)
  default     = []
}

# ACR Configuration
variable "enable_acr" {
  description = "Enable Azure Container Registry"
  type        = bool
  default     = true
}

variable "acr_name" {
  description = "Name of the Azure Container Registry"
  type        = string
}

variable "acr_sku" {
  description = "SKU for Azure Container Registry"
  type        = string
  default     = "Basic"
}

variable "acr_admin_enabled" {
  description = "Enable admin user for ACR"
  type        = bool
  default     = false
}

variable "acr_network_default_action" {
  description = "Default action for ACR network rules"
  type        = string
  default     = "Allow"
}