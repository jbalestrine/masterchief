# Root Module - Enterprise Hub-and-Spoke Architecture

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }

  required_version = ">= 1.0"
}

# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
  }
}

# Configure Azure AD Provider
provider "azuread" {
  tenant_id = var.tenant_id
}

# Hub Module
module "hub" {
  source = "../hub"

  hub_resource_group_name = var.hub_resource_group_name
  location                = var.location
  hub_vnet_name          = var.hub_vnet_name
  hub_address_space      = var.hub_address_space
  tags                   = var.tags

  # Firewall Configuration
  enable_firewall        = var.enable_firewall
  firewall_name          = var.firewall_name
  firewall_sku_tier      = var.firewall_sku_tier

  # Gateway Configuration
  enable_vpn_gateway     = var.enable_vpn_gateway
  vpn_gateway_name       = var.vpn_gateway_name
  vpn_gateway_sku        = var.vpn_gateway_sku

  enable_expressroute_gateway = var.enable_expressroute_gateway
  expressroute_gateway_name   = var.expressroute_gateway_name
  expressroute_gateway_sku    = var.expressroute_gateway_sku

  # Bastion Configuration
  enable_bastion         = var.enable_bastion
  bastion_name           = var.bastion_name
  bastion_sku            = var.bastion_sku

  # Route Table Configuration
  enable_route_table     = var.enable_route_table
  route_table_name       = var.route_table_name
}

# Spoke Modules
module "spokes" {
  source = "../spoke"

  for_each = { for spoke in var.spokes : spoke.name => spoke }

  spoke_resource_group_name = each.value.resource_group_name
  location                  = var.location
  spoke_vnet_name          = each.value.vnet_name
  spoke_address_space      = each.value.address_space
  tags                     = var.tags

  # Hub References
  hub_vnet_id             = module.hub.hub_vnet_id
  hub_resource_group_name = var.hub_resource_group_name
  hub_vnet_name          = var.hub_vnet_name
  firewall_private_ip    = module.hub.firewall_private_ip

  # VNET Peering
  use_remote_gateways    = each.value.use_remote_gateways
  allow_gateway_transit  = each.value.allow_gateway_transit

  # AKS Configuration
  enable_aks             = each.value.enable_aks
  aks_cluster_name       = each.value.aks_cluster_name != "" ? each.value.aks_cluster_name : "${each.value.name}-aks"
  aks_dns_prefix         = each.value.aks_dns_prefix != "" ? each.value.aks_dns_prefix : each.value.name
  aks_kubernetes_version = each.value.aks_kubernetes_version
  aks_sku_tier           = each.value.aks_sku_tier
  aks_default_node_pool_name = each.value.aks_default_node_pool_name
  aks_node_count         = each.value.aks_node_count
  aks_vm_size            = each.value.aks_vm_size
  aks_enable_auto_scaling = each.value.aks_enable_auto_scaling
  aks_min_node_count     = each.value.aks_min_node_count
  aks_max_node_count     = each.value.aks_max_node_count
  aks_max_pods_per_node  = each.value.aks_max_pods_per_node
  aks_os_disk_size_gb    = each.value.aks_os_disk_size_gb
  aks_os_disk_type       = each.value.aks_os_disk_type
  aks_node_pool_type     = each.value.aks_node_pool_type
  aks_availability_zones = each.value.aks_availability_zones
  aks_network_plugin     = each.value.aks_network_plugin
  aks_network_policy     = each.value.aks_network_policy
  aks_load_balancer_sku  = each.value.aks_load_balancer_sku
  aks_outbound_type      = each.value.aks_outbound_type
  aks_dns_service_ip     = each.value.aks_dns_service_ip
  aks_docker_bridge_cidr = each.value.aks_docker_bridge_cidr
  aks_service_cidr       = each.value.aks_service_cidr
  aks_admin_group_object_ids = each.value.aks_admin_group_object_ids
  enable_monitoring      = each.value.enable_monitoring
  log_analytics_workspace_id = each.value.enable_monitoring ? module.spokes[each.key].log_analytics_workspace_id : null

  # Additional Node Pools
  additional_node_pools  = each.value.additional_node_pools

  # Application Gateway
  enable_app_gateway     = each.value.enable_app_gateway
  appgw_name             = each.value.appgw_name != "" ? each.value.appgw_name : "${each.value.name}-appgw"
  appgw_sku_name         = each.value.appgw_sku_name
  appgw_sku_tier         = each.value.appgw_sku_tier
  appgw_capacity         = each.value.appgw_capacity
  waf_firewall_mode      = each.value.waf_firewall_mode
  waf_rule_set_type      = each.value.waf_rule_set_type
  waf_rule_set_version   = each.value.waf_rule_set_version

  # Subnets
  aks_subnet_name        = each.value.aks_subnet_name
  aks_subnet_prefixes    = each.value.aks_subnet_prefixes
  appgw_subnet_name      = each.value.appgw_subnet_name
  appgw_subnet_prefixes  = each.value.appgw_subnet_prefixes
  enable_private_endpoints = each.value.enable_private_endpoints
  private_endpoints_subnet_name = each.value.private_endpoints_subnet_name
  private_endpoints_subnet_prefixes = each.value.private_endpoints_subnet_prefixes

  # Storage
  enable_storage         = each.value.enable_storage
  storage_account_name   = each.value.storage_account_name != "" ? each.value.storage_account_name : "${each.value.name}storage"
  storage_account_tier   = each.value.storage_account_tier
  storage_account_replication_type = each.value.storage_account_replication_type
  storage_account_kind   = each.value.storage_account_kind
  enable_static_website  = each.value.enable_static_website
  static_website_index_document = each.value.static_website_index_document
  static_website_error_document = each.value.static_website_error_document
  storage_network_default_action = each.value.storage_network_default_action
  storage_network_bypass = each.value.storage_network_bypass
  storage_allowed_subnet_ids = each.value.storage_allowed_subnet_ids
  storage_allowed_ip_rules = each.value.storage_allowed_ip_rules
  storage_containers     = each.value.storage_containers

  # Key Vault
  enable_key_vault       = each.value.enable_key_vault
  key_vault_name         = each.value.key_vault_name != "" ? each.value.key_vault_name : "${each.value.name}-kv"
  key_vault_disk_encryption = each.value.key_vault_disk_encryption
  key_vault_soft_delete_retention_days = each.value.key_vault_soft_delete_retention_days
  key_vault_purge_protection = each.value.key_vault_purge_protection
  key_vault_sku          = each.value.key_vault_sku
  key_vault_network_default_action = each.value.key_vault_network_default_action
  key_vault_network_bypass = each.value.key_vault_network_bypass
  key_vault_allowed_ip_rules = each.value.key_vault_allowed_ip_rules

  # ACR
  enable_acr             = each.value.enable_acr
  acr_name               = each.value.acr_name != "" ? each.value.acr_name : "${each.value.name}acr"
  acr_sku                = each.value.acr_sku
  acr_admin_enabled      = each.value.acr_admin_enabled
}

# User Management Module
module "user_management" {
  source = "../user_management"

  scope                   = "/subscriptions/${var.subscription_id}"
  tenant_id              = var.tenant_id

  # Group Configuration
  group_owners           = var.group_owners
  platform_admins_group_name = var.platform_admins_group_name
  platform_admins_members = var.platform_admins_members
  developers_group_name  = var.developers_group_name
  developers_members     = var.developers_members
  devops_engineers_group_name = var.devops_engineers_group_name
  devops_engineers_members = var.devops_engineers_members
  security_auditors_group_name = var.security_auditors_group_name
  security_auditors_members = var.security_auditors_members
  end_users_group_name   = var.end_users_group_name
  end_users_members      = var.end_users_members

  # Resource IDs for role assignments
  resource_group_ids     = concat(
    [module.hub.hub_resource_group_name],
    [for spoke in module.spokes : spoke.spoke_resource_group_name]
  )

  # Service-specific IDs
  aks_cluster_id         = var.enable_user_management_aks ? flatten([for spoke in module.spokes : spoke.aks_cluster_id if spoke.aks_cluster_id != null])[0] : ""
  key_vault_id           = var.enable_user_management_kv ? flatten([for spoke in module.spokes : spoke.key_vault_id if spoke.key_vault_id != null])[0] : ""
  storage_account_id     = var.enable_user_management_storage ? flatten([for spoke in module.spokes : spoke.storage_account_id if spoke.storage_account_id != null])[0] : ""
  acr_id                 = var.enable_user_management_acr ? flatten([for spoke in module.spokes : spoke.acr_id if spoke.acr_id != null])[0] : ""

  # Feature toggles
  enable_aks_role_assignments = var.enable_user_management_aks
  enable_key_vault_access = var.enable_user_management_kv
  enable_storage_role_assignments = var.enable_user_management_storage
  enable_acr_role_assignments = var.enable_user_management_acr

  # Custom roles
  create_custom_roles    = var.create_custom_roles
  platform_admin_role_permissions = var.platform_admin_role_permissions
  developer_role_permissions = var.developer_role_permissions
  devops_engineer_role_permissions = var.devops_engineer_role_permissions
  security_auditor_role_permissions = var.security_auditor_role_permissions

  tags = var.tags
}

# Visualization Module
module "visualization" {
  source = "../visualization"

  hub_resource_group_name = var.hub_resource_group_name
  hub_vnet_name          = var.hub_vnet_name
  hub_address_space      = var.hub_address_space

  spoke_resource_groups  = [for spoke in module.spokes : spoke.spoke_resource_group_name]
  spoke_vnets            = [for spoke in module.spokes : {
    name           = spoke.spoke_vnet_name
    resource_group = spoke.spoke_resource_group_name
    address_space  = spoke.spoke_vnet_address_space
  }]

  enable_aks             = var.enable_aks_overall
  aks_clusters           = flatten([for spoke in module.spokes : [
    for cluster in (spoke.aks_cluster_name != null ? [spoke] : []) : {
      name               = cluster.aks_cluster_name
      resource_group     = cluster.spoke_resource_group_name
      node_count         = var.spokes[index(var.spokes.*.name, spoke.name)].aks_node_count
      kubernetes_version = var.spokes[index(var.spokes.*.name, spoke.name)].aks_kubernetes_version
    }
  ]])

  enable_app_gateway     = var.enable_app_gateway_overall
  enable_storage         = var.enable_storage_overall
  enable_key_vault       = var.enable_key_vault_overall
  enable_acr             = var.enable_acr_overall
  enable_monitoring      = var.enable_monitoring_overall

  user_groups            = var.user_groups_for_visualization
  custom_roles           = var.custom_roles_for_visualization

  location               = var.location
  subscription_id        = var.subscription_id
  tenant_id              = var.tenant_id
  tags                   = var.tags
  enable_static_website  = var.enable_static_website_overall
}