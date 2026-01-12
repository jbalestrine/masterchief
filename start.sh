#!/bin/bash
# MasterChief Platform Startup Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================"
echo "Starting MasterChief Platform"
echo "======================================"

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "Warning: Running as root. Consider using a dedicated user."
fi

# Check if Docker is available
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "Docker detected. Starting with Docker Compose..."
    docker-compose up -d
    
    echo ""
    echo "======================================"
    echo "Platform started!"
    echo "======================================"
    echo ""
    echo "Access the platform at:"
    echo "  API: https://localhost:8443"
    echo "  Grafana: http://localhost:3000"
    echo "  Prometheus: http://localhost:9090"
    echo ""
    echo "View logs with: docker-compose logs -f"
    echo "Stop with: docker-compose down"
    
else
    echo "Starting platform directly..."
    
    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        echo "Error: Python 3 is required but not found."
        exit 1
    fi
    
    # Check if dependencies are installed
    if ! python3 -c "import flask" 2>/dev/null; then
        echo "Installing dependencies..."
        pip3 install -r requirements.txt
    fi
    
    # Start the platform
    python3 platform/main.py
fi
