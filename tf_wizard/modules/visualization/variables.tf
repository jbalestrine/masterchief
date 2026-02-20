# Visualization Module Variables

variable "hub_resource_group_name" {
  description = "Name of the hub resource group"
  type        = string
}

variable "hub_vnet_name" {
  description = "Name of the hub virtual network"
  type        = string
}

variable "hub_address_space" {
  description = "Address space for the hub VNET"
  type        = list(string)
}

variable "spoke_resource_groups" {
  description = "List of spoke resource group names"
  type        = list(string)
  default     = []
}

variable "spoke_vnets" {
  description = "List of spoke VNET configurations"
  type = list(object({
    name            = string
    resource_group  = string
    address_space   = list(string)
  }))
  default = []
}

variable "enable_aks" {
  description = "Enable AKS clusters"
  type        = bool
  default     = true
}

variable "aks_clusters" {
  description = "List of AKS cluster configurations"
  type = list(object({
    name                = string
    resource_group      = string
    node_count          = number
    kubernetes_version  = string
  }))
  default = []
}

variable "enable_app_gateway" {
  description = "Enable Application Gateway"
  type        = bool
  default     = false
}

variable "enable_storage" {
  description = "Enable storage account"
  type        = bool
  default     = true
}

variable "enable_key_vault" {
  description = "Enable Key Vault"
  type        = bool
  default     = true
}

variable "enable_acr" {
  description = "Enable Azure Container Registry"
  type        = bool
  default     = true
}

variable "enable_monitoring" {
  description = "Enable monitoring"
  type        = bool
  default     = true
}

variable "user_groups" {
  description = "List of user groups"
  type        = list(string)
  default     = []
}

variable "custom_roles" {
  description = "List of custom roles"
  type        = list(string)
  default     = []
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "tenant_id" {
  description = "Azure tenant ID"
  type        = string
}

variable "tags" {
  description = "Tags applied to resources"
  type        = map(string)
  default     = {}
}

variable "enable_static_website" {
  description = "Enable static website hosting"
  type        = bool
  default     = false
}