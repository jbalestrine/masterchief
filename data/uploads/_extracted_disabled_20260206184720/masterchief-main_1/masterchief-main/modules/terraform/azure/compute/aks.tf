# Azure Kubernetes Service (AKS) Cluster
# Part of MasterChief Enterprise DevOps Platform

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}

variable "cluster_name" {
  description = "Name of the AKS cluster"
  type        = string
}

variable "dns_prefix" {
  description = "DNS prefix for the cluster"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.27"
}

variable "default_node_pool" {
  description = "Default node pool configuration"
  type = object({
    name                = string
    node_count          = number
    vm_size             = string
    availability_zones  = list(string)
    enable_auto_scaling = bool
    min_count           = optional(number)
    max_count           = optional(number)
  })
  default = {
    name                = "default"
    node_count          = 3
    vm_size             = "Standard_D4s_v3"
    availability_zones  = ["1", "2", "3"]
    enable_auto_scaling = true
    min_count           = 3
    max_count           = 10
  }
}

variable "additional_node_pools" {
  description = "Additional node pools"
  type = map(object({
    vm_size             = string
    node_count          = number
    availability_zones  = list(string)
    enable_auto_scaling = bool
    min_count           = optional(number)
    max_count           = optional(number)
    node_labels         = optional(map(string))
    node_taints         = optional(list(string))
  }))
  default = {}
}

variable "network_plugin" {
  description = "Network plugin (azure or kubenet)"
  type        = string
  default     = "azure"
}

variable "subnet_id" {
  description = "Subnet ID for the cluster"
  type        = string
}

variable "enable_rbac" {
  description = "Enable Kubernetes RBAC"
  type        = bool
  default     = true
}

variable "enable_azure_policy" {
  description = "Enable Azure Policy for AKS"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.cluster_name
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = var.dns_prefix
  kubernetes_version  = var.kubernetes_version

  default_node_pool {
    name                = var.default_node_pool.name
    node_count          = var.default_node_pool.node_count
    vm_size             = var.default_node_pool.vm_size
    availability_zones  = var.default_node_pool.availability_zones
    enable_auto_scaling = var.default_node_pool.enable_auto_scaling
    min_count           = var.default_node_pool.min_count
    max_count           = var.default_node_pool.max_count
    vnet_subnet_id      = var.subnet_id
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = var.network_plugin
    load_balancer_sku = "standard"
    network_policy    = "azure"
  }

  azure_policy_enabled = var.enable_azure_policy
  
  role_based_access_control_enabled = var.enable_rbac

  tags = merge(
    var.tags,
    {
      "ManagedBy" = "MasterChief"
      "Module"    = "terraform-azure-aks"
    }
  )
}

# Additional Node Pools
resource "azurerm_kubernetes_cluster_node_pool" "additional" {
  for_each = var.additional_node_pools

  name                  = each.key
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks.id
  vm_size               = each.value.vm_size
  node_count            = each.value.node_count
  availability_zones    = each.value.availability_zones
  enable_auto_scaling   = each.value.enable_auto_scaling
  min_count             = each.value.min_count
  max_count             = each.value.max_count
  vnet_subnet_id        = var.subnet_id
  node_labels           = each.value.node_labels
  node_taints           = each.value.node_taints

  tags = merge(
    var.tags,
    {
      "ManagedBy" = "MasterChief"
      "NodePool"  = each.key
    }
  )
}

# Outputs
output "cluster_id" {
  description = "ID of the AKS cluster"
  value       = azurerm_kubernetes_cluster.aks.id
}

output "cluster_name" {
  description = "Name of the AKS cluster"
  value       = azurerm_kubernetes_cluster.aks.name
}

output "kube_config" {
  description = "Kubernetes configuration"
  value       = azurerm_kubernetes_cluster.aks.kube_config_raw
  sensitive   = true
}

output "cluster_fqdn" {
  description = "FQDN of the cluster"
  value       = azurerm_kubernetes_cluster.aks.fqdn
}

output "identity_principal_id" {
  description = "Principal ID of the cluster identity"
  value       = azurerm_kubernetes_cluster.aks.identity[0].principal_id
}
