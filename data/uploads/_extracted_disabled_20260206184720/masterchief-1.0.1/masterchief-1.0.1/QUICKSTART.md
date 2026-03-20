# MasterChief Enterprise DevOps Platform - Quick Start Guide

## Installation

### Using pip

```bash
# Clone the repository
git clone https://github.com/jbalestrine/masterchief.git
cd masterchief

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run from source

```bash
# CLI commands
python -m core.cli.main --help
python -m core.cli.main status
python -m core.cli.main module list
```

## Quick Examples

### Initialize a Project

```bash
python -m core.cli.main init --name myproject --path ./myproject
cd myproject
```

### List Available Modules

```bash
python -m core.cli.main module list
```

### Deploy Infrastructure

```bash
python -m core.cli.main deploy --plan
python -m core.cli.main deploy --auto-approve
```

### Interactive Mode

```bash
python -m core.cli.main interactive
```

## Core Components

### 1. Module Loader
Dynamic plugin system with hot-reload capabilities located in `core/module_loader/`

### 2. Configuration Engine
Hierarchical configuration management in `core/config_engine/`

### 3. Event Bus
Pub/sub messaging system in `core/event_bus/`

### 4. CLI Tool
Command-line interface in `core/cli/`

## Infrastructure Modules

### Terraform (Azure)
- **Networking**: VNets, subnets, NSGs (`modules/terraform/azure/networking/`)
- **Compute**: AKS clusters (`modules/terraform/azure/compute/`)
- **Storage**: Storage accounts (templates ready)
- **Database**: SQL, Cosmos DB (templates ready)

### Ansible
- **Common**: Baseline server configuration
- **Security**: Hardening and compliance
- **Monitoring**: Agent installation

### Kubernetes
- **Manifests**: Namespace, RBAC configurations
- **Helm Charts**: Application deployment
- **Kustomize**: Environment overlays

### PowerShell DSC
- **WebServerConfig**: IIS configuration

## ChatOps

### IRC Bot Engine
Python-based bot with TCL-inspired bindings:

```python
bot.bind("pub", "-|-", "!deploy", deploy_handler)
bot.bind("msg", "-|-", "!status", status_handler)
```

See `docs/examples/irc-bot-example.py` for complete example.

## Documentation

- **Architecture**: `docs/architecture/README.md`
- **Runbooks**: `docs/runbooks/README.md`
- **ADRs**: `docs/adrs/`
- **Examples**: `docs/examples/`

## Configuration

Configuration files use hierarchical loading:

1. **Global**: `config/global/config.yaml`
2. **Environment**: `config/environments/{env}.yaml`
3. **Module**: Module-specific configs

Example:
```yaml
# config/environments/prod.yaml
environment: prod
debug: false
azure:
  subscription_id: "${env:AZURE_SUBSCRIPTION_ID}"
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/unit/ -v

# With coverage
pytest --cov=core --cov=modules
```

### Code Quality

```bash
# Formatting
black core/ modules/

# Linting
flake8 core/ modules/

# Type checking
mypy core/
```

## Project Structure

```
masterchief/
├── core/                   # Core platform
│   ├── module_loader/     # Module system
│   ├── config_engine/     # Configuration
│   ├── event_bus/         # Event messaging
│   └── cli/               # CLI tool
├── modules/               # Infrastructure modules
│   ├── terraform/         # Terraform templates
│   ├── ansible/           # Ansible playbooks
│   ├── kubernetes/        # K8s manifests
│   └── powershell-dsc/    # DSC configs
├── chatops/               # IRC bot
├── observability/         # Monitoring
├── config/                # Configuration
├── docs/                  # Documentation
└── tests/                 # Test suite
```

## Next Steps

1. Read the [Architecture Documentation](docs/architecture/README.md)
2. Try the [Azure Deployment Example](docs/examples/azure-deployment.md)
3. Explore [Runbooks](docs/runbooks/README.md)
4. Review [ADRs](docs/adrs/) for design decisions

## Support

- **Issues**: [GitHub Issues](https://github.com/jbalestrine/masterchief/issues)
- **Documentation**: [Wiki](https://github.com/jbalestrine/masterchief/wiki)

## License

MIT License - See [LICENSE](LICENSE) file for details.
