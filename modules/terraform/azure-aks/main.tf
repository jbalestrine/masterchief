# AKS Cluster
resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.cluster_name
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = var.dns_prefix != null ? var.dns_prefix : var.cluster_name
  kubernetes_version  = var.kubernetes_version

  default_node_pool {
    name                = var.default_node_pool.name
    vm_size             = var.default_node_pool.vm_size
    node_count          = var.default_node_pool.enable_auto_scaling ? null : var.default_node_pool.node_count
    enable_auto_scaling = var.default_node_pool.enable_auto_scaling
    min_count           = var.default_node_pool.enable_auto_scaling ? var.default_node_pool.min_count : null
    max_count           = var.default_node_pool.enable_auto_scaling ? var.default_node_pool.max_count : null
    os_disk_size_gb     = var.default_node_pool.os_disk_size_gb
    max_pods            = var.default_node_pool.max_pods
    vnet_subnet_id      = var.subnet_id
    zones               = var.default_node_pool.availability_zones
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = var.network_plugin
    network_policy    = var.network_policy
    service_cidr      = var.service_cidr
    dns_service_ip    = var.dns_service_ip
    load_balancer_sku = "standard"
  }

  azure_active_directory_role_based_access_control {
    managed                = true
    azure_rbac_enabled     = var.enable_azure_rbac
    admin_group_object_ids = var.admin_group_object_ids
  }

  dynamic "http_application_routing" {
    for_each = var.enable_http_application_routing ? [1] : []
    content {
      enabled = true
    }
  }

  dynamic "azure_policy" {
    for_each = var.enable_azure_policy ? [1] : []
    content {
      enabled = true
    }
  }

  dynamic "oms_agent" {
    for_each = var.enable_oms_agent && var.log_analytics_workspace_id != null ? [1] : []
    content {
      log_analytics_workspace_id = var.log_analytics_workspace_id
    }
  }

  tags = merge(
    var.tags,
    {
      environment = var.environment
      managed_by  = "masterchief"
    }
  )
}

# Additional Node Pools
resource "azurerm_kubernetes_cluster_node_pool" "additional" {
  for_each = var.additional_node_pools

  name                  = each.key
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks.id
  vm_size               = each.value.vm_size
  node_count            = each.value.enable_auto_scaling ? null : each.value.node_count
  enable_auto_scaling   = each.value.enable_auto_scaling
  min_count             = each.value.enable_auto_scaling ? each.value.min_count : null
  max_count             = each.value.enable_auto_scaling ? each.value.max_count : null
  os_disk_size_gb       = each.value.os_disk_size_gb
  max_pods              = each.value.max_pods
  vnet_subnet_id        = var.subnet_id
  zones                 = each.value.availability_zones
  node_taints           = each.value.node_taints
  node_labels           = each.value.node_labels

  tags = merge(
    var.tags,
    {
      environment = var.environment
      managed_by  = "masterchief"
    }
  )
}
