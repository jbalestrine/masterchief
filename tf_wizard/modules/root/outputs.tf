# Root Module Outputs

# Hub Outputs
output "hub_resource_group_name" {
  description = "Name of the hub resource group"
  value       = module.hub.hub_resource_group_name
}

output "hub_resource_group_id" {
  description = "ID of the hub resource group"
  value       = module.hub.hub_resource_group_id
}

output "hub_vnet_id" {
  description = "ID of the hub virtual network"
  value       = module.hub.hub_vnet_id
}

output "hub_vnet_name" {
  description = "Name of the hub virtual network"
  value       = module.hub.hub_vnet_name
}

output "hub_vnet_address_space" {
  description = "Address space of the hub virtual network"
  value       = module.hub.hub_vnet_address_space
}

output "firewall_id" {
  description = "ID of the Azure Firewall"
  value       = module.hub.firewall_id
}

output "firewall_name" {
  description = "Name of the Azure Firewall"
  value       = module.hub.firewall_name
}

output "firewall_private_ip" {
  description = "Private IP of the Azure Firewall"
  value       = module.hub.firewall_private_ip
}

output "vpn_gateway_id" {
  description = "ID of the VPN Gateway"
  value       = module.hub.vpn_gateway_id
}

output "vpn_gateway_name" {
  description = "Name of the VPN Gateway"
  value       = module.hub.vpn_gateway_name
}

output "bastion_id" {
  description = "ID of the Azure Bastion"
  value       = module.hub.bastion_id
}

output "bastion_name" {
  description = "Name of the Azure Bastion"
  value       = module.hub.bastion_name
}

# Spoke Outputs
output "spoke_resource_groups" {
  description = "Map of spoke resource groups"
  value = {
    for k, v in module.spokes : k => {
      name = v.spoke_resource_group_name
      id   = v.spoke_resource_group_id
    }
  }
}

output "spoke_vnets" {
  description = "Map of spoke virtual networks"
  value = {
    for k, v in module.spokes : k => {
      name           = v.spoke_vnet_name
      id             = v.spoke_vnet_id
      address_space  = v.spoke_vnet_address_space
    }
  }
}

output "aks_clusters" {
  description = "Map of AKS clusters"
  value = {
    for k, v in module.spokes : k => {
      cluster_name     = v.aks_cluster_name
      cluster_id       = v.aks_cluster_id
      kube_config      = v.aks_kube_config
      node_resource_group = v.aks_node_resource_group
    } if v.aks_cluster_id != null
  }
}

output "application_gateways" {
  description = "Map of Application Gateways"
  value = {
    for k, v in module.spokes : k => {
      id             = v.appgw_id
      name           = v.appgw_name
      public_ip      = v.appgw_public_ip_address
      public_fqdn    = v.appgw_public_ip_fqdn
    } if v.appgw_id != null
  }
}

output "storage_accounts" {
  description = "Map of storage accounts"
  value = {
    for k, v in module.spokes : k => {
      name                 = v.storage_account_name
      id                   = v.storage_account_id
      primary_connection_string = v.storage_account_primary_connection_string
      primary_access_key   = v.storage_account_primary_access_key
      primary_blob_endpoint = v.storage_account_primary_blob_endpoint
      primary_web_endpoint = v.storage_account_primary_web_endpoint
    } if v.storage_account_id != null
  }
}

output "key_vaults" {
  description = "Map of Key Vaults"
  value = {
    for k, v in module.spokes : k => {
      name = v.key_vault_name
      id   = v.key_vault_id
      uri  = v.key_vault_uri
    } if v.key_vault_id != null
  }
}

output "container_registries" {
  description = "Map of Azure Container Registries"
  value = {
    for k, v in module.spokes : k => {
      name          = v.acr_name
      id            = v.acr_id
      login_server = v.acr_login_server
      admin_username = v.acr_admin_username
      admin_password = v.acr_admin_password
    } if v.acr_id != null
  }
}

# User Management Outputs
output "user_groups" {
  description = "Map of created user groups"
  value = {
    platform_admins    = module.user_management.platform_admins_group_id
    developers         = module.user_management.developers_group_id
    devops_engineers   = module.user_management.devops_engineers_group_id
    security_auditors  = module.user_management.security_auditors_group_id
    end_users          = module.user_management.end_users_group_id
  }
}

output "custom_roles" {
  description = "Map of custom roles"
  value = {
    platform_admin     = module.user_management.platform_admin_role_id
    developer          = module.user_management.developer_role_id
    devops_engineer    = module.user_management.devops_engineer_role_id
    security_auditor   = module.user_management.security_auditor_role_id
  }
}

output "role_assignments" {
  description = "List of role assignment IDs"
  value       = module.user_management.role_assignments
}

# Visualization Outputs
output "documentation_files" {
  description = "Paths to generated documentation files"
  value = {
    architecture_diagram    = module.visualization.architecture_diagram_path
    infrastructure_doc      = module.visualization.infrastructure_documentation_path
    deployment_guide        = module.visualization.deployment_guide_path
    security_overview       = module.visualization.security_overview_path
    cost_estimation         = module.visualization.cost_estimation_path
  }
}

output "architecture_summary" {
  description = "Summary of the deployed architecture"
  value       = module.visualization.architecture_summary
}

# VNET Peering Outputs
output "vnet_peerings" {
  description = "Map of VNET peerings"
  value = {
    for k, v in module.spokes : k => {
      hub_to_spoke = v.hub_to_spoke_peering_id
      spoke_to_hub = v.spoke_to_hub_peering_id
    }
  }
}

# Network Security Outputs
output "network_security" {
  description = "Network security configuration summary"
  value = {
    hub_firewall = {
      id   = module.hub.firewall_id
      name = module.hub.firewall_name
      ip   = module.hub.firewall_private_ip
    }
    bastion = {
      id   = module.hub.bastion_id
      name = module.hub.bastion_name
    }
  }
}

# Monitoring Outputs
output "monitoring_workspaces" {
  description = "Map of Log Analytics workspaces"
  value = {
    for k, v in module.spokes : k => {
      id   = v.log_analytics_workspace_id
      name = v.log_analytics_workspace_name
    } if v.log_analytics_workspace_id != null
  }
}

# Complete Infrastructure Summary
output "infrastructure_summary" {
  description = "Complete summary of deployed infrastructure"
  value = {
    hub = {
      resource_group = module.hub.hub_resource_group_name
      vnet = module.hub.hub_vnet_name
      firewall = module.hub.firewall_name
      bastion = module.hub.bastion_name
      vpn_gateway = module.hub.vpn_gateway_name
    }
    spokes = {
      for k, v in module.spokes : k => {
        resource_group = v.spoke_resource_group_name
        vnet = v.spoke_vnet_name
        aks = v.aks_cluster_name
        storage = v.storage_account_name
        key_vault = v.key_vault_name
        acr = v.acr_name
      }
    }
    user_management = {
      groups_created = length(module.user_management.all_groups)
      roles_created = length(module.user_management.all_custom_roles)
    }
    documentation = module.visualization.generated_files
  }
}