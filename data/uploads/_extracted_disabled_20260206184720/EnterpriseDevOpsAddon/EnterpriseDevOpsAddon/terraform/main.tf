resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

module "network" {
  source              = "./modules/network"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  tags                = var.tags
  address_space       = local.address_space
  app_subnet          = local.app_subnet
  sofs_subnet         = local.sofs_subnet
}

module "keyvault" {
  source              = "./modules/keyvault"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  tags                = var.tags
}

module "compute" {
  source              = "./modules/compute"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  admin_username      = var.admin_username
  admin_password      = var.admin_password
  subnet_id           = module.network.app_subnet_id
  vm_size             = local.web_vm_size
  tags                = var.tags
}

module "sql" {
  source              = "./modules/sql"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  admin_user          = var.sql_admin_user
  admin_password      = var.sql_admin_password
  tags                = var.tags
}

module "monitoring" {
  source              = "./modules/monitoring"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  tags                = var.tags
}
