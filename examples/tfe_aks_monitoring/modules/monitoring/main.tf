variable "name_prefix" { type = string }
variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "target_resource_id" { type = string }

resource "azurerm_log_analytics_workspace" "law" {
    name                = "${var.name_prefix}-law"
    location            = var.location
    resource_group_name = var.resource_group_name
    sku                 = "PerGB2018"
}

resource "azurerm_monitor_diagnostic_setting" "diagnostics" {
    name                       = "${var.name_prefix}-diag"
    target_resource_id         = var.target_resource_id
    log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
    log {
        category = "Administrative"
        enabled  = true
        retention_policy { enabled = true, days = 30 }
    }
    metric {
        category = "AllMetrics"
        enabled  = true
        retention_policy { enabled = true, days = 30 }
    }
}

output "log_analytics_workspace_id" { value = azurerm_log_analytics_workspace.law.id }
output "monitoring_configured" { value = true }
