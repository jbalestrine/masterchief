# User Management Module - Azure AD Integration and RBAC

# Azure AD Groups for different roles
resource "azuread_group" "platform_admins" {
  display_name     = var.platform_admins_group_name
  description      = "Platform Administrators with full access to all resources"
  security_enabled = true
  owners           = var.group_owners
  members          = var.platform_admins_members
}

resource "azuread_group" "developers" {
  display_name     = var.developers_group_name
  description      = "Developers with access to development environments"
  security_enabled = true
  owners           = var.group_owners
  members          = var.developers_members
}

resource "azuread_group" "devops_engineers" {
  display_name     = var.devops_engineers_group_name
  description      = "DevOps engineers with access to CI/CD and infrastructure"
  security_enabled = true
  owners           = var.group_owners
  members          = var.devops_engineers_members
}

resource "azuread_group" "security_auditors" {
  display_name     = var.security_auditors_group_name
  description      = "Security auditors with read-only access for compliance"
  security_enabled = true
  owners           = var.group_owners
  members          = var.security_auditors_members
}

resource "azuread_group" "end_users" {
  display_name     = var.end_users_group_name
  description      = "End users with access to applications"
  security_enabled = true
  owners           = var.group_owners
  members          = var.end_users_members
}

# Custom role definitions for fine-grained access control
resource "azurerm_role_definition" "platform_admin" {
  name        = "Platform Administrator"
  scope       = var.scope
  description = "Custom role for platform administrators with elevated permissions"

  permissions {
    actions = [
      "Microsoft.Authorization/*/read",
      "Microsoft.Authorization/*/write",
      "Microsoft.Authorization/*/delete",
      "Microsoft.Resources/subscriptions/resourceGroups/read",
      "Microsoft.Resources/subscriptions/resourceGroups/write",
      "Microsoft.Resources/subscriptions/resourceGroups/delete",
      "Microsoft.Network/*/read",
      "Microsoft.Network/*/write",
      "Microsoft.Network/*/delete",
      "Microsoft.Compute/*/read",
      "Microsoft.Compute/*/write",
      "Microsoft.Compute/*/delete",
      "Microsoft.ContainerService/*/read",
      "Microsoft.ContainerService/*/write",
      "Microsoft.ContainerService/*/delete",
      "Microsoft.Storage/*/read",
      "Microsoft.Storage/*/write",
      "Microsoft.Storage/*/delete",
      "Microsoft.KeyVault/*/read",
      "Microsoft.KeyVault/*/write",
      "Microsoft.KeyVault/*/delete",
      "Microsoft.ManagedIdentity/*/read",
      "Microsoft.ManagedIdentity/*/write",
      "Microsoft.ManagedIdentity/*/delete"
    ]
    not_actions = []
  }

  assignable_scopes = [
    var.scope
  ]
}

resource "azurerm_role_definition" "developer" {
  name        = "Developer"
  scope       = var.scope
  description = "Custom role for developers with application deployment permissions"

  permissions {
    actions = [
      "Microsoft.ContainerService/managedClusters/read",
      "Microsoft.ContainerService/managedClusters/write",
      "Microsoft.ContainerRegistry/registries/read",
      "Microsoft.ContainerRegistry/registries/write",
      "Microsoft.Storage/storageAccounts/read",
      "Microsoft.Storage/storageAccounts/write",
      "Microsoft.KeyVault/vaults/read",
      "Microsoft.KeyVault/vaults/write",
      "Microsoft.Network/virtualNetworks/read",
      "Microsoft.Network/virtualNetworks/write",
      "Microsoft.Network/subnets/read",
      "Microsoft.Network/subnets/write"
    ]
    not_actions = [
      "Microsoft.ContainerService/managedClusters/delete",
      "Microsoft.ContainerRegistry/registries/delete",
      "Microsoft.Storage/storageAccounts/delete",
      "Microsoft.KeyVault/vaults/delete",
      "Microsoft.Network/virtualNetworks/delete",
      "Microsoft.Network/subnets/delete"
    ]
  }

  assignable_scopes = [
    var.scope
  ]
}

resource "azurerm_role_definition" "devops_engineer" {
  name        = "DevOps Engineer"
  scope       = var.scope
  description = "Custom role for DevOps engineers with infrastructure management permissions"

  permissions {
    actions = [
      "Microsoft.ContainerService/*/read",
      "Microsoft.ContainerService/*/write",
      "Microsoft.ContainerRegistry/*/read",
      "Microsoft.ContainerRegistry/*/write",
      "Microsoft.Storage/*/read",
      "Microsoft.Storage/*/write",
      "Microsoft.Network/*/read",
      "Microsoft.Network/*/write",
      "Microsoft.Compute/*/read",
      "Microsoft.Compute/*/write",
      "Microsoft.KeyVault/*/read",
      "Microsoft.KeyVault/*/write",
      "Microsoft.ManagedIdentity/*/read",
      "Microsoft.ManagedIdentity/*/write"
    ]
    not_actions = [
      "Microsoft.ContainerService/managedClusters/delete",
      "Microsoft.ContainerRegistry/registries/delete",
      "Microsoft.Storage/storageAccounts/delete",
      "Microsoft.Network/virtualNetworks/delete",
      "Microsoft.Compute/virtualMachines/delete",
      "Microsoft.KeyVault/vaults/delete",
      "Microsoft.ManagedIdentity/userAssignedIdentities/delete"
    ]
  }

  assignable_scopes = [
    var.scope
  ]
}

resource "azurerm_role_definition" "security_auditor" {
  name        = "Security Auditor"
  scope       = var.scope
  description = "Custom role for security auditors with read-only access"

  permissions {
    actions = [
      "Microsoft.Authorization/*/read",
      "Microsoft.Resources/*/read",
      "Microsoft.Network/*/read",
      "Microsoft.Compute/*/read",
      "Microsoft.ContainerService/*/read",
      "Microsoft.Storage/*/read",
      "Microsoft.KeyVault/*/read",
      "Microsoft.ManagedIdentity/*/read",
      "Microsoft.Security/*/read",
      "Microsoft.PolicyInsights/*/read"
    ]
    not_actions = []
  }

  assignable_scopes = [
    var.scope
  ]
}

# Role assignments for subscription level
resource "azurerm_role_assignment" "platform_admins_subscription" {
  scope                = var.scope
  role_definition_name = azurerm_role_definition.platform_admin.name
  principal_id         = azuread_group.platform_admins.object_id
}

resource "azurerm_role_assignment" "developers_subscription" {
  scope                = var.scope
  role_definition_name = azurerm_role_definition.developer.name
  principal_id         = azuread_group.developers.object_id
}

resource "azurerm_role_assignment" "devops_engineers_subscription" {
  scope                = var.scope
  role_definition_name = azurerm_role_definition.devops_engineer.name
  principal_id         = azuread_group.devops_engineers.object_id
}

resource "azurerm_role_assignment" "security_auditors_subscription" {
  scope                = var.scope
  role_definition_name = azurerm_role_definition.security_auditor.name
  principal_id         = azuread_group.security_auditors.object_id
}

# AKS-specific role assignments
resource "azurerm_role_assignment" "platform_admins_aks" {
  count                = var.enable_aks_role_assignments ? 1 : 0
  scope                = var.aks_cluster_id
  role_definition_name = "Azure Kubernetes Service RBAC Cluster Admin"
  principal_id         = azuread_group.platform_admins.object_id
}

resource "azurerm_role_assignment" "developers_aks" {
  count                = var.enable_aks_role_assignments ? 1 : 0
  scope                = var.aks_cluster_id
  role_definition_name = "Azure Kubernetes Service RBAC Writer"
  principal_id         = azuread_group.developers.object_id
}

resource "azurerm_role_assignment" "devops_engineers_aks" {
  count                = var.enable_aks_role_assignments ? 1 : 0
  scope                = var.aks_cluster_id
  role_definition_name = "Azure Kubernetes Service RBAC Admin"
  principal_id         = azuread_group.devops_engineers.object_id
}

# Key Vault access policies
resource "azurerm_key_vault_access_policy" "platform_admins_kv" {
  count        = var.enable_key_vault_access ? 1 : 0
  key_vault_id = var.key_vault_id
  tenant_id    = var.tenant_id
  object_id    = azuread_group.platform_admins.object_id

  key_permissions = [
    "Get", "List", "Update", "Create", "Import", "Delete", "Recover", "Backup", "Restore"
  ]

  secret_permissions = [
    "Get", "List", "Set", "Delete", "Recover", "Backup", "Restore"
  ]

  certificate_permissions = [
    "Get", "List", "Update", "Create", "Import", "Delete", "Recover", "Backup", "Restore"
  ]
}

resource "azurerm_key_vault_access_policy" "developers_kv" {
  count        = var.enable_key_vault_access ? 1 : 0
  key_vault_id = var.key_vault_id
  tenant_id    = var.tenant_id
  object_id    = azuread_group.developers.object_id

  key_permissions = [
    "Get", "List"
  ]

  secret_permissions = [
    "Get", "List", "Set"
  ]

  certificate_permissions = [
    "Get", "List"
  ]
}

resource "azurerm_key_vault_access_policy" "devops_engineers_kv" {
  count        = var.enable_key_vault_access ? 1 : 0
  key_vault_id = var.key_vault_id
  tenant_id    = var.tenant_id
  object_id    = azuread_group.devops_engineers.object_id

  key_permissions = [
    "Get", "List", "Update", "Create", "Import", "Delete", "Recover", "Backup", "Restore"
  ]

  secret_permissions = [
    "Get", "List", "Set", "Delete", "Recover", "Backup", "Restore"
  ]

  certificate_permissions = [
    "Get", "List", "Update", "Create", "Import", "Delete", "Recover", "Backup", "Restore"
  ]
}

# Storage account role assignments
resource "azurerm_role_assignment" "platform_admins_storage" {
  count                = var.enable_storage_role_assignments ? 1 : 0
  scope                = var.storage_account_id
  role_definition_name = "Storage Account Contributor"
  principal_id         = azuread_group.platform_admins.object_id
}

resource "azurerm_role_assignment" "developers_storage" {
  count                = var.enable_storage_role_assignments ? 1 : 0
  scope                = var.storage_account_id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azuread_group.developers.object_id
}

resource "azurerm_role_assignment" "devops_engineers_storage" {
  count                = var.enable_storage_role_assignments ? 1 : 0
  scope                = var.storage_account_id
  role_definition_name = "Storage Account Contributor"
  principal_id         = azuread_group.devops_engineers.object_id
}

# ACR role assignments
resource "azurerm_role_assignment" "platform_admins_acr" {
  count                = var.enable_acr_role_assignments ? 1 : 0
  scope                = var.acr_id
  role_definition_name = "AcrPush"
  principal_id         = azuread_group.platform_admins.object_id
}

resource "azurerm_role_assignment" "developers_acr" {
  count                = var.enable_acr_role_assignments ? 1 : 0
  scope                = var.acr_id
  role_definition_name = "AcrPull"
  principal_id         = azuread_group.developers.object_id
}

resource "azurerm_role_assignment" "devops_engineers_acr" {
  count                = var.enable_acr_role_assignments ? 1 : 0
  scope                = var.acr_id
  role_definition_name = "AcrPush"
  principal_id         = azuread_group.devops_engineers.object_id
}

# Conditional resource group level assignments
resource "azurerm_role_assignment" "platform_admins_resource_groups" {
  for_each             = toset(var.resource_group_ids)
  scope                = each.value
  role_definition_name = azurerm_role_definition.platform_admin.name
  principal_id         = azuread_group.platform_admins.object_id
}

resource "azurerm_role_assignment" "developers_resource_groups" {
  for_each             = toset(var.resource_group_ids)
  scope                = each.value
  role_definition_name = azurerm_role_definition.developer.name
  principal_id         = azuread_group.developers.object_id
}

resource "azurerm_role_assignment" "devops_engineers_resource_groups" {
  for_each             = toset(var.resource_group_ids)
  scope                = each.value
  role_definition_name = azurerm_role_definition.devops_engineer.name
  principal_id         = azuread_group.devops_engineers.object_id
}

resource "azurerm_role_assignment" "security_auditors_resource_groups" {
  for_each             = toset(var.resource_group_ids)
  scope                = each.value
  role_definition_name = azurerm_role_definition.security_auditor.name
  principal_id         = azuread_group.security_auditors.object_id
}