#!/bin/bash
# MasterChief Platform - Quick Start Demo
# This script demonstrates the platform capabilities

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   MasterChief Enterprise DevOps Platform - Quick Demo     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required"
    exit 1
fi

# Check if dependencies are installed
echo "Checking dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing dependencies..."
    pip3 install -q flask flask-cors pyyaml psutil requests
fi

echo "✓ Dependencies OK"
echo ""

# Display platform information
echo "Platform Information:"
echo "  Version: 1.0.0"
echo "  Install Dir: $(pwd)"
echo "  Python: $(python3 --version)"
echo ""

# Show available components
echo "Available Components:"
echo "  ✓ OS - Bootable distribution builder"
echo "  ✓ Platform - Core system management"
echo "  ✓ Addons - Shoutcast, Jamroom, Scripts"
echo "  ✓ Docker - Container orchestration"
echo ""

# Show OS capabilities
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "OS Distribution Builder"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Build bootable ISO:"
echo "  cd os/iso-builder && sudo ./build.sh"
echo ""
echo "Create bootable USB:"
echo "  cd os/usb-creator && sudo ./create-usb.sh <iso> <device>"
echo ""

# Show platform capabilities
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Platform Management Capabilities"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Service Management:"
echo "  • List, start, stop, restart system services"
echo "  • View service logs and status"
echo "  • Enable/disable services at boot"
echo ""
echo "Process Management:"
echo "  • Monitor CPU, memory usage per process"
echo "  • Kill/terminate processes"
echo "  • System resource statistics"
echo ""
echo "Package Management:"
echo "  • Search and install packages (apt, pip, npm)"
echo "  • Update packages"
echo "  • List installed packages"
echo ""
echo "Hardware Management:"
echo "  • CPU, memory, disk discovery"
echo "  • Network interface configuration"
echo "  • Storage management"
echo ""
echo "Monitoring & Health:"
echo "  • Real-time system metrics"
echo "  • Alert management"
echo "  • Resource usage tracking"
echo ""
echo "Backup & Recovery:"
echo "  • Full and incremental backups"
echo "  • Multiple backup destinations"
echo "  • Point-in-time recovery"
echo ""
echo "CMDB & Asset Inventory:"
echo "  • Automatic hardware discovery"
echo "  • Change tracking"
echo "  • Asset relationships"
echo ""

# Show addon capabilities
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Addon Integrations"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Shoutcast Server:"
echo "  • Streaming server management"
echo "  • Listener statistics"
echo "  • Multi-stream support"
echo ""
echo "Jamroom CMS:"
echo "  • Community platform setup"
echo "  • Module management"
echo "  • LAMP/LEMP stack"
echo ""
echo "Custom Script Manager:"
echo "  • Upload and execute scripts"
echo "  • Sandboxed execution"
echo "  • Scheduled execution"
echo ""

# Show deployment options
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Deployment Options"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Docker Compose (Recommended for testing):"
echo "   docker-compose up -d"
echo "   Access: https://localhost:8443"
echo ""
echo "2. Manual Installation:"
echo "   sudo ./install.sh"
echo "   sudo systemctl start masterchief"
echo ""
echo "3. Bootable ISO:"
echo "   Build ISO and boot from USB/CD"
echo "   Follow first-boot wizard"
echo ""

# Show API examples
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "API Examples"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Start the platform:"
echo "  python3 platform/main.py"
echo ""
echo "Then test with curl:"
echo "  curl -k https://localhost:8443/api/health"
echo "  curl -k https://localhost:8443/api/services"
echo "  curl -k https://localhost:8443/api/monitoring/health"
echo "  curl -k https://localhost:8443/api/processes"
echo ""

# Show documentation
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Documentation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  📖 README.md - Main documentation"
echo "  📖 docs/installation.md - Installation guide"
echo "  📖 docs/configuration.md - Configuration reference"
echo "  📖 docs/api/README.md - API documentation"
echo "  📖 CONTRIBUTING.md - Contribution guidelines"
echo "  📖 IMPLEMENTATION_SUMMARY.md - Implementation details"
echo ""

# Offer to start the platform
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Would you like to start the platform now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting MasterChief Platform..."
    echo ""
    
    # Check for Docker
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        echo "Docker detected. Starting with Docker Compose..."
        docker-compose up -d
        echo ""
        echo "Platform started!"
        echo "Access the API at: https://localhost:8443"
        echo "Access Grafana at: http://localhost:3000 (admin/admin)"
        echo ""
        echo "View logs: docker-compose logs -f"
    else
        echo "Starting platform directly..."
        python3 platform/main.py
    fi
else
    echo "You can start the platform later with: ./start.sh"
fi

echo ""
echo "Thank you for trying MasterChief Platform!"
