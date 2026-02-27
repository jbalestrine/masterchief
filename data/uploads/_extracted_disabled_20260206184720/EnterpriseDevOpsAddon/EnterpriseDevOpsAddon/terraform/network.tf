resource "azurerm_virtual_network" "vnet" {
  name                = "EnterpriseVNet"
  address_space       = var.address_space
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

resource "azurerm_subnet" "app" {
  name                 = "AppSubnet"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [var.app_subnet]
}

output "app_subnet_id" {
  value = azurerm_subnet.app.id
}
