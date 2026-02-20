# Root Module Variables

# Azure Configuration
variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "tenant_id" {
  description = "Azure tenant ID"
  type        = string
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "East US"
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {
    Environment = "Production"
    Project     = "Enterprise-Hub-Spoke"
    ManagedBy   = "Terraform"
  }
}

# Hub Configuration
variable "hub_resource_group_name" {
  description = "Name of the hub resource group"
  type        = string
  default     = "rg-hub-network"
}

variable "hub_vnet_name" {
  description = "Name of the hub virtual network"
  type        = string
  default     = "vnet-hub"
}

variable "hub_address_space" {
  description = "Address space for the hub VNET"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

# Hub - Firewall Configuration
variable "enable_firewall" {
  description = "Enable Azure Firewall in hub"
  type        = bool
  default     = true
}

variable "firewall_name" {
  description = "Name of the Azure Firewall"
  type        = string
  default     = "fw-hub"
}

variable "firewall_sku_tier" {
  description = "SKU tier for Azure Firewall"
  type        = string
  default     = "Standard"
}

# Hub - Gateway Configuration
variable "enable_vpn_gateway" {
  description = "Enable VPN Gateway in hub"
  type        = bool
  default     = true
}

variable "vpn_gateway_name" {
  description = "Name of the VPN Gateway"
  type        = string
  default     = "vpngw-hub"
}

variable "vpn_gateway_sku" {
  description = "SKU for VPN Gateway"
  type        = string
  default     = "VpnGw1"
}

variable "enable_expressroute_gateway" {
  description = "Enable ExpressRoute Gateway in hub"
  type        = bool
  default     = false
}

variable "expressroute_gateway_name" {
  description = "Name of the ExpressRoute Gateway"
  type        = string
  default     = "ergw-hub"
}

variable "expressroute_gateway_sku" {
  description = "SKU for ExpressRoute Gateway"
  type        = string
  default     = "Standard"
}

# Hub - Bastion Configuration
variable "enable_bastion" {
  description = "Enable Azure Bastion in hub"
  type        = bool
  default     = true
}

variable "bastion_name" {
  description = "Name of the Azure Bastion"
  type        = string
  default     = "bastion-hub"
}

variable "bastion_sku" {
  description = "SKU for Azure Bastion"
  type        = string
  default     = "Basic"
}

# Hub - Route Table Configuration
variable "enable_route_table" {
  description = "Enable route table in hub"
  type        = bool
  default     = true
}

variable "route_table_name" {
  description = "Name of the route table"
  type        = string
  default     = "rt-hub"
}

# Spokes Configuration
variable "spokes" {
  description = "Configuration for spoke networks"
  type = list(object({
    name = string
    resource_group_name = string
    vnet_name = string
    address_space = list(string)

    # VNET Peering
    use_remote_gateways = optional(bool, true)
    allow_gateway_transit = optional(bool, true)

    # AKS Configuration
    enable_aks = optional(bool, true)
    aks_cluster_name = optional(string, "")
    aks_dns_prefix = optional(string, "")
    aks_kubernetes_version = optional(string, "1.27.0")
    aks_sku_tier = optional(string, "Free")
    aks_default_node_pool_name = optional(string, "default")
    aks_node_count = optional(number, 3)
    aks_vm_size = optional(string, "Standard_D2_v2")
    aks_enable_auto_scaling = optional(bool, true)
    aks_min_node_count = optional(number, 1)
    aks_max_node_count = optional(number, 10)
    aks_max_pods_per_node = optional(number, 30)
    aks_os_disk_size_gb = optional(number, 128)
    aks_os_disk_type = optional(string, "Managed")
    aks_node_pool_type = optional(string, "VirtualMachineScaleSets")
    aks_availability_zones = optional(list(string), ["1", "2", "3"])
    aks_network_plugin = optional(string, "azure")
    aks_network_policy = optional(string, "azure")
    aks_load_balancer_sku = optional(string, "standard")
    aks_outbound_type = optional(string, "loadBalancer")
    aks_dns_service_ip = optional(string, "10.0.0.10")
    aks_docker_bridge_cidr = optional(string, "172.17.0.1/16")
    aks_service_cidr = optional(string, "10.0.0.0/16")
    aks_admin_group_object_ids = optional(list(string), [])

    # Additional Node Pools
    additional_node_pools = optional(map(object({
      vm_size = string
      node_count = number
      enable_auto_scaling = bool
      min_count = optional(number)
      max_count = optional(number)
      max_pods = number
      os_disk_size_gb = number
      os_disk_type = string
      node_taints = optional(list(string))
      node_labels = optional(map(string))
      zones = optional(list(string))
    })), {})

    # Application Gateway
    enable_app_gateway = optional(bool, false)
    appgw_name = optional(string, "")
    appgw_sku_name = optional(string, "WAF_v2")
    appgw_sku_tier = optional(string, "WAF_v2")
    appgw_capacity = optional(number, 2)
    waf_firewall_mode = optional(string, "Prevention")
    waf_rule_set_type = optional(string, "OWASP")
    waf_rule_set_version = optional(string, "3.2")

    # Subnets
    aks_subnet_name = optional(string, "aks")
    aks_subnet_prefixes = optional(list(string), ["10.1.0.0/22"])
    appgw_subnet_name = optional(string, "appgw")
    appgw_subnet_prefixes = optional(list(string), ["10.1.4.0/24"])
    enable_private_endpoints = optional(bool, true)
    private_endpoints_subnet_name = optional(string, "private-endpoints")
    private_endpoints_subnet_prefixes = optional(list(string), ["10.1.5.0/24"])

    # Storage
    enable_storage = optional(bool, true)
    storage_account_name = optional(string, "")
    storage_account_tier = optional(string, "Standard")
    storage_account_replication_type = optional(string, "GRS")
    storage_account_kind = optional(string, "StorageV2")
    enable_static_website = optional(bool, false)
    static_website_index_document = optional(string, "index.html")
    static_website_error_document = optional(string, "error.html")
    storage_network_default_action = optional(string, "Deny")
    storage_network_bypass = optional(list(string), ["AzureServices"])
    storage_allowed_subnet_ids = optional(list(string), [])
    storage_allowed_ip_rules = optional(list(string), [])
    storage_containers = optional(map(object({
      access_type = string
    })), {})

    # Key Vault
    enable_key_vault = optional(bool, true)
    key_vault_name = optional(string, "")
    key_vault_disk_encryption = optional(bool, true)
    key_vault_soft_delete_retention_days = optional(number, 90)
    key_vault_purge_protection = optional(bool, true)
    key_vault_sku = optional(string, "standard")
    key_vault_network_default_action = optional(string, "Deny")
    key_vault_network_bypass = optional(list(string), ["AzureServices"])
    key_vault_allowed_ip_rules = optional(list(string), [])

    # ACR
    enable_acr = optional(bool, true)
    acr_name = optional(string, "")
    acr_sku = optional(string, "Basic")
    acr_admin_enabled = optional(bool, false)

    # Monitoring
    enable_monitoring = optional(bool, true)
  }))
  default = []
}

# User Management Configuration
variable "group_owners" {
  description = "Object IDs of group owners"
  type        = list(string)
  default     = []
}

variable "platform_admins_group_name" {
  description = "Name of the platform administrators group"
  type        = string
  default     = "Platform-Administrators"
}

variable "platform_admins_members" {
  description = "Object IDs of platform administrators"
  type        = list(string)
  default     = []
}

variable "developers_group_name" {
  description = "Name of the developers group"
  type        = string
  default     = "Developers"
}

variable "developers_members" {
  description = "Object IDs of developers"
  type        = list(string)
  default     = []
}

variable "devops_engineers_group_name" {
  description = "Name of the DevOps engineers group"
  type        = string
  default     = "DevOps-Engineers"
}

variable "devops_engineers_members" {
  description = "Object IDs of DevOps engineers"
  type        = list(string)
  default     = []
}

variable "security_auditors_group_name" {
  description = "Name of the security auditors group"
  type        = string
  default     = "Security-Auditors"
}

variable "security_auditors_members" {
  description = "Object IDs of security auditors"
  type        = list(string)
  default     = []
}

variable "end_users_group_name" {
  description = "Name of the end users group"
  type        = string
  default     = "End-Users"
}

variable "end_users_members" {
  description = "Object IDs of end users"
  type        = list(string)
  default     = []
}

# User Management Feature Toggles
variable "enable_user_management_aks" {
  description = "Enable AKS role assignments in user management"
  type        = bool
  default     = true
}

variable "enable_user_management_kv" {
  description = "Enable Key Vault access policies in user management"
  type        = bool
  default     = true
}

variable "enable_user_management_storage" {
  description = "Enable storage role assignments in user management"
  type        = bool
  default     = true
}

variable "enable_user_management_acr" {
  description = "Enable ACR role assignments in user management"
  type        = bool
  default     = true
}

# Custom Roles Configuration
variable "create_custom_roles" {
  description = "Create custom role definitions"
  type        = bool
  default     = true
}

variable "platform_admin_role_permissions" {
  description = "Additional permissions for platform admin role"
  type = object({
    actions     = optional(list(string), [])
    not_actions = optional(list(string), [])
  })
  default = {
    actions     = []
    not_actions = []
  }
}

variable "developer_role_permissions" {
  description = "Additional permissions for developer role"
  type = object({
    actions     = optional(list(string), [])
    not_actions = optional(list(string), [])
  })
  default = {
    actions     = []
    not_actions = []
  }
}

variable "devops_engineer_role_permissions" {
  description = "Additional permissions for DevOps engineer role"
  type = object({
    actions     = optional(list(string), [])
    not_actions = optional(list(string), [])
  })
  default = {
    actions     = []
    not_actions = []
  }
}

variable "security_auditor_role_permissions" {
  description = "Additional permissions for security auditor role"
  type = object({
    actions     = optional(list(string), [])
    not_actions = optional(list(string), [])
  })
  default = {
    actions     = []
    not_actions = []
  }
}

# Visualization Configuration
variable "enable_aks_overall" {
  description = "Enable AKS visualization"
  type        = bool
  default     = true
}

variable "enable_app_gateway_overall" {
  description = "Enable Application Gateway visualization"
  type        = bool
  default     = false
}

variable "enable_storage_overall" {
  description = "Enable storage visualization"
  type        = bool
  default     = true
}

variable "enable_key_vault_overall" {
  description = "Enable Key Vault visualization"
  type        = bool
  default     = true
}

variable "enable_acr_overall" {
  description = "Enable ACR visualization"
  type        = bool
  default     = true
}

variable "enable_monitoring_overall" {
  description = "Enable monitoring visualization"
  type        = bool
  default     = true
}

variable "enable_static_website_overall" {
  description = "Enable static website visualization"
  type        = bool
  default     = false
}

variable "user_groups_for_visualization" {
  description = "User groups for visualization"
  type        = list(string)
  default     = ["Platform-Administrators", "Developers", "DevOps-Engineers", "Security-Auditors", "End-Users"]
}

variable "custom_roles_for_visualization" {
  description = "Custom roles for visualization"
  type        = list(string)
  default     = ["Platform Administrator", "Developer", "DevOps Engineer", "Security Auditor"]
}