variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region where Key Vault will be created"
  type        = string
}

variable "keyvault_name" {
  description = "Key Vault name (3-24 characters)"
  type        = string
  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9-]{1,22}[a-zA-Z0-9]$", var.keyvault_name))
    error_message = "Key Vault name must be 3-24 characters, start with a letter, and contain only letters, numbers, and hyphens."
  }
}

variable "sku_name" {
  description = "SKU name for Key Vault (standard or premium)"
  type        = string
  default     = "standard"
  validation {
    condition     = contains(["standard", "premium"], var.sku_name)
    error_message = "SKU must be either standard or premium."
  }
}

variable "enabled_for_deployment" {
  description = "Enable Key Vault for Azure VM deployment"
  type        = bool
  default     = false
}

variable "enabled_for_disk_encryption" {
  description = "Enable Key Vault for Azure Disk Encryption"
  type        = bool
  default     = true
}

variable "enabled_for_template_deployment" {
  description = "Enable Key Vault for ARM template deployment"
  type        = bool
  default     = true
}

variable "enable_rbac_authorization" {
  description = "Use RBAC for Key Vault authorization instead of access policies"
  type        = bool
  default     = false
}

variable "purge_protection_enabled" {
  description = "Enable purge protection (cannot be disabled once enabled)"
  type        = bool
  default     = true
}

variable "soft_delete_retention_days" {
  description = "Soft delete retention period in days"
  type        = number
  default     = 90
  validation {
    condition     = var.soft_delete_retention_days >= 7 && var.soft_delete_retention_days <= 90
    error_message = "Soft delete retention days must be between 7 and 90."
  }
}

variable "access_policies" {
  description = "Access policies for Key Vault"
  type = list(object({
    object_id               = string
    tenant_id               = string
    key_permissions         = optional(list(string), [])
    secret_permissions      = optional(list(string), [])
    certificate_permissions = optional(list(string), [])
  }))
  default = []
}

variable "network_acls" {
  description = "Network ACLs for Key Vault"
  type = object({
    default_action             = string
    bypass                     = string
    ip_rules                   = list(string)
    virtual_network_subnet_ids = list(string)
  })
  default = {
    default_action             = "Allow"
    bypass                     = "AzureServices"
    ip_rules                   = []
    virtual_network_subnet_ids = []
  }
}

variable "secrets" {
  description = "Secrets to store in Key Vault (values should be from secure sources)"
  type        = map(string)
  default     = {}
  sensitive   = true
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}
