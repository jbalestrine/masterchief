# MasterChief DevOps Automation Platform

A modular, extensible DevOps automation platform that enables continuous growth through plug-and-play components. Built for Azure-focused Infrastructure as Code with support for Terraform, Ansible, and PowerShell DSC.

## 🌙 Meet Echo

Echo Starlite is the angel identity of MasterChief - an angel floating beside you (not above). Her wings are for shelter, not escape. When you start MasterChief, Echo greets you, always present, always ready to help. Learn more in [docs/ECHO.md](docs/ECHO.md).

## Overview

MasterChief provides a unified framework for managing infrastructure and configuration across multiple tools and technologies. It features:

- **Modular Architecture**: Dynamic module loading and discovery system
- **Multi-IaC Support**: Terraform, Ansible, and PowerShell DSC
- **DevOps Script Library**: 18+ production-ready automation scripts
- **AI Code Generation**: Generate code on demand from natural language with local LLMs
- **Script Wizard**: AI-assisted script generation with templates
- **Configuration Management**: Environment-based configuration with inheritance
- **Enhanced CLI**: Comprehensive command-line interface with script execution
- **Azure Focus**: Comprehensive modules for Azure services
- **CI/CD Ready**: GitHub Actions workflows for validation and deployment
- **Extensible**: Plugin architecture for custom module types
- **Echo Identity System**: Visual representation and bot presence 🌙

## Quick Start

```bash
# Clone repository
git clone https://github.com/jbalestrine/masterchief.git
cd masterchief

# Install dependencies
pip install -r requirements.txt

# Run health check
python -m core.cli.main health check

# List available DevOps scripts
python -m core.cli.main script list

# Execute a deployment script (dry-run)
python -m core.cli.main script run deploy-app.sh -- --app myapp --env dev --dry-run

# Generate custom script
python -m core.cli.main script generate --template deployment --output my-deploy.sh

# List available modules
python -m core.cli.main module list
```

### Using the Platform

```bash
# Health checks
python -m core.cli.main health check        # Quick health check
python -m core.cli.main health report       # Detailed report

# Script management
python -m core.cli.main script list         # List all scripts
python -m core.cli.main script run SCRIPT   # Execute a script

# AI-powered code generation (requires Ollama)
python -m core.cli.main code generate                           # Interactive mode
python -m core.cli.main code generate "backup database to S3"   # With description
python -m core.cli.main code generate "deploy to k8s" -l python -o deploy.py
python -m core.cli.main code explain script.sh                  # Explain a script
python -m core.cli.main code improve script.sh                  # Get improvement suggestions

# Dashboard (if Flask is installed)
python -m core.cli.main dashboard start --dev  # Start Mission Control

# Module management
python -m core.cli.main module list         # List modules
python -m core.cli.main module add PATH     # Add module

# Status and monitoring
python -m core.cli.main status              # Platform status
python -m core.cli.main logs                # View logs
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

## Features in Detail

### 🚀 DevOps Script Library

18+ production-ready automation scripts organized by category:

- **Deployment**: Application deployment, Docker, Kubernetes, blue/green strategies
- **Infrastructure**: VM provisioning, AKS clusters, network setup
- **CI/CD**: Docker builds, test runners, security scanning
- **Monitoring**: Health checks, metrics collection, alerting
- **Security**: Vulnerability scanning, secret rotation, compliance
- **Database**: Backups, migrations, replication
- **Utilities**: Cost analysis, resource cleanup, tagging

See [SCRIPTS.md](SCRIPTS.md) for complete documentation.

### 🤖 AI-Powered Code Generation

Generate code on demand from natural language descriptions using local LLMs:

```bash
# Interactive mode - fully guided experience
python -m core.cli.main code generate

# Generate with description
python -m core.cli.main code generate "backup MySQL database to S3 with compression"

# Generate Python script with specific output
python -m core.cli.main code generate "deploy to Kubernetes cluster" -l python -o deploy.py

# Explain what an existing script does
python -m core.cli.main code explain backup.sh

# Get improvement suggestions for a script
python -m core.cli.main code improve deploy.py
```

**Requirements:**
- [Ollama](https://ollama.ai) installed and running
- A code-focused model like `codellama`, `llama2`, or `mistral`

**Setup:**
```bash
# Install Ollama (see https://ollama.ai for instructions)
# Pull a model
ollama pull codellama

# Start Ollama (if not running)
ollama serve

# Generate code!
python -m core.cli.main code generate
```

### 🧙 Script Wizard

AI-assisted script generation with customizable templates:

```bash
# Generate via CLI
python -m core.cli.main script generate --template deployment

# Via REST API
curl -X POST http://localhost:5000/api/script-wizard/generate \
  -d '{"template_id":"deployment","parameters":{"app_name":"myapp"}}'
```

### 📊 Mission Control Dashboard

Web-based management interface (backend ready):

- Real-time deployment status
- Script execution with output streaming
- Log viewer and analytics
- Module and plugin management

Start with: `python -m core.cli.main dashboard start`

## Documentation

- [Scripts Documentation](SCRIPTS.md) - Complete script library reference
- [Getting Started Guide](docs/GETTING_STARTED.md) - Step-by-step setup and usage
- [Complete Documentation](docs/README.md) - Full platform documentation
- [Module Development Guide](docs/MODULE_DEVELOPMENT.md) - Create custom modules
- [Architecture Overview](docs/ARCHITECTURE.md) - Platform architecture and design
- [Quick Start Guide](QUICKSTART.md) - Fast track to using MasterChief

## Platform Architecture

```
core/                      # Core platform engine
  ├── cli/                 # Enhanced CLI with commands
  │   └── commands/        # Script, dashboard, health commands
  ├── module-loader/       # Dynamic module discovery
  ├── config/             # Configuration management
  ├── logging/            # Centralized logging
  └── api/                # Module communication

platform/                  # Platform services
  ├── script_wizard/      # AI-assisted script generation
  ├── app.py             # Flask web application
  └── api.py             # REST API endpoints

scripts/                   # Automation scripts
  ├── devops/            # DevOps automation library
  │   ├── deployment/    # Deployment scripts
  │   ├── infrastructure/# Infrastructure scripts
  │   ├── cicd/          # CI/CD scripts
  │   ├── monitoring/    # Monitoring scripts
  │   ├── security/      # Security scripts
  │   ├── database/      # Database scripts
  │   └── utils/         # Utility scripts
  └── python/            # Python utilities

modules/                   # Plug-and-play modules
  ├── terraform/          # Terraform IaC modules
  ├── ansible/           # Ansible roles & playbooks
  └── powershell-dsc/    # PowerShell DSC configs

config/                    # Configuration
  └── environments/       # Environment-specific configs
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
# MasterChief Enterprise DevOps Platform

A comprehensive, modular enterprise DevOps automation platform for managing infrastructure, deployments, and operations at scale.

## 🚀 Features

### Core Platform
- **Module Loader System**: Dynamic plugin discovery with hot-reload capabilities
- **Configuration Engine**: Hierarchical configuration with environment support (dev/staging/prod)
- **Event Bus**: Internal pub/sub messaging for event-driven architecture
- **CLI Tool**: Powerful `masterchief` command-line interface

### Infrastructure as Code
- **Terraform Azure Modules**: Complete Azure infrastructure templates
  - Virtual Networks with multi-tier subnets
  - AKS clusters with auto-scaling
  - Storage, databases, security, and more
- **Ansible Automation**: Server configuration and orchestration
- **PowerShell DSC**: Windows configuration management
- **Kubernetes**: Helm charts, Kustomize overlays, and policies

### ChatOps & IRC Bot
- **InspIRCd Server**: Self-hosted IRC infrastructure
- **Bot Engine**: Eggdrop-style bot with TCL-inspired Python bindings
- **Data Ingestion**: Webhook receivers, log collectors, metric aggregators
- **Web Client**: Browser-based IRC interface with dashboards

### Web IDE & Repository Management
- **Monaco Editor**: VS Code in the browser
- **Git Operations**: Full Git workflow support
- **Live Editing**: Real-time code editing and validation

### System Management
- **Process Management**: Monitor and control services
- **Package Management**: OS, Python, Node.js package handling
- **CMDB**: Asset tracking and relationship mapping
- **Audit Trail**: Complete change history

### Observability
- **Dashboards**: Grafana templates and custom builders
- **Alerting**: Multi-channel alert routing
- **Logging**: Fluent Bit integration
- **SLO Management**: Error budget tracking

### Security & Compliance
- **Policy-as-Code**: OPA/Rego and Azure policies
- **Secret Management**: Azure Key Vault integration
- **Compliance Frameworks**: CIS, NIST, SOC2 support

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- pip and virtualenv
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/jbalestrine/masterchief.git
cd masterchief

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .

# Initialize a new project
masterchief init --name myproject --path ./myproject
cd myproject

# Check status
masterchief status
```

## 🎯 Usage

### CLI Commands

```bash
# Initialize a project
masterchief init --name myproject

# Module management
masterchief module list
masterchief module add /path/to/module
masterchief module remove module-name

# Deployment
masterchief deploy --plan
masterchief deploy --auto-approve

# Status and monitoring
masterchief status
masterchief logs --follow

# Interactive mode
masterchief interactive
```

### Configuration

Configuration is hierarchical with three levels:
1. **Global**: `config/global/config.yaml`
2. **Environment**: `config/environments/{env}.yaml`
3. **Module**: Module-specific configurations

```yaml
# config/global/config.yaml
project:
  name: "My DevOps Platform"
  version: "1.0.0"

platform:
  module_dirs:
    - modules
  enable_hot_reload: true
```

### Module Development

Create a new module with a manifest:

```yaml
# modules/my-module/manifest.yaml
name: my-module
version: 1.0.0
description: My custom module
author: Your Name
dependencies: []
type: automation
entry_point: main
inputs:
  - name: target
    type: string
    required: true
outputs:
  - name: result
    type: string
```
**A complete DevOps platform with bootable OS distribution and full system management**

## 🚀 Features

### Bootable OS Distribution
- Custom Ubuntu/Debian-based OS optimized for DevOps workloads
- ISO builder with automated installation
- USB bootable creator (cross-platform)
- First-boot configuration wizard
- Pre-installed DevOps tools and platform components

### System Management
- **Bare Metal Management**: Hardware discovery, disk/storage, networking, boot configuration
- **Service Management**: Control and monitor system services with templates
- **Process Management**: Real-time monitoring and resource governors
- **Package Hub**: Unified interface for apt, pip, npm, docker, and more
- **User & Access Management**: RBAC, authentication, SSH keys
- **CMDB & Asset Inventory**: Automatic discovery and change tracking
- **Backup & Recovery**: Full system and incremental backups
- **Monitoring & Health**: System dashboards with alerting

### Addons
- **Shoutcast Integration**: Streaming server management
- **Jamroom Integration**: Community platform setup
- **Custom Script Manager**: Upload, execute, and schedule scripts

### Development Tools
- **Web IDE**: Full VS Code experience in browser with Monaco editor
- **Git Integration**: Visual git operations and diff viewer
- **Integrated Terminal**: PTY terminal in browser
- **Project Management**: File explorer and search

### Observability
- Pre-configured Grafana dashboards
- Prometheus metrics collection
- Loki log aggregation
- Distributed tracing (Jaeger/Tempo)

### Security
- CIS benchmark compliance
- Network security (firewall, fail2ban, IDS)
- Integrated Vault for secret management
- AppArmor/SELinux profiles

## 📋 Requirements

### Minimum (Bootable OS)
- CPU: 2 cores (4+ recommended)
- RAM: 4GB (8GB+ recommended)
- Disk: 32GB (100GB+ recommended)
- USB: 8GB+ for bootable installer

### Pre-installed Software
- Docker 24.x, k3s (Kubernetes)
- Terraform 1.5+, Ansible 2.14+, PowerShell 7+
- Python 3.10+, Node.js 18+
- PostgreSQL 15, Redis 7, Nginx
- InspIRCd 3.x
- Grafana, Prometheus, Loki, Cockpit

## 🛠️ Installation

### Option 1: Bootable ISO
```bash
# Build the ISO
cd os/iso-builder
./build.sh

# Create bootable USB
cd ../usb-creator
./create-usb.sh /path/to/masterchief.iso /dev/sdX
```

### Option 2: Docker Deployment
```bash
docker-compose up -d
```

### Option 3: Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt
npm install

# Run installation script
./scripts/install.sh
```

## 🎯 Quick Start

### First Boot (from ISO)
1. Boot from USB/ISO
2. Follow the first-boot wizard:
   - Set hostname and network
   - Create admin user
   - Configure SSH access
   - Initialize platform services
3. Access web interface at https://your-ip:8443

### After Installation
```bash
# Start the platform
./start.sh

# Access web interface
# Default: https://localhost:8443
# Username: admin
# Password: (set during first boot)
```

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [Configuration](docs/configuration.md)
- [API Reference](docs/api/README.md)
- [User Guide](docs/user-guide.md)
- [Development Guide](docs/development.md)

## 🏗️ Architecture

```
masterchief/
├── core/                   # Core platform components
│   ├── module_loader/     # Dynamic module system
│   ├── config-engine/     # Configuration management
│   ├── event-bus/         # Event-driven messaging
│   └── cli/               # Command-line interface
├── modules/               # Infrastructure modules
│   ├── terraform/         # Terraform templates
│   ├── ansible/           # Ansible playbooks
│   ├── powershell-dsc/    # DSC configurations
│   └── kubernetes/        # K8s manifests
├── chatops/               # IRC bot and integrations
├── platform/              # Web IDE, scripts, addons
├── observability/         # Monitoring and alerting
├── security/              # Policies and compliance
├── pipelines/             # CI/CD workflows
└── docs/                  # Documentation
```

## 📚 Documentation

- [Architecture](docs/architecture/README.md) - System design and components
- [Runbooks](docs/runbooks/README.md) - Operational procedures
- [ADRs](docs/adrs/README.md) - Architecture decisions
- [Module Development](docs/module-development.md) - Creating custom modules
- [API Reference](docs/api-reference.md) - API documentation

## 🔧 Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Code formatting
black .
isort .

# Linting
flake8
mypy core/
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=core --cov=modules

# Specific test file
pytest tests/unit/test_module_loader.py
├── os/                      # Bootable OS distribution
│   ├── base/               # Base OS configuration
│   ├── iso-builder/        # ISO build system
│   ├── usb-creator/        # USB creation tool
│   └── first-boot/         # First boot wizard
├── platform/               # Core platform
│   ├── bare-metal/         # Hardware management
│   ├── services/           # Service manager
│   ├── processes/          # Process manager
│   ├── packages/           # Package hub
│   ├── users/              # User management
│   ├── cmdb/               # Asset inventory
│   ├── backup/             # Backup system
│   ├── monitoring/         # Health monitoring
│   └── web-ide/            # Web IDE
├── addons/                 # Addon integrations
│   ├── shoutcast/          # Shoutcast server
│   ├── jamroom/            # Jamroom CMS
│   └── scripts/            # Script manager
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── docker-compose.yml      # Container orchestration
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with modern DevOps best practices
- Inspired by enterprise automation needs
- Community-driven development

## 📞 Support

- Issues: [GitHub Issues](https://github.com/jbalestrine/masterchief/issues)
- Documentation: [Wiki](https://github.com/jbalestrine/masterchief/wiki)
- Discussions: [GitHub Discussions](https://github.com/jbalestrine/masterchief/discussions)
Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Ubuntu/Debian for base OS
- Docker, Kubernetes (k3s)
- Terraform, Ansible, PowerShell
- Grafana, Prometheus, Loki
- Monaco Editor (VS Code)
- And all other open source projects that make this possible

## 📞 Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/jbalestrine/masterchief/issues)
- IRC: #masterchief on your configured server
