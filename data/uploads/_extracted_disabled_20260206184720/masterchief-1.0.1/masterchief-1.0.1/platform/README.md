# MasterChief Platform - Core Platform

This directory contains the core platform modules for system management.

## Architecture

```
platform/
├── api.py              # Main Flask API application
├── config.py           # Configuration management
├── main.py            # Entry point
├── bare-metal/        # Hardware & infrastructure management
├── backup/            # Backup & recovery
├── cmdb/              # Asset inventory & discovery
├── monitoring/        # Health monitoring & alerts
├── packages/          # Package manager hub
├── processes/         # Process management
├── services/          # Service management
├── users/             # User & access management
└── web-ide/           # Web-based IDE
```

## Modules

### Service Manager (`services/`)

Control and monitor system services using systemd.

**Features:**
- List all services with status
- Start/stop/restart services
- Enable/disable services at boot
- View service logs
- Service health monitoring

**API:**
```python
from platform.services.manager import ServiceManager

manager = ServiceManager()
services = manager.list_services()
manager.start('nginx')
manager.restart('docker')
logs = manager.get_logs('postgresql', lines=100)
```

### Bare Metal Management (`bare-metal/`)

Manage hardware, storage, networking, and boot configuration.

**Components:**
- `hardware.py` - CPU, memory, disk, network discovery
- `storage.py` - Disk/partition/filesystem management
- `network.py` - Network interface configuration
- `boot.py` - GRUB and kernel management (future)

**API:**
```python
from platform.bare_metal.hardware import HardwareDiscovery

hw = HardwareDiscovery()
info = hw.discover_all()
print(f"CPU: {info['cpu']['model']}")
print(f"RAM: {info['memory']['total_bytes']} bytes")
```

### Process Manager (`processes/`)

Real-time process monitoring and control.

**Features:**
- List processes with resource usage
- CPU, memory, I/O per process
- Process tree visualization
- Kill/terminate processes
- Resource limits (cgroups)

**API:**
```python
from platform.processes.manager import ProcessManager

pm = ProcessManager()
processes = pm.list_processes(sort_by='cpu')
stats = pm.get_system_stats()
pm.kill_process(1234, signal='TERM')
```

### Package Manager Hub (`packages/`)

Unified interface for multiple package managers (apt, pip, npm, docker).

**Features:**
- Search across all package managers
- Install/remove packages
- Update packages
- Security vulnerability scanning
- Version pinning

**API:**
```python
from platform.packages.manager import PackageManager

pm = PackageManager()
results = pm.search('nginx', manager='apt')
pm.install('nginx', manager='apt')
packages = pm.list_installed(manager='all')
```

### Monitoring & Health (`monitoring/`)

System health monitoring and alerting.

**Features:**
- Real-time system metrics (CPU, RAM, disk)
- Service health checks
- Alert management
- Performance metrics
- Resource usage trends

**API:**
```python
from platform.monitoring.api import monitoring_bp

# Access via REST API
GET /api/monitoring/health
GET /api/monitoring/metrics
GET /api/monitoring/alerts
```

### User Management (`users/`)

User and access management with RBAC.

**Features:**
- Create/modify/delete users
- Group management
- SSH key management
- Sudo configuration
- RBAC roles and permissions

### CMDB & Asset Inventory (`cmdb/`)

Configuration management database and asset discovery.

**Features:**
- Automatic hardware discovery
- Software inventory
- Change tracking
- Relationship mapping
- Compliance reporting

### Backup & Recovery (`backup/`)

System backup and recovery management.

**Features:**
- Full system backups
- Incremental backups
- Multiple destinations (local, S3, Azure, etc.)
- Point-in-time recovery
- Automated scheduling

### Web IDE (`web-ide/`)

Browser-based integrated development environment.

**Features:**
- Monaco editor (VS Code engine)
- Multi-language support
- Git integration
- Integrated terminal
- File management

## Configuration

Platform configuration is managed in `/etc/masterchief/config.yml`:

```yaml
platform:
  version: "1.0.0"
  install_dir: "/opt/masterchief"
  config_dir: "/etc/masterchief"
  log_dir: "/var/log/masterchief"
  data_dir: "/var/lib/masterchief"
```

## API Endpoints

All modules expose REST API endpoints under `/api/`:

- `/api/services` - Service management
- `/api/bare-metal` - Hardware management
- `/api/processes` - Process management
- `/api/packages` - Package management
- `/api/users` - User management
- `/api/cmdb` - Asset inventory
- `/api/backup` - Backup management
- `/api/monitoring` - Health monitoring
- `/api/web-ide` - Web IDE

See [API Documentation](../docs/api/README.md) for details.

## Development

### Running the Platform

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run development server
python3 platform/main.py

# Or with environment variables
export MASTERCHIEF_ENV=development
python3 platform/main.py
```

### Testing

```bash
# Run tests
pytest platform/

# Run specific module tests
pytest platform/services/

# With coverage
pytest --cov=platform platform/
```

### Adding New Modules

1. Create module directory in `platform/`
2. Create `manager.py` with core logic
3. Create `api.py` with Flask Blueprint
4. Register blueprint in `platform/api.py`
5. Add tests in `tests/`
6. Update documentation

## Security

- All API endpoints should validate input
- Use proper authentication/authorization
- Follow principle of least privilege
- Audit all configuration changes
- Encrypt sensitive data at rest
- Use HTTPS for all API communication

## Performance

- Use connection pooling for databases
- Cache frequently accessed data
- Implement rate limiting
- Use async operations where appropriate
- Monitor resource usage
- Optimize database queries

## Logging

All modules use Python's logging framework:

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Service started")
logger.warning("High CPU usage detected")
logger.error("Failed to connect to database")
```

Logs are written to `/var/log/masterchief/masterchief.log`.

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.
