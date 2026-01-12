# MasterChief DevOps Automation Platform

A modular, extensible DevOps automation platform that enables continuous growth through plug-and-play components. Built for Azure-focused Infrastructure as Code with support for Terraform, Ansible, and PowerShell DSC.

## Overview

MasterChief provides a unified framework for managing infrastructure and configuration across multiple tools and technologies. It features:

- **Modular Architecture**: Dynamic module loading and discovery system
- **Multi-IaC Support**: Terraform, Ansible, and PowerShell DSC
- **Configuration Management**: Environment-based configuration with inheritance
- **Azure Focus**: Comprehensive modules for Azure services
- **CI/CD Ready**: GitHub Actions workflows for validation and deployment
- **Extensible**: Plugin architecture for custom module types

## Quick Start

```bash
# Clone repository
git clone https://github.com/jbalestrine/masterchief.git
cd masterchief

# Install dependencies
pip install pyyaml

# List available modules
python scripts/python/masterchief.py list

# Show configuration
python scripts/python/masterchief.py config dev

# Initialize a new module
python scripts/python/masterchief.py init terraform my-module
```

## Available Modules

### Terraform Modules
- **azure-vnet**: Virtual Network with subnets and NSGs
- **azure-aks**: Azure Kubernetes Service with multi-node pools
- **azure-storage**: Storage Account with containers and file shares
- **azure-keyvault**: Key Vault for secrets management

### Ansible Roles
- **common**: Base Linux server configuration
- **docker**: Docker installation and configuration

### PowerShell DSC
- **CommonServer**: Base Windows server configuration
- **WebServer**: IIS web server setup

## Documentation

- [Getting Started Guide](docs/GETTING_STARTED.md) - Step-by-step setup and usage
- [Complete Documentation](docs/README.md) - Full platform documentation
- [Module Development Guide](docs/MODULE_DEVELOPMENT.md) - Create custom modules
- [Architecture Overview](docs/ARCHITECTURE.md) - Platform architecture and design

## Platform Architecture

```
core/                   # Core platform engine
  ├── module-loader/    # Dynamic module discovery
  ├── config/          # Configuration management
  ├── logging/         # Centralized logging
  └── api/             # Module communication

modules/                # Plug-and-play modules
  ├── terraform/       # Terraform IaC modules
  ├── ansible/         # Ansible roles & playbooks
  └── powershell-dsc/  # PowerShell DSC configs

scripts/                # Automation scripts
  └── python/          # CLI and utilities
```

## Contributing

We welcome contributions! Please see our [Module Development Guide](docs/MODULE_DEVELOPMENT.md) for details on creating new modules.

## Requirements

- Python 3.10+
- Terraform 1.5+ (for Terraform modules)
- Ansible 2.14+ (for Ansible modules)
- PowerShell 7+ (for DSC modules)
- Azure CLI (for Azure deployments)

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Submit a pull request
- Contact: jbalestrine@users.noreply.github.com