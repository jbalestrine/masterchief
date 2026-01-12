variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region where AKS cluster will be created"
  type        = string
}

variable "cluster_name" {
  description = "Name of the AKS cluster"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = null
}

variable "dns_prefix" {
  description = "DNS prefix for the AKS cluster"
  type        = string
  default     = null
}

variable "subnet_id" {
  description = "ID of the subnet where AKS nodes will be deployed"
  type        = string
}

variable "default_node_pool" {
  description = "Configuration for the default node pool"
  type = object({
    name                = string
    vm_size             = string
    node_count          = number
    enable_auto_scaling = bool
    min_count           = optional(number)
    max_count           = optional(number)
    os_disk_size_gb     = optional(number, 128)
    max_pods            = optional(number, 30)
    availability_zones  = optional(list(string), [])
  })
  default = {
    name                = "default"
    vm_size             = "Standard_D2s_v3"
    node_count          = 3
    enable_auto_scaling = true
    min_count           = 2
    max_count           = 5
    os_disk_size_gb     = 128
    max_pods            = 30
    availability_zones  = ["1", "2", "3"]
  }
}

variable "additional_node_pools" {
  description = "Additional node pools to create"
  type = map(object({
    vm_size             = string
    node_count          = number
    enable_auto_scaling = bool
    min_count           = optional(number)
    max_count           = optional(number)
    os_disk_size_gb     = optional(number, 128)
    max_pods            = optional(number, 30)
    node_taints         = optional(list(string), [])
    node_labels         = optional(map(string), {})
    availability_zones  = optional(list(string), [])
  }))
  default = {}
}

variable "network_plugin" {
  description = "Network plugin to use (azure or kubenet)"
  type        = string
  default     = "azure"
  validation {
    condition     = contains(["azure", "kubenet"], var.network_plugin)
    error_message = "Network plugin must be either 'azure' or 'kubenet'."
  }
}

variable "network_policy" {
  description = "Network policy to use (azure or calico)"
  type        = string
  default     = "azure"
}

variable "service_cidr" {
  description = "CIDR for Kubernetes services"
  type        = string
  default     = "10.240.0.0/16"
}

variable "dns_service_ip" {
  description = "IP address for Kubernetes DNS service"
  type        = string
  default     = "10.240.0.10"
}

variable "enable_rbac" {
  description = "Enable Kubernetes RBAC"
  type        = bool
  default     = true
}

variable "enable_azure_rbac" {
  description = "Enable Azure RBAC for Kubernetes authorization"
  type        = bool
  default     = false
}

variable "admin_group_object_ids" {
  description = "AAD group object IDs for cluster admin access"
  type        = list(string)
  default     = []
}

variable "enable_http_application_routing" {
  description = "Enable HTTP application routing addon"
  type        = bool
  default     = false
}

variable "enable_azure_policy" {
  description = "Enable Azure Policy addon"
  type        = bool
  default     = true
}

variable "enable_oms_agent" {
  description = "Enable OMS agent (Azure Monitor)"
  type        = bool
  default     = true
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics workspace ID for OMS agent"
  type        = string
  default     = null
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
