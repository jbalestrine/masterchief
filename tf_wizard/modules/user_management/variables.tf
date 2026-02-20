# User Management Module Variables

variable "scope" {
  description = "Scope for role assignments (subscription or resource group)"
  type        = string
}

variable "tenant_id" {
  description = "Azure tenant ID"
  type        = string
}

# Group Configuration
variable "group_owners" {
  description = "Object IDs of group owners"
  type        = list(string)
  default     = []
}

variable "platform_admins_group_name" {
  description = "Name of the platform administrators group"
  type        = string
  default     = "Platform-Administrators"
}

variable "platform_admins_members" {
  description = "Object IDs of platform administrators"
  type        = list(string)
  default     = []
}

variable "developers_group_name" {
  description = "Name of the developers group"
  type        = string
  default     = "Developers"
}

variable "developers_members" {
  description = "Object IDs of developers"
  type        = list(string)
  default     = []
}

variable "devops_engineers_group_name" {
  description = "Name of the DevOps engineers group"
  type        = string
  default     = "DevOps-Engineers"
}

variable "devops_engineers_members" {
  description = "Object IDs of DevOps engineers"
  type        = list(string)
  default     = []
}

variable "security_auditors_group_name" {
  description = "Name of the security auditors group"
  type        = string
  default     = "Security-Auditors"
}

variable "security_auditors_members" {
  description = "Object IDs of security auditors"
  type        = list(string)
  default     = []
}

variable "end_users_group_name" {
  description = "Name of the end users group"
  type        = string
  default     = "End-Users"
}

variable "end_users_members" {
  description = "Object IDs of end users"
  type        = list(string)
  default     = []
}

# Resource IDs for role assignments
variable "resource_group_ids" {
  description = "List of resource group IDs for role assignments"
  type        = list(string)
  default     = []
}

variable "aks_cluster_id" {
  description = "ID of the AKS cluster for role assignments"
  type        = string
  default     = ""
}

variable "key_vault_id" {
  description = "ID of the Key Vault for access policies"
  type        = string
  default     = ""
}

variable "storage_account_id" {
  description = "ID of the storage account for role assignments"
  type        = string
  default     = ""
}

variable "acr_id" {
  description = "ID of the Azure Container Registry for role assignments"
  type        = string
  default     = ""
}

# Feature toggles
variable "enable_aks_role_assignments" {
  description = "Enable AKS-specific role assignments"
  type        = bool
  default     = true
}

variable "enable_key_vault_access" {
  description = "Enable Key Vault access policies"
  type        = bool
  default     = true
}

variable "enable_storage_role_assignments" {
  description = "Enable storage account role assignments"
  type        = bool
  default     = true
}

variable "enable_acr_role_assignments" {
  description = "Enable ACR role assignments"
  type        = bool
  default     = true
}

# Custom role definitions
variable "create_custom_roles" {
  description = "Create custom role definitions"
  type        = bool
  default     = true
}

variable "platform_admin_role_permissions" {
  description = "Additional permissions for platform admin role"
  type = object({
    actions     = optional(list(string), [])
    not_actions = optional(list(string), [])
  })
  default = {
    actions     = []
    not_actions = []
  }
}

variable "developer_role_permissions" {
  description = "Additional permissions for developer role"
  type = object({
    actions     = optional(list(string), [])
    not_actions = optional(list(string), [])
  })
  default = {
    actions     = []
    not_actions = []
  }
}

variable "devops_engineer_role_permissions" {
  description = "Additional permissions for DevOps engineer role"
  type = object({
    actions     = optional(list(string), [])
    not_actions = optional(list(string), [])
  })
  default = {
    actions     = []
    not_actions = []
  }
}

variable "security_auditor_role_permissions" {
  description = "Additional permissions for security auditor role"
  type = object({
    actions     = optional(list(string), [])
    not_actions = optional(list(string), [])
  })
  default = {
    actions     = []
    not_actions = []
  }
}

# Azure AD Application Registration (for service principals)
variable "create_service_principals" {
  description = "Create service principals for automation"
  type        = bool
  default     = false
}

variable "service_principals" {
  description = "Service principal configurations"
  type = map(object({
    display_name = string
    description  = optional(string, "")
    owners       = optional(list(string), [])
  }))
  default = {}
}

# Conditional access policies
variable "create_conditional_access_policies" {
  description = "Create conditional access policies"
  type        = bool
  default     = false
}

variable "conditional_access_policies" {
  description = "Conditional access policy configurations"
  type = map(object({
    display_name   = string
    state          = string
    conditions     = any
    grant_controls = any
  }))
  default = {}
}

# PIM (Privileged Identity Management) settings
variable "enable_pim_assignments" {
  description = "Enable PIM assignments for elevated roles"
  type        = bool
  default     = false
}

variable "pim_assignments" {
  description = "PIM assignment configurations"
  type = map(object({
    principal_id         = string
    role_definition_name = string
    scope                = string
    justification        = string
    duration_hours       = number
  }))
  default = {}
}

# Tags
variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}