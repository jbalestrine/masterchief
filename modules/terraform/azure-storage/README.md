# Azure Storage Account Module

This module creates an Azure Storage Account with configurable tiers, replication, containers, and file shares.

## Features

- Configurable performance tier (Standard/Premium)
- Multiple replication options (LRS, GRS, ZRS, etc.)
- Blob containers with access levels
- File shares with quotas
- Data Lake Gen2 support (hierarchical namespace)
- Blob versioning and change feed
- Network rules and firewall
- HTTPS enforcement and TLS configuration

## Usage

```hcl
module "storage" {
  source = "../../modules/terraform/azure-storage"

  resource_group_name   = "rg-storage-example"
  location              = "eastus"
  storage_account_name  = "stexample001"
  
  account_tier             = "Standard"
  account_replication_type = "GRS"
  access_tier              = "Hot"

  enable_blob_versioning = true
  enable_change_feed     = true

  containers = {
    "data" = {
      access_type = "private"
    }
    "logs" = {
      access_type = "private"
    }
  }

  file_shares = {
    "shared" = {
      quota_gb = 100
      tier     = "TransactionOptimized"
    }
  }

  network_rules = {
    default_action = "Deny"
    bypass         = ["AzureServices"]
    ip_rules       = ["203.0.113.0/24"]
    virtual_network_subnet_ids = [
      "/subscriptions/.../subnets/subnet-app"
    ]
  }

  tags = {
    project     = "example"
    cost_center = "engineering"
  }

  environment = "prod"
}
```

## Performance Tiers

### Standard Tier
- General-purpose storage
- Supports all storage types (blobs, files, queues, tables)
- LRS, GRS, RAGRS, ZRS, GZRS, RAGZRS replication
- Hot and Cool access tiers

### Premium Tier
- High-performance storage
- SSD-based
- LRS or ZRS replication only
- Specialized types: BlockBlobStorage, FileStorage

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| resource_group_name | Resource group name | string | - | yes |
| location | Azure region | string | - | yes |
| storage_account_name | Storage account name (3-24 chars, lowercase alphanumeric) | string | - | yes |
| account_tier | Performance tier | string | "Standard" | no |
| account_replication_type | Replication type | string | "LRS" | no |
| containers | Blob containers | map(object) | {} | no |
| file_shares | File shares | map(object) | {} | no |
| tags | Resource tags | map(string) | {} | no |

## Outputs

| Name | Description |
|------|-------------|
| storage_account_id | Storage account resource ID |
| storage_account_name | Storage account name |
| primary_connection_string | Primary connection string (sensitive) |
| primary_blob_endpoint | Primary blob endpoint URL |
| container_names | List of container names |
| file_share_names | List of file share names |
