data "azurerm_client_config" "current" {}

# Key Vault
resource "azurerm_key_vault" "keyvault" {
  name                            = var.keyvault_name
  location                        = var.location
  resource_group_name             = var.resource_group_name
  tenant_id                       = data.azurerm_client_config.current.tenant_id
  sku_name                        = var.sku_name
  enabled_for_deployment          = var.enabled_for_deployment
  enabled_for_disk_encryption     = var.enabled_for_disk_encryption
  enabled_for_template_deployment = var.enabled_for_template_deployment
  enable_rbac_authorization       = var.enable_rbac_authorization
  purge_protection_enabled        = var.purge_protection_enabled
  soft_delete_retention_days      = var.soft_delete_retention_days

  network_acls {
    default_action             = var.network_acls.default_action
    bypass                     = var.network_acls.bypass
    ip_rules                   = var.network_acls.ip_rules
    virtual_network_subnet_ids = var.network_acls.virtual_network_subnet_ids
  }

  tags = merge(
    var.tags,
    {
      environment = var.environment
      managed_by  = "masterchief"
    }
  )
}

# Access Policies
resource "azurerm_key_vault_access_policy" "policies" {
  for_each = { for idx, policy in var.access_policies : idx => policy }

  key_vault_id = azurerm_key_vault.keyvault.id
  tenant_id    = each.value.tenant_id
  object_id    = each.value.object_id

  key_permissions         = each.value.key_permissions
  secret_permissions      = each.value.secret_permissions
  certificate_permissions = each.value.certificate_permissions
}

# Secrets
resource "azurerm_key_vault_secret" "secrets" {
  for_each = var.secrets

  name         = each.key
  value        = each.value
  key_vault_id = azurerm_key_vault.keyvault.id

  depends_on = [azurerm_key_vault_access_policy.policies]
}
