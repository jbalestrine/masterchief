variable "name_prefix" { type = string }
variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "node_count" { type = number }
variable "node_size" { type = string }
variable "enable_aad" { type = bool }
variable "enable_autoscaler" { type = bool }
variable "min_node_count" { type = number }
variable "max_node_count" { type = number }

resource "azurerm_kubernetes_cluster" "this" {
    name                = "${var.name_prefix}-aks"
    location            = var.location
    resource_group_name = var.resource_group_name

    api_server_authorized_ip_ranges = []

    default_node_pool {
        name       = "default"
        node_count = var.node_count
        vm_size    = var.node_size
        max_pods   = 110
        enable_auto_scaling = var.enable_autoscaler
        min_count = var.min_node_count
        max_count = var.max_node_count
    }

    identity {
        type = "SystemAssigned"
    }

    network_profile {
        network_plugin = "azure"
        network_policy = "azure"
        dns_service_ip = "10.0.0.10"
        service_cidr    = "10.0.0.0/16"
        docker_bridge_cidr = "172.17.0.1/16"
    }

    role_based_access_control {
        enabled = true
    }

    addon_profile {
        oms_agent {
            enabled = true
            log_analytics_workspace_id = var.log_analytics_workspace_id
        }
        azure_policy {
            enabled = true
        }
    }

    azure_active_directory_role_based_access_control {
        managed = var.enable_aad
    }

    tags = {
        ManagedBy = "masterchief"
    }
}

output "aks_cluster_name" { value = azurerm_kubernetes_cluster.this.name }
output "aks_kube_config" { value = azurerm_kubernetes_cluster.this.kube_admin_config_raw }
