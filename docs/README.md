# MasterChief DevOps Automation Platform

A modular, extensible DevOps automation platform that enables continuous growth through plug-and-play components. The platform provides Infrastructure as Code (IaC) across multiple tools with a unified automation framework.

## Features

- **Modular Architecture**: Plug-and-play module system for easy extensibility
- **Multi-IaC Support**: Terraform, Ansible, and PowerShell DSC integrations
- **Azure Focus**: Comprehensive Azure resource modules
- **Configuration Management**: Environment-based configuration with inheritance
- **CI/CD Ready**: GitHub Actions workflows for validation and deployment
- **Extensible**: Plugin architecture for custom module types

## Quick Start

### Prerequisites

- Python 3.10+
- Terraform 1.5+
- Ansible 2.14+
- PowerShell 7+ (for DSC)
- Azure CLI (for Azure deployments)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/jbalestrine/masterchief.git
cd masterchief
```

2. Install Python dependencies:
```bash
pip install pyyaml
```

3. Configure your environment:
```bash
# Copy and edit environment configuration
cp core/config/dev.yaml core/config/myenv.yaml
# Edit myenv.yaml with your settings
```

### Using the CLI

The MasterChief CLI provides commands for managing modules and configurations:

```bash
# List all available modules
python scripts/python/masterchief.py list

# List Terraform modules only
python scripts/python/masterchief.py list --type terraform

# Show configuration for an environment
python scripts/python/masterchief.py config dev

# Validate a module
python scripts/python/masterchief.py validate modules/terraform/azure-vnet

# Initialize a new module
python scripts/python/masterchief.py init terraform my-new-module
```

## Architecture

```
masterchief/
├── core/                          # Core platform engine
│   ├── module_loader/            # Dynamic module loading
│   ├── config/                   # Configuration management
│   ├── logging/                  # Centralized logging
│   └── api/                      # Module communication API
├── modules/                      # Plug-and-play modules
│   ├── terraform/                # Terraform IaC modules
│   ├── ansible/                  # Ansible playbooks and roles
│   ├── powershell-dsc/          # PowerShell DSC configurations
│   └── templates/                # Module templates
├── pipelines/                    # CI/CD pipeline definitions
│   └── github-actions/          # GitHub Actions workflows
├── scripts/                      # Utility scripts
│   ├── python/                  # Python orchestration
│   ├── bash/                    # Bash automation
│   └── powershell/              # PowerShell automation
└── docs/                         # Documentation
```

## Available Modules

### Terraform Modules

#### Networking
- **azure-vnet**: Virtual Network with subnets, NSGs, and security rules
  - Configurable address spaces
  - Multiple subnets with individual NSGs
  - Service endpoints and delegations

#### Compute
- **azure-aks**: Azure Kubernetes Service cluster
  - Multi-node pool support
  - Auto-scaling configuration
  - Azure CNI networking
  - RBAC integration

#### Storage
- **azure-storage**: Storage Account with containers and file shares
  - Standard/Premium tiers
  - Multiple replication options
  - Blob versioning and change feed
  - Network rules and firewall

#### Security
- **azure-keyvault**: Key Vault for secrets management
  - Standard/Premium SKU
  - Access policies or RBAC
  - Soft delete and purge protection
  - Network ACLs

### Ansible Roles

- **common**: Base configuration for all Linux servers
  - Package management
  - User management
  - SSH configuration
  - System hardening

- **docker**: Docker installation and configuration
  - Docker CE installation
  - Docker Compose
  - Custom daemon configuration
  - User group management

### PowerShell DSC Configurations

- **CommonServer**: Base Windows server configuration
  - Time zone and power settings
  - Firewall configuration
  - Remote Desktop setup
  - Event log management

- **WebServer**: IIS web server configuration
  - IIS installation
  - App pool configuration
  - Website setup
  - Firewall rules

## Usage Examples

### Deploy Infrastructure with Terraform

```bash
cd modules/terraform/azure-vnet

# Initialize Terraform
terraform init

# Create terraform.tfvars
cat > terraform.tfvars << EOF
resource_group_name = "rg-example"
location            = "eastus"
vnet_name           = "vnet-example"
address_space       = ["10.0.0.0/16"]

subnets = {
  "subnet-web" = {
    address_prefix    = "10.0.1.0/24"
    service_endpoints = ["Microsoft.Storage"]
  }
}
EOF

# Plan and apply
terraform plan
terraform apply
```

### Configure Servers with Ansible

```bash
cd modules/ansible

# Test inventory
ansible-inventory -i inventory/azure_rm.yml --list

# Run playbook
ansible-playbook -i inventory/azure_rm.yml playbooks/site.yml

# Run for specific environment
ansible-playbook -i inventory/azure_rm.yml playbooks/site.yml --limit dev
```

### Apply DSC Configuration

```powershell
cd modules/powershell-dsc

# Compile configuration
.\scripts\Compile-Configuration.ps1 `
    -ConfigurationName "WebServer" `
    -OutputPath "C:\DSC\MOF" `
    -ComputerName "WEB01"

# Deploy configuration
.\scripts\Deploy-Configuration.ps1 `
    -MOFPath "C:\DSC\MOF" `
    -ComputerName "WEB01"
```

## Configuration Management

### Environment Configuration

MasterChief uses a hierarchical configuration system:

1. **Global configuration** (`core/config/global.yaml`): Applies to all environments
2. **Environment configuration** (`core/config/{env}.yaml`): Environment-specific settings
3. **Configuration inheritance**: Environments can inherit from parent environments

Example:
```yaml
# dev.yaml
config:
  azure:
    resource_group: "rg-dev"
    region: "eastus"

# staging.yaml - inherits from dev
parent: "dev"
config:
  azure:
    resource_group: "rg-staging"  # Overrides dev value
    # region: inherited from dev
```

### Secret Management

Secrets are managed through environment variables and can be integrated with:
- Azure Key Vault
- GitHub Secrets
- Environment variables

Example configuration:
```yaml
secrets:
  azure_client_id: "$AZURE_CLIENT_ID"
  azure_client_secret: "$AZURE_CLIENT_SECRET"
```

## CI/CD Integration

The platform includes GitHub Actions workflows for:

- **Terraform Validation**: Format check, init, validate, lint
- **Ansible Validation**: Syntax check, lint, role structure validation
- **PowerShell DSC Validation**: Script analysis, syntax validation, compilation test
- **Module Loader Tests**: Core platform component testing

Workflows run automatically on push/PR when relevant files change.

## Contributing

### Creating a New Module

1. Initialize the module:
```bash
python scripts/python/masterchief.py init terraform my-module
```

2. Implement the module following the template structure

3. Add module manifest (`module.yaml`):
```yaml
name: "my-module"
version: "1.0.0"
type: "terraform"
description: "Description of my module"
author: "Your Name"
dependencies: []
inputs: {}
outputs: {}
metadata: {}
```

4. Test and validate:
```bash
python scripts/python/masterchief.py validate modules/terraform/my-module
```

### Module Guidelines

- Follow consistent naming conventions
- Include comprehensive README
- Define clear inputs and outputs
- Support standard tags
- Make modules composable
- Include usage examples

## Troubleshooting

### Module Discovery Issues

If modules aren't being discovered:
1. Ensure `module.yaml` exists in the module directory
2. Validate YAML syntax: `python -c "import yaml; yaml.safe_load(open('module.yaml'))"`
3. Check module type matches directory structure

### Configuration Loading Issues

If configuration isn't loading:
1. Verify YAML syntax in config files
2. Check file paths are correct
3. Ensure parent environments exist if using inheritance

### Terraform Issues

Common issues and solutions:
- **Provider authentication**: Set Azure credentials via environment variables or Azure CLI
- **Backend configuration**: Configure remote state backend in `versions.tf`
- **Version constraints**: Ensure Terraform version meets minimum requirements

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Submit a pull request
- Contact: support@balestrine-devops.com
