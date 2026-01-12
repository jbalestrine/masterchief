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

## 🏗️ Architecture

```
masterchief/
├── core/                   # Core platform components
│   ├── module-loader/     # Dynamic module system
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