# Visualization Module Outputs

output "architecture_diagram_path" {
  description = "Path to the generated architecture diagram file"
  value       = local_file.architecture_diagram.filename
}

output "infrastructure_documentation_path" {
  description = "Path to the generated infrastructure documentation file"
  value       = local_file.infrastructure_doc.filename
}

output "deployment_guide_path" {
  description = "Path to the generated deployment guide file"
  value       = local_file.deployment_guide.filename
}

output "security_overview_path" {
  description = "Path to the generated security overview file"
  value       = local_file.security_overview.filename
}

output "cost_estimation_path" {
  description = "Path to the generated cost estimation file"
  value       = local_file.cost_estimation.filename
}

output "generated_files" {
  description = "List of all generated documentation files"
  value = [
    local_file.architecture_diagram.filename,
    local_file.infrastructure_doc.filename,
    local_file.deployment_guide.filename,
    local_file.security_overview.filename,
    local_file.cost_estimation.filename
  ]
}

output "architecture_summary" {
  description = "Summary of the architecture components"
  value = {
    hub_components = {
      resource_group = var.hub_resource_group_name
      vnet = var.hub_vnet_name
      address_space = var.hub_address_space
    }
    spoke_components = {
      resource_groups = var.spoke_resource_groups
      vnets = length(var.spoke_vnets)
      aks_clusters = var.enable_aks ? length(var.aks_clusters) : 0
    }
    security_components = {
      app_gateway = var.enable_app_gateway
      key_vault = var.enable_key_vault
      storage = var.enable_storage
      acr = var.enable_acr
    }
    monitoring = var.enable_monitoring
    user_management = {
      groups = length(var.user_groups)
      roles = length(var.custom_roles)
    }
  }
}