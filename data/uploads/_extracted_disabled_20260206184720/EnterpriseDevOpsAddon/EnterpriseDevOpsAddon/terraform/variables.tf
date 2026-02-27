variable "location" {
  type    = string
  default = "eastus"
}

variable "resource_group_name" {
  type    = string
  default = "EnterpriseAppRG"
}

variable "admin_username" {
  type = string
}

variable "admin_password" {
  type      = string
  sensitive = true
}

variable "sql_admin_user" {
  type = string
}

variable "sql_admin_password" {
  type      = string
  sensitive = true
}

variable "tags" {
  type = map(string)
  default = {
    Environment = "Production"
    Owner       = "EnterpriseIT"
    CostCenter  = "IT-Apps"
    Compliance  = "ISO27001"
  }
}
