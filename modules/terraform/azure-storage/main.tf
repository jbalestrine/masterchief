# Storage Account
resource "azurerm_storage_account" "storage" {
  name                            = var.storage_account_name
  resource_group_name             = var.resource_group_name
  location                        = var.location
  account_tier                    = var.account_tier
  account_replication_type        = var.account_replication_type
  account_kind                    = var.account_kind
  access_tier                     = var.account_kind == "StorageV2" || var.account_kind == "BlobStorage" ? var.access_tier : null
  enable_https_traffic_only       = var.enable_https_traffic_only
  min_tls_version                 = var.min_tls_version
  is_hns_enabled                  = var.enable_hierarchical_namespace

  blob_properties {
    versioning_enabled  = var.enable_blob_versioning
    change_feed_enabled = var.enable_change_feed

    delete_retention_policy {
      days = 7
    }

    container_delete_retention_policy {
      days = 7
    }
  }

  network_rules {
    default_action             = var.network_rules.default_action
    bypass                     = var.network_rules.bypass
    ip_rules                   = var.network_rules.ip_rules
    virtual_network_subnet_ids = var.network_rules.virtual_network_subnet_ids
  }

  tags = merge(
    var.tags,
    {
      environment = var.environment
      managed_by  = "masterchief"
    }
  )
}

# Blob Containers
resource "azurerm_storage_container" "containers" {
  for_each = var.containers

  name                  = each.key
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = each.value.access_type
}

# File Shares
resource "azurerm_storage_share" "file_shares" {
  for_each = var.file_shares

  name                 = each.key
  storage_account_name = azurerm_storage_account.storage.name
  quota                = each.value.quota_gb
  enabled_protocol     = "SMB"
  
  # Access tier is only supported for certain storage account configurations
  access_tier = var.account_tier == "Premium" ? each.value.tier : null
}
