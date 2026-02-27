output "vnet_id" {
  description = "Virtual network resource ID"
  value       = azurerm_virtual_network.vnet.id
}

output "vnet_name" {
  description = "Virtual network name"
  value       = azurerm_virtual_network.vnet.name
}

output "vnet_location" {
  description = "Virtual network location"
  value       = azurerm_virtual_network.vnet.location
}

output "vnet_address_space" {
  description = "Virtual network address space"
  value       = azurerm_virtual_network.vnet.address_space
}

output "subnet_ids" {
  description = "Map of subnet names to their resource IDs"
  value       = { for k, v in azurerm_subnet.subnets : k => v.id }
}

output "subnet_address_prefixes" {
  description = "Map of subnet names to their address prefixes"
  value       = { for k, v in azurerm_subnet.subnets : k => v.address_prefixes }
}

output "nsg_ids" {
  description = "Map of NSG names to their resource IDs"
  value       = { for k, v in azurerm_network_security_group.nsgs : k => v.id }
}

output "nsg_names" {
  description = "Map of subnet names to their NSG names"
  value       = { for k, v in azurerm_network_security_group.nsgs : k => v.name }
}
