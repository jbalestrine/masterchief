# MasterChief Platform - Installation Guide

## Prerequisites

- Ubuntu 22.04 LTS or Debian 12 (or compatible)
- Root or sudo access
- Minimum 4GB RAM, 2 CPU cores
- 32GB free disk space
- Internet connection for downloading packages

## Installation Methods

### 1. Bootable ISO Installation

#### Build the ISO

```bash
cd os/iso-builder
sudo ./build.sh
```

This will:
- Create a bootable ISO based on Ubuntu 22.04
- Pre-install all DevOps tools
- Include MasterChief platform
- Configure security hardening

#### Create Bootable USB

```bash
cd os/usb-creator
sudo ./create-usb.sh ../iso-builder/output/masterchief-1.0.0-amd64.iso /dev/sdX
```

Replace `/dev/sdX` with your USB device.

#### Boot and Install

1. Boot from USB/ISO
2. Select "Install MasterChief OS"
3. Follow the first-boot wizard:
   - Set hostname
   - Configure network
   - Create admin user
   - Configure SSH
   - Initialize services

### 2. Docker Installation

#### Using Docker Compose

```bash
# Clone repository
git clone https://github.com/jbalestrine/masterchief.git
cd masterchief

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f masterchief-api
```

#### Access the Platform

- API: https://localhost:8443
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

### 3. Manual Installation

#### Install on Ubuntu/Debian

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Clone repository
git clone https://github.com/jbalestrine/masterchief.git
cd masterchief

# Run installer
sudo ./install.sh
```

#### Configuration

Edit configuration file:

```bash
sudo nano /etc/masterchief/config.yml
```

#### Start the Platform

```bash
sudo systemctl start masterchief
sudo systemctl enable masterchief
```

#### Check Status

```bash
sudo systemctl status masterchief
sudo journalctl -u masterchief -f
```

## Post-Installation

### Access Web Interface

Open browser to: https://your-server-ip:8443

Default credentials (change immediately):
- Username: admin
- Password: (set during installation)

### Configure Services

1. **Service Manager**: Manage system services
2. **Bare Metal**: Configure hardware and networking
3. **Monitoring**: Set up alerts and dashboards
4. **Backup**: Configure backup schedules
5. **Users**: Add team members and set permissions

### Security Hardening

The platform includes CIS benchmark Level 1 compliance by default:

- Firewall enabled (UFW)
- SSH hardened (no root login, key-based auth)
- Automatic security updates
- AppArmor/SELinux enabled
- Audit logging (auditd)

### Enable Addons

#### Shoutcast

```bash
# Edit config
sudo nano /etc/masterchief/config.yml

# Set addons.shoutcast.enabled: true
# Restart platform
sudo systemctl restart masterchief
```

#### Jamroom

```bash
# Install Jamroom addon
cd addons/jamroom
sudo python3 -m manager install

# Configure database
sudo python3 -m manager configure
```

#### Custom Scripts

```bash
# Upload script via API or web interface
curl -X POST https://localhost:8443/api/scripts/upload \
  -H "Content-Type: application/json" \
  -d '{"name": "backup.sh", "content": "#!/bin/bash\n..."}'
```

## Troubleshooting

### Platform won't start

```bash
# Check logs
sudo journalctl -u masterchief -n 100

# Check configuration
sudo python3 -c "import yaml; print(yaml.safe_load(open('/etc/masterchief/config.yml')))"

# Verify dependencies
pip3 list | grep -E "flask|psutil|pyyaml"
```

### Cannot access web interface

```bash
# Check if service is running
sudo systemctl status masterchief

# Check firewall
sudo ufw status

# Allow port 8443
sudo ufw allow 8443/tcp

# Check if port is listening
sudo netstat -tlnp | grep 8443
```

### Database connection failed

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -h localhost -U masterchief -d masterchief

# Reset password
sudo -u postgres psql -c "ALTER USER masterchief PASSWORD 'newpassword';"
```

## Upgrading

### Docker

```bash
docker-compose pull
docker-compose up -d
```

### Manual

```bash
cd /opt/masterchief
git pull
pip3 install -r requirements.txt --upgrade
sudo systemctl restart masterchief
```

## Uninstalling

### Docker

```bash
docker-compose down -v
```

### Manual

```bash
sudo systemctl stop masterchief
sudo systemctl disable masterchief
sudo rm -rf /opt/masterchief
sudo rm -rf /etc/masterchief
sudo rm /etc/systemd/system/masterchief.service
sudo systemctl daemon-reload
```

## Support

- Documentation: [docs/](../docs/)
- Issues: GitHub Issues
- IRC: #masterchief on configured server
