# Hub Module Outputs

output "hub_resource_group_name" {
  description = "Name of the hub resource group"
  value       = azurerm_resource_group.hub.name
}

output "hub_resource_group_id" {
  description = "ID of the hub resource group"
  value       = azurerm_resource_group.hub.id
}

output "hub_vnet_name" {
  description = "Name of the hub virtual network"
  value       = azurerm_virtual_network.hub.name
}

output "hub_vnet_id" {
  description = "ID of the hub virtual network"
  value       = azurerm_virtual_network.hub.id
}

output "hub_vnet_address_space" {
  description = "Address space of the hub virtual network"
  value       = azurerm_virtual_network.hub.address_space
}

output "gateway_subnet_id" {
  description = "ID of the GatewaySubnet"
  value       = var.enable_vpn_gateway || var.enable_expressroute ? azurerm_subnet.gateway[0].id : null
}

output "firewall_subnet_id" {
  description = "ID of the AzureFirewallSubnet"
  value       = var.enable_firewall ? azurerm_subnet.firewall[0].id : null
}

output "bastion_subnet_id" {
  description = "ID of the AzureBastionSubnet"
  value       = var.enable_bastion ? azurerm_subnet.bastion[0].id : null
}

output "shared_services_subnet_id" {
  description = "ID of the shared services subnet"
  value       = azurerm_subnet.shared_services.id
}

output "dns_subnet_id" {
  description = "ID of the DNS subnet"
  value       = var.enable_dns_forwarder ? azurerm_subnet.dns[0].id : null
}

output "firewall_private_ip" {
  description = "Private IP of the Azure Firewall"
  value       = var.enable_firewall ? azurerm_firewall.hub[0].ip_configuration[0].private_ip_address : null
}

output "firewall_public_ip" {
  description = "Public IP of the Azure Firewall"
  value       = var.enable_firewall ? azurerm_public_ip.firewall[0].ip_address : null
}

output "bastion_public_ip" {
  description = "Public IP of the Azure Bastion"
  value       = var.enable_bastion ? azurerm_public_ip.bastion[0].ip_address : null
}

output "vpn_gateway_id" {
  description = "ID of the VPN Gateway"
  value       = var.enable_vpn_gateway ? azurerm_virtual_network_gateway.vpn[0].id : null
}

output "expressroute_gateway_id" {
  description = "ID of the ExpressRoute Gateway"
  value       = var.enable_expressroute ? azurerm_virtual_network_gateway.expressroute[0].id : null
}

output "dns_forwarder_private_ip" {
  description = "Private IP of the DNS forwarder VM"
  value       = var.enable_dns_forwarder ? azurerm_network_interface.dns_forwarder[0].private_ip_address : null
}