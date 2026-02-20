# Spoke Module
# Creates individual workload environments with AKS, storage, and cloning capabilities

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.0"
    }
  }
}

# Spoke Resource Group
resource "azurerm_resource_group" "spoke" {
  name     = var.spoke_resource_group_name
  location = var.location
  tags     = var.tags
}

# Spoke Virtual Network
resource "azurerm_virtual_network" "spoke" {
  name                = var.spoke_vnet_name
  location            = azurerm_resource_group.spoke.location
  resource_group_name = azurerm_resource_group.spoke.name
  address_space       = var.spoke_address_space
  tags                = var.tags
}

# VNET Peering to Hub
resource "azurerm_virtual_network_peering" "spoke_to_hub" {
  name                         = "${var.spoke_vnet_name}-to-hub"
  resource_group_name          = azurerm_resource_group.spoke.name
  virtual_network_name         = azurerm_virtual_network.spoke.name
  remote_virtual_network_id    = var.hub_vnet_id
  allow_virtual_network_access = true
  allow_forwarded_traffic      = true
  allow_gateway_transit        = false
  use_remote_gateways          = var.use_remote_gateways
}

resource "azurerm_virtual_network_peering" "hub_to_spoke" {
  provider                     = azurerm.hub
  name                         = "hub-to-${var.spoke_vnet_name}"
  resource_group_name          = var.hub_resource_group_name
  virtual_network_name         = var.hub_vnet_name
  remote_virtual_network_id    = azurerm_virtual_network.spoke.id
  allow_virtual_network_access = true
  allow_forwarded_traffic      = true
  allow_gateway_transit        = var.allow_gateway_transit
  use_remote_gateways          = false
}

# AKS Subnet
resource "azurerm_subnet" "aks" {
  count                = var.enable_aks ? 1 : 0
  name                 = var.aks_subnet_name
  resource_group_name  = azurerm_resource_group.spoke.name
  virtual_network_name = azurerm_virtual_network.spoke.name
  address_prefixes     = var.aks_subnet_prefixes
}

# Application Gateway Subnet (for WAF)
resource "azurerm_subnet" "appgw" {
  count                = var.enable_app_gateway ? 1 : 0
  name                 = var.appgw_subnet_name
  resource_group_name  = azurerm_resource_group.spoke.name
  virtual_network_name = azurerm_virtual_network.spoke.name
  address_prefixes     = var.appgw_subnet_prefixes
}

# Private Endpoints Subnet
resource "azurerm_subnet" "private_endpoints" {
  count                = var.enable_private_endpoints ? 1 : 0
  name                 = var.private_endpoints_subnet_name
  resource_group_name  = azurerm_resource_group.spoke.name
  virtual_network_name = azurerm_virtual_network.spoke.name
  address_prefixes     = var.private_endpoints_subnet_prefixes

  private_endpoint_network_policies_enabled = false
}

# Network Security Groups
resource "azurerm_network_security_group" "aks" {
  count               = var.enable_aks ? 1 : 0
  name                = "${var.spoke_vnet_name}-aks-nsg"
  location            = azurerm_resource_group.spoke.location
  resource_group_name = azurerm_resource_group.spoke.name
  tags                = var.tags
}

resource "azurerm_subnet_network_security_group_association" "aks" {
  count                     = var.enable_aks ? 1 : 0
  subnet_id                 = azurerm_subnet.aks[0].id
  network_security_group_id = azurerm_network_security_group.aks[0].id
}

# Route Table for AKS subnet
resource "azurerm_route_table" "aks" {
  count                         = var.enable_aks ? 1 : 0
  name                          = "${var.spoke_vnet_name}-aks-rt"
  location                      = azurerm_resource_group.spoke.location
  resource_group_name           = azurerm_resource_group.spoke.name
  disable_bgp_route_propagation = false

  route {
    name                   = "to-firewall"
    address_prefix         = "0.0.0.0/0"
    next_hop_type          = "VirtualAppliance"
    next_hop_in_ip_address = var.firewall_private_ip
  }

  tags = var.tags
}

resource "azurerm_subnet_route_table_association" "aks" {
  count          = var.enable_aks ? 1 : 0
  subnet_id      = azurerm_subnet.aks[0].id
  route_table_id = azurerm_route_table.aks[0].id
}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "aks" {
  count               = var.enable_aks ? 1 : 0
  name                = var.aks_cluster_name
  location            = azurerm_resource_group.spoke.location
  resource_group_name = azurerm_resource_group.spoke.name
  dns_prefix          = var.aks_dns_prefix
  kubernetes_version  = var.aks_kubernetes_version
  sku_tier            = var.aks_sku_tier

  default_node_pool {
    name                = var.aks_default_node_pool_name
    node_count          = var.aks_node_count
    vm_size             = var.aks_vm_size
    vnet_subnet_id      = azurerm_subnet.aks[0].id
    enable_auto_scaling = var.aks_enable_auto_scaling
    min_count           = var.aks_enable_auto_scaling ? var.aks_min_node_count : null
    max_count           = var.aks_enable_auto_scaling ? var.aks_max_node_count : null
    max_pods            = var.aks_max_pods_per_node
    os_disk_size_gb     = var.aks_os_disk_size_gb
    os_disk_type        = var.aks_os_disk_type
    type                = var.aks_node_pool_type
    zones               = var.aks_availability_zones
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin     = var.aks_network_plugin
    network_policy     = var.aks_network_policy
    load_balancer_sku  = var.aks_load_balancer_sku
    outbound_type      = var.aks_outbound_type
    dns_service_ip     = var.aks_dns_service_ip
    docker_bridge_cidr = var.aks_docker_bridge_cidr
    service_cidr       = var.aks_service_cidr
  }

  # Enable Azure AD integration
  azure_active_directory_role_based_access_control {
    managed                = true
    admin_group_object_ids = var.aks_admin_group_object_ids
  }

  # Enable Azure Monitor
  oms_agent {
    log_analytics_workspace_id = var.enable_monitoring ? var.log_analytics_workspace_id : null
  }

  # Enable Azure Policy
  azure_policy_enabled = var.enable_azure_policy

  # Enable Key Vault secrets provider
  key_vault_secrets_provider {
    secret_rotation_enabled = var.enable_key_vault_secrets_provider
  }

  tags = var.tags
}

# Additional Node Pools
resource "azurerm_kubernetes_cluster_node_pool" "additional" {
  for_each              = var.additional_node_pools
  name                  = each.key
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks[0].id
  vm_size               = each.value.vm_size
  node_count            = each.value.node_count
  vnet_subnet_id        = azurerm_subnet.aks[0].id
  enable_auto_scaling   = each.value.enable_auto_scaling
  min_count             = each.value.enable_auto_scaling ? each.value.min_count : null
  max_count             = each.value.enable_auto_scaling ? each.value.max_count : null
  max_pods              = each.value.max_pods
  os_disk_size_gb       = each.value.os_disk_size_gb
  os_disk_type          = each.value.os_disk_type
  node_taints           = each.value.node_taints
  node_labels           = each.value.node_labels
  zones                 = each.value.zones
  tags                  = var.tags
}

# Application Gateway (WAF)
resource "azurerm_public_ip" "appgw" {
  count               = var.enable_app_gateway ? 1 : 0
  name                = "${var.spoke_vnet_name}-appgw-pip"
  location            = azurerm_resource_group.spoke.location
  resource_group_name = azurerm_resource_group.spoke.name
  allocation_method   = "Static"
  sku                 = "Standard"
  tags                = var.tags
}

resource "azurerm_application_gateway" "waf" {
  count               = var.enable_app_gateway ? 1 : 0
  name                = var.appgw_name
  location            = azurerm_resource_group.spoke.location
  resource_group_name = azurerm_resource_group.spoke.name

  sku {
    name     = var.appgw_sku_name
    tier     = var.appgw_sku_tier
    capacity = var.appgw_capacity
  }

  gateway_ip_configuration {
    name      = "appgw-ip-config"
    subnet_id = azurerm_subnet.appgw[0].id
  }

  frontend_port {
    name = "http"
    port = 80
  }

  frontend_port {
    name = "https"
    port = 443
  }

  frontend_ip_configuration {
    name                 = "public"
    public_ip_address_id = azurerm_public_ip.appgw[0].id
  }

  backend_address_pool {
    name = "default"
  }

  backend_http_settings {
    name                  = "default"
    cookie_based_affinity = "Disabled"
    port                  = 80
    protocol              = "Http"
    request_timeout       = 20
  }

  http_listener {
    name                           = "http"
    frontend_ip_configuration_name = "public"
    frontend_port_name             = "http"
    protocol                       = "Http"
  }

  request_routing_rule {
    name                       = "default"
    rule_type                  = "Basic"
    http_listener_name         = "http"
    backend_address_pool_name  = "default"
    backend_http_settings_name = "default"
    priority                   = 100
  }

  # WAF Configuration
  waf_configuration {
    enabled          = true
    firewall_mode    = var.waf_firewall_mode
    rule_set_type    = var.waf_rule_set_type
    rule_set_version = var.waf_rule_set_version
  }

  tags = var.tags
}

# Storage Account
resource "azurerm_storage_account" "spoke" {
  count                    = var.enable_storage ? 1 : 0
  name                     = var.storage_account_name
  location                 = azurerm_resource_group.spoke.location
  resource_group_name      = azurerm_resource_group.spoke.name
  account_tier             = var.storage_account_tier
  account_replication_type = var.storage_account_replication_type
  account_kind             = var.storage_account_kind

  # Enable advanced threat protection
  dynamic "static_website" {
    for_each = var.enable_static_website ? [1] : []
    content {
      index_document     = var.static_website_index_document
      error_404_document = var.static_website_error_document
    }
  }

  # Network rules
  network_rules {
    default_action             = var.storage_network_default_action
    bypass                     = var.storage_network_bypass
    virtual_network_subnet_ids = var.storage_allowed_subnet_ids
    ip_rules                   = var.storage_allowed_ip_rules
  }

  tags = var.tags
}

# Storage Containers
resource "azurerm_storage_container" "containers" {
  for_each              = var.enable_storage ? var.storage_containers : {}
  name                  = each.key
  storage_account_name  = azurerm_storage_account.spoke[0].name
  container_access_type = each.value.access_type
}

# Key Vault
resource "azurerm_key_vault" "spoke" {
  count                       = var.enable_key_vault ? 1 : 0
  name                        = var.key_vault_name
  location                    = azurerm_resource_group.spoke.location
  resource_group_name         = azurerm_resource_group.spoke.name
  enabled_for_disk_encryption = var.key_vault_disk_encryption
  tenant_id                   = var.tenant_id
  soft_delete_retention_days  = var.key_vault_soft_delete_retention_days
  purge_protection_enabled    = var.key_vault_purge_protection
  sku_name                    = var.key_vault_sku

  network_acls {
    default_action = var.key_vault_network_default_action
    bypass         = var.key_vault_network_bypass
    ip_rules       = var.key_vault_allowed_ip_rules
    virtual_network_subnet_ids = var.enable_private_endpoints ? [
      azurerm_subnet.private_endpoints[0].id
    ] : []
  }

  tags = var.tags
}

# Private Endpoint for Key Vault
resource "azurerm_private_endpoint" "key_vault" {
  count               = var.enable_key_vault && var.enable_private_endpoints ? 1 : 0
  name                = "${var.key_vault_name}-pe"
  location            = azurerm_resource_group.spoke.location
  resource_group_name = azurerm_resource_group.spoke.name
  subnet_id           = azurerm_subnet.private_endpoints[0].id

  private_service_connection {
    name                           = "keyvault-connection"
    private_connection_resource_id = azurerm_key_vault.spoke[0].id
    is_manual_connection           = false
    subresource_names              = ["vault"]
  }

  tags = var.tags
}

# Azure Container Registry
resource "azurerm_container_registry" "acr" {
  count               = var.enable_acr ? 1 : 0
  name                = var.acr_name
  location            = azurerm_resource_group.spoke.location
  resource_group_name = azurerm_resource_group.spoke.name
  sku                 = var.acr_sku
  admin_enabled       = var.acr_admin_enabled

  network_rule_set {
    default_action = var.acr_network_default_action
  }

  tags = var.tags
}

# Private Endpoint for ACR
resource "azurerm_private_endpoint" "acr" {
  count               = var.enable_acr && var.enable_private_endpoints ? 1 : 0
  name                = "${var.acr_name}-pe"
  location            = azurerm_resource_group.spoke.location
  resource_group_name = azurerm_resource_group.spoke.name
  subnet_id           = azurerm_subnet.private_endpoints[0].id

  private_service_connection {
    name                           = "acr-connection"
    private_connection_resource_id = azurerm_container_registry.acr[0].id
    is_manual_connection           = false
    subresource_names              = ["registry"]
  }

  tags = var.tags
}