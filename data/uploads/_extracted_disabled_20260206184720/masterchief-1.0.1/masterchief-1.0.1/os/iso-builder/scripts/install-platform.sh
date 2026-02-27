#!/bin/bash
# MasterChief Platform Installation Script (ISO version)
# This script is included in the ISO and runs during installation

set -e

echo "======================================"
echo "MasterChief Platform Installer"
echo "======================================"

INSTALL_DIR="/opt/masterchief"
CONFIG_DIR="/etc/masterchief"
LOG_DIR="/var/log/masterchief"
DATA_DIR="/var/lib/masterchief"

# Create directories if they don't exist
mkdir -p $INSTALL_DIR
mkdir -p $CONFIG_DIR
mkdir -p $LOG_DIR
mkdir -p $DATA_DIR

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --quiet flask pyyaml jinja2 requests sqlalchemy psycopg2-binary redis

# Create default configuration
if [ ! -f $CONFIG_DIR/config.yml ]; then
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
fi

# Create systemd service
cat > /etc/systemd/system/masterchief.service <<EOF
[Unit]
Description=MasterChief DevOps Platform
After=network.target docker.service

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

# Reload systemd
systemctl daemon-reload
systemctl enable masterchief.service

echo "Platform installation complete!"
echo "Use 'systemctl start masterchief' to start the platform"
