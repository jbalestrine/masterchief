#!/usr/bin/env python3
"""
MasterChief Platform - Structure Validation
Validates that all required files and modules are present
"""

import os
import sys
from pathlib import Path

def check_file(path, description):
    """Check if a file exists"""
    if Path(path).exists():
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} - MISSING: {path}")
        return False

def check_directory(path, description):
    """Check if a directory exists"""
    if Path(path).is_dir():
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} - MISSING: {path}")
        return False

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   MasterChief Platform - Structure Validation             ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    os.chdir(Path(__file__).parent)
    passed = 0
    failed = 0
    
    # Core files
    print("Core Files:")
    checks = [
        ("README.md", "Main README"),
        ("LICENSE", "License file"),
        ("requirements.txt", "Python dependencies"),
        ("config.yml", "Configuration file"),
        ("Dockerfile", "Docker image definition"),
        ("docker-compose.yml", "Docker Compose orchestration"),
        ("install.sh", "Installation script"),
        ("start.sh", "Startup script"),
        (".gitignore", "Git ignore file"),
        ("CONTRIBUTING.md", "Contributing guidelines"),
        ("IMPLEMENTATION_SUMMARY.md", "Implementation summary"),
        ("demo.sh", "Demo script"),
    ]
    for path, desc in checks:
        if check_file(path, desc):
            passed += 1
        else:
            failed += 1
    print()
    
    # Platform modules
    print("Platform Modules:")
    checks = [
        ("platform/main.py", "Main entry point"),
        ("platform/api.py", "Flask API"),
        ("platform/config.py", "Configuration management"),
        ("platform/services/manager.py", "Service manager"),
        ("platform/services/api.py", "Service API"),
        ("platform/processes/manager.py", "Process manager"),
        ("platform/processes/api.py", "Process API"),
        ("platform/packages/manager.py", "Package manager"),
        ("platform/packages/api.py", "Package API"),
        ("platform/bare-metal/hardware.py", "Hardware discovery"),
        ("platform/bare-metal/storage.py", "Storage management"),
        ("platform/bare-metal/network.py", "Network management"),
        ("platform/bare-metal/api.py", "Bare metal API"),
        ("platform/users/api.py", "User management API"),
        ("platform/cmdb/api.py", "CMDB API"),
        ("platform/backup/api.py", "Backup API"),
        ("platform/monitoring/api.py", "Monitoring API"),
        ("platform/web-ide/api.py", "Web IDE API"),
    ]
    for path, desc in checks:
        if check_file(path, desc):
            passed += 1
        else:
            failed += 1
    print()
    
    # Addons
    print("Addons:")
    checks = [
        ("addons/shoutcast/manager.py", "Shoutcast manager"),
        ("addons/jamroom/manager.py", "Jamroom manager"),
        ("addons/scripts/manager.py", "Script manager"),
    ]
    for path, desc in checks:
        if check_file(path, desc):
            passed += 1
        else:
            failed += 1
    print()
    
    # OS distribution
    print("OS Distribution:")
    checks = [
        ("os/iso-builder/build.sh", "ISO builder script"),
        ("os/iso-builder/packages/base.list", "Base packages"),
        ("os/iso-builder/packages/devops.list", "DevOps packages"),
        ("os/iso-builder/scripts/customize.sh", "Customization script"),
        ("os/iso-builder/scripts/install-platform.sh", "Platform installer"),
        ("os/iso-builder/preseed/preseed.cfg", "Debian preseed"),
        ("os/iso-builder/preseed/kickstart.cfg", "RHEL kickstart"),
        ("os/usb-creator/create-usb.sh", "USB creator"),
        ("os/first-boot/wizard.sh", "First boot wizard"),
    ]
    for path, desc in checks:
        if check_file(path, desc):
            passed += 1
        else:
            failed += 1
    print()
    
    # Documentation
    print("Documentation:")
    checks = [
        ("docs/installation.md", "Installation guide"),
        ("docs/configuration.md", "Configuration guide"),
        ("docs/api/README.md", "API documentation"),
        ("platform/README.md", "Platform documentation"),
        ("addons/README.md", "Addons documentation"),
        ("os/base/README.md", "Base OS documentation"),
    ]
    for path, desc in checks:
        if check_file(path, desc):
            passed += 1
        else:
            failed += 1
    print()
    
    # Directories
    print("Directory Structure:")
    checks = [
        ("platform", "Platform directory"),
        ("addons", "Addons directory"),
        ("os", "OS directory"),
        ("docs", "Documentation directory"),
        ("scripts", "Scripts directory"),
    ]
    for path, desc in checks:
        if check_directory(path, desc):
            passed += 1
        else:
            failed += 1
    print()
    
    # Summary
    print("═" * 60)
    print(f"Validation Results:")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Total:  {passed + failed}")
    print("═" * 60)
    
    if failed == 0:
        print()
        print("✓ All checks passed! Platform structure is complete.")
        print()
        return 0
    else:
        print()
        print(f"✗ {failed} checks failed. Please review the missing files.")
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
