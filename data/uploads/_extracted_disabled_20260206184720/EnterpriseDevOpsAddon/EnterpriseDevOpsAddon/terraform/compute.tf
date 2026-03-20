resource "azurerm_windows_virtual_machine" "web" {
  name                = "EnterpriseWebVM"
  location            = var.location
  resource_group_name = var.resource_group_name
  size                = var.vm_size
  admin_username      = var.admin_username
  admin_password      = var.admin_password
  network_interface_ids = [azurerm_network_interface.nic.id]
  tags                = var.tags
}

resource "azurerm_virtual_machine_extension" "dsc" {
  name                 = "IIS-DSC"
  virtual_machine_id   = azurerm_windows_virtual_machine.web.id
  publisher            = "Microsoft.Powershell"
  type                 = "DSC"
  type_handler_version = "2.83"

  settings = jsonencode({
    configuration = {
      url      = "https://yourblob/dsc-iis.zip"
      script   = "dsc-iis.ps1"
      function = "EnterpriseWebIIS"
    }
  })
}
