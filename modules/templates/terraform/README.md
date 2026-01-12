# Terraform Module Template

This template provides the standard structure for Terraform modules.

## Structure

```
module-name/
├── module.yaml          # Module manifest
├── main.tf              # Main resource definitions
├── variables.tf         # Input variables
├── outputs.tf           # Output values
├── versions.tf          # Provider version constraints
├── README.md            # Module documentation
└── examples/            # Usage examples
    └── basic/
        ├── main.tf
        └── variables.tf
```

## Usage

1. Copy this template directory
2. Rename to your module name
3. Update module.yaml with your module metadata
4. Define resources in main.tf
5. Define variables in variables.tf
6. Define outputs in outputs.tf
7. Update README.md with usage instructions

## Naming Conventions

- Use lowercase with hyphens for module names: `azure-vnet`, `aks-cluster`
- Use snake_case for Terraform variables and resources
- Prefix Azure resources with service type: `rg_`, `vnet_`, `aks_`

## Variable Conventions

All modules should support:
- `resource_group_name` - Target resource group
- `location` - Azure region
- `tags` - Resource tags (map)
- `environment` - Environment name (dev/staging/prod)

## Output Conventions

Return resource IDs and essential attributes:
- `<resource>_id` - Azure resource ID
- `<resource>_name` - Resource name
- `<resource>_location` - Resource location
