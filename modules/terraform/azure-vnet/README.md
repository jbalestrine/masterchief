# Azure Virtual Network Module

This module creates an Azure Virtual Network with subnets and Network Security Groups.

## Features

- Creates Virtual Network with configurable address space
- Creates multiple subnets with individual NSGs
- Supports subnet service endpoints
- Supports subnet delegations
- Automatic NSG association with subnets
- Configurable NSG security rules
- DDoS protection support
- Custom DNS servers support

## Usage

```hcl
module "vnet" {
  source = "../../modules/terraform/azure-vnet"

  resource_group_name = "rg-example"
  location            = "eastus"
  vnet_name           = "vnet-example"
  address_space       = ["10.0.0.0/16"]

  subnets = {
    "subnet-web" = {
      address_prefix    = "10.0.1.0/24"
      service_endpoints = ["Microsoft.Storage", "Microsoft.KeyVault"]
    }
    "subnet-app" = {
      address_prefix    = "10.0.2.0/24"
      service_endpoints = ["Microsoft.Sql"]
    }
    "subnet-data" = {
      address_prefix = "10.0.3.0/24"
    }
  }

  nsg_rules = {
    "subnet-web" = [
      {
        name                       = "allow-https"
        priority                   = 100
        direction                  = "Inbound"
        access                     = "Allow"
        protocol                   = "Tcp"
        source_port_range          = "*"
        destination_port_range     = "443"
        source_address_prefix      = "*"
        destination_address_prefix = "*"
      }
    ]
  }

  tags = {
    project     = "example"
    cost_center = "engineering"
  }

  environment = "dev"
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| resource_group_name | Resource group name | string | - | yes |
| location | Azure region | string | - | yes |
| vnet_name | Virtual network name | string | - | yes |
| address_space | VNet address space | list(string) | ["10.0.0.0/16"] | no |
| subnets | Subnet configurations | map(object) | {} | no |
| dns_servers | DNS servers | list(string) | [] | no |
| nsg_rules | NSG security rules | map(list(object)) | {} | no |
| tags | Resource tags | map(string) | {} | no |
| environment | Environment name | string | "dev" | no |

## Outputs

| Name | Description |
|------|-------------|
| vnet_id | Virtual network resource ID |
| vnet_name | Virtual network name |
| subnet_ids | Map of subnet IDs |
| nsg_ids | Map of NSG IDs |

## Examples

See the `examples/` directory for complete usage examples.
