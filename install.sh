#!/bin/bash
# MasterChief Platform Installation Script

set -e

INSTALL_DIR="/opt/masterchief"
CONFIG_DIR="/etc/masterchief"
LOG_DIR="/var/log/masterchief"
DATA_DIR="/var/lib/masterchief"

echo "======================================"
echo "MasterChief Platform Installer"
echo "======================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo ./install.sh)"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    echo "Cannot detect OS. Unsupported system."
    exit 1
fi

echo "Detected OS: $OS $VER"
echo ""

# Create directories
echo "Creating directories..."
mkdir -p $INSTALL_DIR
mkdir -p $CONFIG_DIR
mkdir -p $LOG_DIR
mkdir -p $DATA_DIR

# Install dependencies based on OS
echo "Installing dependencies..."
case $OS in
    ubuntu|debian)
        apt-get update
        apt-get install -y \
            python3 python3-pip python3-venv \
            nodejs npm \
            git curl wget jq \
            docker.io docker-compose \
            postgresql-client redis-tools \
            nginx \
            build-essential
        ;;
    centos|rhel|fedora)
        dnf install -y \
            python3 python3-pip \
            nodejs npm \
            git curl wget jq \
            docker docker-compose \
            postgresql redis \
            nginx \
            gcc gcc-c++ make
        ;;
    *)
        echo "Unsupported OS: $OS"
        exit 1
        ;;
esac

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Install Node.js dependencies (if package.json exists)
if [ -f package.json ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Copy files
echo "Copying platform files..."
cp -r platform $INSTALL_DIR/
cp -r addons $INSTALL_DIR/
cp -r scripts $INSTALL_DIR/
cp -r docs $INSTALL_DIR/

# Create configuration files
echo "Creating configuration files..."
cat > $CONFIG_DIR/config.yml <<EOF
platform:
  version: "1.0.0"
  install_dir: "$INSTALL_DIR"
  config_dir: "$CONFIG_DIR"
  log_dir: "$LOG_DIR"
  data_dir: "$DATA_DIR"

api:
  host: "0.0.0.0"
  port: 8443
  ssl: true
  
database:
  type: "postgresql"
  host: "localhost"
  port: 5432
  database: "masterchief"
  
monitoring:
  enabled: true
  prometheus_port: 9090
  grafana_port: 3000

security:
  cis_compliance: true
  firewall_enabled: true
  auto_updates: true
EOF

# Create systemd service
echo "Creating systemd service..."
cat > /etc/systemd/system/masterchief.service <<EOF
[Unit]
Description=MasterChief DevOps Platform
After=network.target docker.service postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/platform/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable masterchief.service

echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Configure the platform: edit $CONFIG_DIR/config.yml"
echo "2. Start the platform: systemctl start masterchief"
echo "3. Check status: systemctl status masterchief"
echo "4. Access web interface: https://localhost:8443"
echo ""
echo "For more information, see: $INSTALL_DIR/docs/"
