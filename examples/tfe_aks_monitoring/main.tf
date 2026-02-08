resource "azurerm_resource_group" "rg_tfe-aks-demo" {
  name = "rg-tfe-aks-demo"
  location = ${var.location}
}
