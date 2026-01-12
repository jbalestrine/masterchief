output "keyvault_id" {
  description = "Key Vault resource ID"
  value       = azurerm_key_vault.keyvault.id
}

output "keyvault_name" {
  description = "Key Vault name"
  value       = azurerm_key_vault.keyvault.name
}

output "keyvault_uri" {
  description = "Key Vault URI"
  value       = azurerm_key_vault.keyvault.vault_uri
}

output "tenant_id" {
  description = "Tenant ID"
  value       = azurerm_key_vault.keyvault.tenant_id
}

output "secret_names" {
  description = "List of secret names in Key Vault"
  value       = [for s in azurerm_key_vault_secret.secrets : s.name]
}
