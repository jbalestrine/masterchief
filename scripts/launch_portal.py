#!/usr/bin/env python3
"""
MasterChief Web Portal Launcher
Starts both the Flask backend API and optionally the React frontend
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("  MasterChief DevOps Platform - Web Portal")
    print("=" * 60)
    print()

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    # Check Python packages
    try:
        import flask
        import flask_cors
        import yaml
        print("✓ Python dependencies OK")
    except ImportError as e:
        print(f"✗ Missing Python dependency: {e}")
        print("  Run: pip install -r requirements.txt")
        return False
    
    return True

def start_backend():
    """Start the Flask backend API"""
    print("\nStarting Backend API...")
    print("-" * 60)
    
    # Add current directory to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    from platform.api import create_app
    
    config = {
        'SECRET_KEY': 'dev-secret-key-change-in-production',
        'DEBUG': True,
        'MAX_CONTENT_LENGTH': 100 * 1024 * 1024,  # 100MB max file upload
    }
    
    app = create_app(config)
    
    print("✓ Backend API ready")
    print(f"  URL: http://localhost:5000")
    print(f"  API: http://localhost:5000/api")
    print()
    print("Available endpoints:")
    print("  - GET  /api/plugins/           - List plugins")
    print("  - POST /api/plugins/upload     - Upload plugin")
    print("  - GET  /api/deployments/       - List deployments")
    print("  - POST /api/deployments/start  - Start deployment")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n\nShutting down...")

def start_frontend():
    """Instructions for starting the frontend"""
    print("\nTo start the React frontend:")
    print("-" * 60)
    print("  cd platform/portal")
    print("  npm install")
    print("  npm run dev")
    print()
    print("Frontend will be available at: http://localhost:3000")
    print("-" * 60)

def main():
    """Main entry point"""
    print_banner()
    
    if not check_dependencies():
        sys.exit(1)
    
    print("\nStartup mode:")
    print("  1. Backend only (Flask API)")
    print("  2. Show frontend instructions")
    print()
    
    choice = input("Select mode [1]: ").strip() or "1"
    
    if choice == "1":
        start_backend()
    elif choice == "2":
        start_frontend()
        print("\nOnce frontend is running, open http://localhost:3000 in your browser")
    else:
        print("Invalid choice")
        sys.exit(1)

if __name__ == "__main__":
    main()
