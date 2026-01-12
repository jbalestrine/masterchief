# Azure Kubernetes Service (AKS) Module

This module creates an Azure Kubernetes Service (AKS) cluster with configurable node pools.

## Features

- AKS cluster with system-assigned managed identity
- Configurable default node pool with auto-scaling
- Support for multiple additional node pools
- Azure CNI or Kubenet networking
- Azure RBAC integration
- Azure Policy addon
- Azure Monitor (OMS agent) integration
- Availability zones support
- Node pool taints and labels

## Usage

```hcl
module "aks" {
  source = "../../modules/terraform/azure-aks"

  resource_group_name = "rg-aks-example"
  location            = "eastus"
  cluster_name        = "aks-example"
  kubernetes_version  = "1.27.3"
  subnet_id           = module.vnet.subnet_ids["subnet-aks"]

  default_node_pool = {
    name                = "system"
    vm_size             = "Standard_D4s_v3"
    node_count          = 3
    enable_auto_scaling = true
    min_count           = 2
    max_count           = 5
    availability_zones  = ["1", "2", "3"]
  }

  additional_node_pools = {
    "user" = {
      vm_size             = "Standard_D8s_v3"
      node_count          = 2
      enable_auto_scaling = true
      min_count           = 1
      max_count           = 10
      node_labels = {
        workload = "user"
      }
    }
  }

  network_plugin = "azure"
  network_policy = "azure"

  enable_azure_policy = true
  enable_oms_agent    = true
  
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  admin_group_object_ids = [
    "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  ]

  tags = {
    project     = "example"
    cost_center = "engineering"
  }

  environment = "dev"
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| resource_group_name | Resource group name | string | - | yes |
| location | Azure region | string | - | yes |
| cluster_name | AKS cluster name | string | - | yes |
| subnet_id | Subnet ID for nodes | string | - | yes |
| kubernetes_version | Kubernetes version | string | null | no |
| default_node_pool | Default node pool config | object | see variables.tf | no |
| additional_node_pools | Additional node pools | map(object) | {} | no |
| network_plugin | Network plugin | string | "azure" | no |
| enable_azure_policy | Enable Azure Policy | bool | true | no |
| tags | Resource tags | map(string) | {} | no |

## Outputs

| Name | Description |
|------|-------------|
| cluster_id | AKS cluster resource ID |
| cluster_name | AKS cluster name |
| identity_principal_id | System-assigned identity principal ID |
| kube_config | Kubernetes configuration (sensitive) |

## Requirements

- Azure subscription
- Virtual network and subnet already created
- Optional: Log Analytics workspace for monitoring
