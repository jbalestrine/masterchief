#!/usr/bin/env python3
"""
MasterChief Complete Setup Script
Handles dependency installation, environment setup, and launches the setup wizard
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and return success status"""
    try:
        print(f"🔧 {description}")
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")

    # Upgrade pip first
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        print("⚠️  Warning: Could not upgrade pip, continuing...")

    # Install core dependencies (excluding problematic ones)
    core_deps = [
        "flask>=3.0.0",
        "flask-cors>=4.0.0",
        "flask-socketio>=5.3.0",
        "python-dotenv",
        "click>=8.1.0",
        "pyyaml>=6.0",
        "jinja2>=3.1.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.0.0",
        "redis>=5.0.0",
        "psycopg2-binary>=2.9.0",
        "sqlalchemy>=2.0.0"
    ]

    failed_core = []
    for dep in core_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            failed_core.append(dep)

    if failed_core:
        print(f"❌ Core dependency installation failed for: {', '.join(failed_core)}")
        return False

    print("✅ Core dependencies installed successfully")

    # Try to install optional dependencies (continue even if they fail)
    optional_deps = [
        ("pygame", "Voice features"),
        ("azure-identity", "Azure integration"),
        ("azure-mgmt-resource", "Azure resource management"),
        ("azure-mgmt-compute", "Azure compute management"),
        ("azure-mgmt-storage", "Azure storage management"),
        ("azure-mgmt-web", "Azure web app management"),
        ("PyGitHub", "GitHub integration"),
        ("Flask-Login", "User authentication"),
        ("Authlib", "OAuth authentication"),
        ("requests-oauthlib", "OAuth requests"),
        ("msal", "Microsoft authentication")
    ]

    print("\n🔧 Installing optional dependencies...")
    failed_optional = []

    for dep, description in optional_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep} ({description})"):
            failed_optional.append(f"{dep} ({description})")

    if failed_optional:
        print(f"⚠️  Some optional dependencies failed to install: {', '.join(failed_optional)}")
        print("The application will work with reduced functionality.")
    else:
        print("✅ All optional dependencies installed successfully")

    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path('.env')
    if not env_file.exists():
        print("\n📝 Creating .env file...")
        with open(env_file, 'w') as f:
            f.write("# MasterChief Environment Configuration\n")
            f.write("# Add your authentication credentials here\n\n")
            f.write("# Flask Configuration\n")
            f.write("SECRET_KEY=masterchief-secret-key-change-in-production\n\n")
            f.write("# Azure AD Configuration\n")
            f.write("# AZURE_CLIENT_ID=your-azure-client-id\n")
            f.write("# AZURE_CLIENT_SECRET=your-azure-client-secret\n")
            f.write("# AZURE_TENANT_ID=your-azure-tenant-id\n")
            f.write("# AZURE_SUBSCRIPTION_ID=your-azure-subscription-id\n\n")
            f.write("# OKTA Configuration\n")
            f.write("# OKTA_CLIENT_ID=your-okta-client-id\n")
            f.write("# OKTA_CLIENT_SECRET=your-okta-client-secret\n")
            f.write("# OKTA_DOMAIN=your-org.okta.com\n\n")
            f.write("# GitHub Configuration\n")
            f.write("# GITHUB_CLIENT_ID=your-github-client-id\n")
            f.write("# GITHUB_CLIENT_SECRET=your-github-client-secret\n")
        print("✅ .env file created")
    else:
        print("ℹ️  .env file already exists")

def test_imports():
    """Test that all modules can be imported"""
    print("\n🧪 Testing module imports...")

    modules_to_test = [
        ('flask', 'Flask'),
        ('auth_config', 'Authentication Config'),
        ('auth_module', 'Authentication Module'),
        ('azure_integration', 'Azure Integration'),
        ('github_integration', 'GitHub Integration'),
        ('app_management', 'App Management'),
        ('setup_wizard', 'Setup Wizard')
    ]

    failed_imports = []

    for module_name, description in modules_to_test:
        try:
            if module_name == 'flask':
                import flask
            elif module_name == 'auth_config':
                import auth_config
            elif module_name == 'auth_module':
                import auth_module
            elif module_name == 'azure_integration':
                import azure_integration
            elif module_name == 'github_integration':
                import github_integration
            elif module_name == 'app_management':
                import app_management
            elif module_name == 'setup_wizard':
                import setup_wizard
            print(f"✅ {description} - OK")
        except ImportError as e:
            print(f"⚠️  {description} - Import failed: {e}")
            failed_imports.append(description)

    if failed_imports:
        print(f"⚠️  Some modules failed to import: {', '.join(failed_imports)}")
        print("The application may work with reduced functionality.")
    else:
        print("✅ All modules imported successfully")

    return True

def main():
    """Main setup function"""
    print("🚀 MasterChief Complete Setup")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        sys.exit(1)

    # Create environment file
    create_env_file()

    # Test imports
    test_imports()

    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Configure your authentication credentials in the .env file")
    print("2. Run: python run_setup.py")
    print("3. Follow the setup wizard in your browser")
    print("\nOr run the setup wizard directly:")
    print("python run_setup.py")

    # Ask if user wants to start now
    try:
        response = input("\nWould you like to start MasterChief now? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            print("\n🚀 Starting MasterChief...")
            subprocess.run([sys.executable, 'run_setup.py'])
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled")

if __name__ == "__main__":
    main()