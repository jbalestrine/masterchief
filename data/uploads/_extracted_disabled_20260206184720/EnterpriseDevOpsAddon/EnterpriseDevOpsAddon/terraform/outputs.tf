output "resource_group" {
  value = azurerm_resource_group.rg.name
}

output "web_vm" {
  value = module.compute.vm_name
}

output "sql_server" {
  value = module.sql.server_name
}
