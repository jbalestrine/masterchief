# User Management Module Outputs

output "platform_admins_group_id" {
  description = "Object ID of the platform administrators group"
  value       = azuread_group.platform_admins.object_id
}

output "platform_admins_group_name" {
  description = "Display name of the platform administrators group"
  value       = azuread_group.platform_admins.display_name
}

output "developers_group_id" {
  description = "Object ID of the developers group"
  value       = azuread_group.developers.object_id
}

output "developers_group_name" {
  description = "Display name of the developers group"
  value       = azuread_group.developers.display_name
}

output "devops_engineers_group_id" {
  description = "Object ID of the DevOps engineers group"
  value       = azuread_group.devops_engineers.object_id
}

output "devops_engineers_group_name" {
  description = "Display name of the DevOps engineers group"
  value       = azuread_group.devops_engineers.display_name
}

output "security_auditors_group_id" {
  description = "Object ID of the security auditors group"
  value       = azuread_group.security_auditors.object_id
}

output "security_auditors_group_name" {
  description = "Display name of the security auditors group"
  value       = azuread_group.security_auditors.display_name
}

output "end_users_group_id" {
  description = "Object ID of the end users group"
  value       = azuread_group.end_users.object_id
}

output "end_users_group_name" {
  description = "Display name of the end users group"
  value       = azuread_group.end_users.display_name
}

output "platform_admin_role_id" {
  description = "ID of the platform administrator custom role"
  value       = var.create_custom_roles ? azurerm_role_definition.platform_admin.id : null
}

output "platform_admin_role_name" {
  description = "Name of the platform administrator custom role"
  value       = var.create_custom_roles ? azurerm_role_definition.platform_admin.name : null
}

output "developer_role_id" {
  description = "ID of the developer custom role"
  value       = var.create_custom_roles ? azurerm_role_definition.developer.id : null
}

output "developer_role_name" {
  description = "Name of the developer custom role"
  value       = var.create_custom_roles ? azurerm_role_definition.developer.name : null
}

output "devops_engineer_role_id" {
  description = "ID of the DevOps engineer custom role"
  value       = var.create_custom_roles ? azurerm_role_definition.devops_engineer.id : null
}

output "devops_engineer_role_name" {
  description = "Name of the DevOps engineer custom role"
  value       = var.create_custom_roles ? azurerm_role_definition.devops_engineer.name : null
}

output "security_auditor_role_id" {
  description = "ID of the security auditor custom role"
  value       = var.create_custom_roles ? azurerm_role_definition.security_auditor.id : null
}

output "security_auditor_role_name" {
  description = "Name of the security auditor custom role"
  value       = var.create_custom_roles ? azurerm_role_definition.security_auditor.name : null
}

output "all_groups" {
  description = "Map of all created groups with their object IDs"
  value = {
    platform_admins    = azuread_group.platform_admins.object_id
    developers         = azuread_group.developers.object_id
    devops_engineers   = azuread_group.devops_engineers.object_id
    security_auditors  = azuread_group.security_auditors.object_id
    end_users          = azuread_group.end_users.object_id
  }
}

output "all_custom_roles" {
  description = "Map of all custom roles with their IDs"
  value = var.create_custom_roles ? {
    platform_admin     = azurerm_role_definition.platform_admin.id
    developer          = azurerm_role_definition.developer.id
    devops_engineer    = azurerm_role_definition.devops_engineer.id
    security_auditor   = azurerm_role_definition.security_auditor.id
  } : {}
}

output "role_assignments" {
  description = "List of all role assignment IDs"
  value = concat(
    [azurerm_role_assignment.platform_admins_subscription.id],
    [azurerm_role_assignment.developers_subscription.id],
    [azurerm_role_assignment.devops_engineers_subscription.id],
    [azurerm_role_assignment.security_auditors_subscription.id],
    var.enable_aks_role_assignments ? [
      azurerm_role_assignment.platform_admins_aks[0].id,
      azurerm_role_assignment.developers_aks[0].id,
      azurerm_role_assignment.devops_engineers_aks[0].id
    ] : [],
    var.enable_storage_role_assignments ? [
      azurerm_role_assignment.platform_admins_storage[0].id,
      azurerm_role_assignment.developers_storage[0].id,
      azurerm_role_assignment.devops_engineers_storage[0].id
    ] : [],
    var.enable_acr_role_assignments ? [
      azurerm_role_assignment.platform_admins_acr[0].id,
      azurerm_role_assignment.developers_acr[0].id,
      azurerm_role_assignment.devops_engineers_acr[0].id
    ] : [],
    [for ra in azurerm_role_assignment.platform_admins_resource_groups : ra.id],
    [for ra in azurerm_role_assignment.developers_resource_groups : ra.id],
    [for ra in azurerm_role_assignment.devops_engineers_resource_groups : ra.id],
    [for ra in azurerm_role_assignment.security_auditors_resource_groups : ra.id]
  )
}

output "key_vault_access_policies" {
  description = "List of Key Vault access policy IDs"
  value = var.enable_key_vault_access ? [
    azurerm_key_vault_access_policy.platform_admins_kv[0].id,
    azurerm_key_vault_access_policy.developers_kv[0].id,
    azurerm_key_vault_access_policy.devops_engineers_kv[0].id
  ] : []
}