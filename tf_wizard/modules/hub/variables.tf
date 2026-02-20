# Hub Module Variables

variable "hub_resource_group_name" {
  description = "Name of the hub resource group"
  type        = string
}

variable "location" {
  description = "Azure region for resources"
  type        = string
}

variable "hub_vnet_name" {
  description = "Name of the hub virtual network"
  type        = string
}

variable "hub_address_space" {
  description = "Address space for the hub VNET"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# Gateway Configuration
variable "enable_vpn_gateway" {
  description = "Enable VPN Gateway in hub"
  type        = bool
  default     = false
}

variable "enable_expressroute" {
  description = "Enable ExpressRoute Gateway in hub"
  type        = bool
  default     = false
}

variable "gateway_subnet_prefixes" {
  description = "Address prefixes for GatewaySubnet"
  type        = list(string)
  default     = ["10.0.0.0/24"]
}

variable "vpn_gateway_name" {
  description = "Name of the VPN Gateway"
  type        = string
  default     = "vpn-gateway"
}

variable "vpn_gateway_sku" {
  description = "SKU for VPN Gateway"
  type        = string
  default     = "VpnGw1"
}

variable "vpn_active_active" {
  description = "Enable active-active mode for VPN Gateway"
  type        = bool
  default     = false
}

variable "expressroute_gateway_name" {
  description = "Name of the ExpressRoute Gateway"
  type        = string
  default     = "expressroute-gateway"
}

variable "expressroute_gateway_sku" {
  description = "SKU for ExpressRoute Gateway"
  type        = string
  default     = "ErGw1AZ"
}

# Firewall Configuration
variable "enable_firewall" {
  description = "Enable Azure Firewall in hub"
  type        = bool
  default     = true
}

variable "firewall_name" {
  description = "Name of the Azure Firewall"
  type        = string
  default     = "hub-firewall"
}

variable "firewall_subnet_prefixes" {
  description = "Address prefixes for AzureFirewallSubnet"
  type        = list(string)
  default     = ["10.0.1.0/24"]
}

# Bastion Configuration
variable "enable_bastion" {
  description = "Enable Azure Bastion in hub"
  type        = bool
  default     = true
}

variable "bastion_name" {
  description = "Name of the Azure Bastion"
  type        = string
  default     = "hub-bastion"
}

variable "bastion_subnet_prefixes" {
  description = "Address prefixes for AzureBastionSubnet"
  type        = list(string)
  default     = ["10.0.2.0/24"]
}

# Shared Services Configuration
variable "shared_services_subnet_name" {
  description = "Name of the shared services subnet"
  type        = string
  default     = "shared-services"
}

variable "shared_services_subnet_prefixes" {
  description = "Address prefixes for shared services subnet"
  type        = list(string)
  default     = ["10.0.3.0/24"]
}

# DNS Forwarder Configuration
variable "enable_dns_forwarder" {
  description = "Enable DNS forwarder VM in hub"
  type        = bool
  default     = false
}

variable "dns_subnet_name" {
  description = "Name of the DNS subnet"
  type        = string
  default     = "dns"
}

variable "dns_subnet_prefixes" {
  description = "Address prefixes for DNS subnet"
  type        = list(string)
  default     = ["10.0.4.0/24"]
}

variable "dns_forwarder_name" {
  description = "Name of the DNS forwarder VM"
  type        = string
  default     = "dns-forwarder"
}

variable "dns_forwarder_size" {
  description = "VM size for DNS forwarder"
  type        = string
  default     = "Standard_B2s"
}

variable "dns_forwarder_admin_username" {
  description = "Admin username for DNS forwarder VM"
  type        = string
  default     = "azureuser"
}

variable "dns_forwarder_ssh_key" {
  description = "SSH public key for DNS forwarder VM"
  type        = string
}