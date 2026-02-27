# Azure Key Vault Module

This module creates an Azure Key Vault for managing secrets, keys, and certificates.

## Features

- Key Vault with configurable SKU (Standard/Premium)
- Access policies or RBAC authorization
- Network ACLs and firewall rules
- Soft delete and purge protection
- Support for secrets, keys, and certificates
- Azure service integrations (VM deployment, disk encryption, ARM templates)

## Usage

```hcl
data "azurerm_client_config" "current" {}

module "keyvault" {
  source = "../../modules/terraform/azure-keyvault"

  resource_group_name = "rg-security-example"
  location            = "eastus"
  keyvault_name       = "kv-example-001"
  
  sku_name = "standard"

  enabled_for_disk_encryption     = true
  enabled_for_template_deployment = true
  purge_protection_enabled        = true
  soft_delete_retention_days      = 90

  access_policies = [
    {
      tenant_id = data.azurerm_client_config.current.tenant_id
      object_id = data.azurerm_client_config.current.object_id

      secret_permissions = [
        "Get",
        "List",
        "Set",
        "Delete",
        "Recover",
        "Backup",
        "Restore"
      ]

      key_permissions = [
        "Get",
        "List",
        "Create",
        "Delete",
        "Recover"
      ]

      certificate_permissions = [
        "Get",
        "List",
        "Create",
        "Delete"
      ]
    }
  ]

  network_acls = {
    default_action = "Deny"
    bypass         = "AzureServices"
    ip_rules       = ["203.0.113.0/24"]
    virtual_network_subnet_ids = [
      "/subscriptions/.../subnets/subnet-app"
    ]
  }

  secrets = {
    "database-password" = var.db_password
    "api-key"           = var.api_key
  }

  tags = {
    project     = "example"
    cost_center = "security"
  }

  environment = "prod"
}
```

## Security Best Practices

1. **Enable Purge Protection**: Prevents permanent deletion of Key Vault and secrets
2. **Use RBAC Authorization**: More granular control than access policies
3. **Network ACLs**: Restrict access to specific networks
4. **Soft Delete**: Enables recovery of deleted secrets
5. **Audit Logging**: Enable diagnostic settings to log access

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| resource_group_name | Resource group name | string | - | yes |
| location | Azure region | string | - | yes |
| keyvault_name | Key Vault name (3-24 chars) | string | - | yes |
| sku_name | SKU (standard/premium) | string | "standard" | no |
| access_policies | Access policies | list(object) | [] | no |
| secrets | Secrets to store | map(string) | {} | no |
| purge_protection_enabled | Enable purge protection | bool | true | no |
| tags | Resource tags | map(string) | {} | no |

## Outputs

| Name | Description |
|------|-------------|
| keyvault_id | Key Vault resource ID |
| keyvault_name | Key Vault name |
| keyvault_uri | Key Vault URI |
| secret_names | List of secret names |

## SKU Comparison

### Standard
- Software-protected keys
- Suitable for most workloads
- Lower cost

### Premium
- HSM-backed keys
- FIPS 140-2 Level 2 validated
- Higher security requirements
