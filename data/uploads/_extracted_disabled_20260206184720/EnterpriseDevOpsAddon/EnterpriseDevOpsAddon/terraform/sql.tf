resource "azurerm_mssql_server" "sql" {
  name                         = "enterprise-sql-server"
  resource_group_name          = var.resource_group_name
  location                     = var.location
  version                      = "12.0"
  administrator_login          = var.admin_user
  administrator_login_password = var.admin_password
  tags                          = var.tags
}

resource "azurerm_mssql_database" "db" {
  name      = "EnterpriseAppDB"
  server_id = azurerm_mssql_server.sql.id
  sku_name = "GP_S_Gen5_2"
}
