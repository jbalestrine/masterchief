# MasterChief Platform - Configuration Guide

## Configuration File

The main configuration file is located at `/etc/masterchief/config.yml`.

## Configuration Structure

```yaml
platform:
  version: "1.0.0"              # Platform version
  install_dir: "/opt/masterchief"   # Installation directory
  config_dir: "/etc/masterchief"    # Configuration directory
  log_dir: "/var/log/masterchief"   # Log directory
  data_dir: "/var/lib/masterchief"  # Data directory

api:
  host: "0.0.0.0"               # Listen address (0.0.0.0 = all interfaces)
  port: 8443                    # HTTPS port
  ssl: true                     # Enable SSL/TLS

database:
  type: "postgresql"            # Database type
  host: "localhost"             # Database host
  port: 5432                    # Database port
  database: "masterchief"       # Database name
  user: "masterchief"           # Database user
  password: ""                  # Database password

monitoring:
  enabled: true                 # Enable monitoring
  prometheus_port: 9090         # Prometheus port
  grafana_port: 3000           # Grafana port

security:
  cis_compliance: true          # CIS benchmark compliance
  firewall_enabled: true        # Enable firewall
  auto_updates: true           # Automatic security updates

addons:
  shoutcast:
    enabled: false              # Enable Shoutcast addon
    port: 8000                  # Shoutcast port
  
  jamroom:
    enabled: false              # Enable Jamroom addon
    path: "/var/www/jamroom"    # Jamroom installation path
  
  scripts:
    enabled: true               # Enable custom script manager
    max_execution_time: 300     # Maximum script execution time (seconds)
```

## Environment Variables

You can override configuration using environment variables:

```bash
export MASTERCHIEF_ENV=production
export DATABASE_URL=postgresql://user:pass@host:5432/dbname
export REDIS_URL=redis://localhost:6379/0
```

## SSL/TLS Configuration

### Self-Signed Certificate (Development)

The platform automatically generates a self-signed certificate for development.

### Production Certificate

For production, use Let's Encrypt or your own certificate:

```bash
# Create certificate directory
sudo mkdir -p /etc/masterchief/ssl

# Copy your certificate
sudo cp your-cert.crt /etc/masterchief/ssl/cert.crt
sudo cp your-key.key /etc/masterchief/ssl/key.key

# Update config.yml
ssl:
  enabled: true
  cert_file: "/etc/masterchief/ssl/cert.crt"
  key_file: "/etc/masterchief/ssl/key.key"
```

## Database Configuration

### PostgreSQL

```yaml
database:
  type: "postgresql"
  host: "localhost"
  port: 5432
  database: "masterchief"
  user: "masterchief"
  password: "your-secure-password"
```

### Connection String

Alternatively, use a connection string:

```yaml
database:
  url: "postgresql://masterchief:password@localhost:5432/masterchief"
```

## Monitoring Configuration

### Prometheus

Configure Prometheus targets in `config/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'masterchief'
    static_configs:
      - targets: ['localhost:8443']
  
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
```

### Grafana

Configure Grafana datasources in `config/grafana/datasources/`:

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
```

## Security Configuration

### Firewall Rules

```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow API
sudo ufw allow 8443/tcp

# Allow Grafana
sudo ufw allow 3000/tcp

# Enable firewall
sudo ufw enable
```

### SSH Hardening

Edit `/etc/ssh/sshd_config`:

```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
Port 22
```

### Automatic Updates

Configure unattended upgrades in `/etc/apt/apt.conf.d/50unattended-upgrades`:

```
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
};
Unattended-Upgrade::Automatic-Reboot "false";
```

## Addon Configuration

### Shoutcast

```yaml
addons:
  shoutcast:
    enabled: true
    port: 8000
    password: "changeme"
    max_users: 100
    log_file: "/var/log/shoutcast/sc_serv.log"
```

### Jamroom

```yaml
addons:
  jamroom:
    enabled: true
    path: "/var/www/jamroom"
    database:
      host: "localhost"
      database: "jamroom"
      user: "jamroom"
      password: "changeme"
```

### Custom Scripts

```yaml
addons:
  scripts:
    enabled: true
    max_execution_time: 300
    allowed_extensions: [".sh", ".py", ".js"]
    storage_path: "/var/lib/masterchief/scripts"
```

## Logging Configuration

### Log Levels

Set log level in config:

```yaml
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  handlers:
    - type: "file"
      filename: "/var/log/masterchief/masterchief.log"
    - type: "console"
```

### Log Rotation

Configure logrotate in `/etc/logrotate.d/masterchief`:

```
/var/log/masterchief/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        systemctl reload masterchief
    endscript
}
```

## Backup Configuration

```yaml
backup:
  enabled: true
  schedule: "0 2 * * *"  # Daily at 2 AM
  retention: 7            # Keep 7 days
  destinations:
    - type: "local"
      path: "/var/backups/masterchief"
    - type: "s3"
      bucket: "masterchief-backups"
      region: "us-east-1"
```

## Performance Tuning

### API Workers

For production, use gunicorn or uwsgi:

```yaml
api:
  workers: 4
  threads: 2
  timeout: 30
```

### Database Pool

```yaml
database:
  pool_size: 20
  max_overflow: 10
  pool_timeout: 30
```

## Reloading Configuration

After making changes:

```bash
# Reload configuration without restart
sudo systemctl reload masterchief

# Or restart service
sudo systemctl restart masterchief
```

## Validation

Validate your configuration:

```bash
sudo python3 -c "
import yaml
with open('/etc/masterchief/config.yml') as f:
    config = yaml.safe_load(f)
    print('Configuration is valid')
    print(yaml.dump(config, default_flow_style=False))
"
```
