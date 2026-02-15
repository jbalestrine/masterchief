#!/usr/bin/env python3
"""
MasterChief Setup Runner
Starts the Flask application and directs to setup wizard if authentication is not configured
"""

import os
import sys
import webbrowser
import time
import subprocess
from pathlib import Path

def check_auth_configured():
    """Check if authentication is configured"""
    env_file = Path('.env')
    if not env_file.exists():
        return False

    required_configs = {
        'azure': ['AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET', 'AZURE_TENANT_ID'],
        'okta': ['OKTA_CLIENT_ID', 'OKTA_CLIENT_SECRET', 'OKTA_DOMAIN'],
        'github': ['GITHUB_CLIENT_ID', 'GITHUB_CLIENT_SECRET']
    }

    configured_providers = []
    with open(env_file, 'r') as f:
        env_vars = {}
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value

    for provider, keys in required_configs.items():
        if all(env_vars.get(key) for key in keys):
            configured_providers.append(provider)

    return len(configured_providers) > 0

def main():
    """Main setup runner"""
    print("🚀 MasterChief Setup Runner")
    print("=" * 50)

    # Check if authentication is configured
    auth_configured = check_auth_configured()

    if auth_configured:
        print("✅ Authentication appears to be configured")
        print("Starting MasterChief application...")
        start_url = "http://localhost:5000/web-ide"
    else:
        print("🔧 Authentication not configured")
        print("Starting setup wizard...")
        start_url = "http://localhost:5000/setup"

    print(f"Opening {start_url} in your browser...")

    # Start the Flask application
    try:
        # Import and run the main app
        from main import app

        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open(start_url)

        import threading
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()

        # Run the app
        print("Starting Flask application on http://localhost:5000")
        print("Press Ctrl+C to stop")
        app.run(host='0.0.0.0', port=5000, debug=True)

    except KeyboardInterrupt:
        print("\n👋 Shutting down MasterChief")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()