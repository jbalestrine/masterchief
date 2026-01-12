# MasterChief Enterprise DevOps Platform

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