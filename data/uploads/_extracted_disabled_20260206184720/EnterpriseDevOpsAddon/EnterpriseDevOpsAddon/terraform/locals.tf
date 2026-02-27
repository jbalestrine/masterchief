locals {
  vnet_name       = "EnterpriseVNet"
  address_space   = ["10.0.0.0/16"]
  app_subnet      = "10.0.1.0/24"
  sofs_subnet     = "10.0.2.0/24"
  web_vm_size     = "Standard_D2s_v5"
  sofs_vm_size    = "Standard_D4s_v5"
}
