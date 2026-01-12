#!/usr/bin/env python3
"""
MasterChief DevOps Platform
===========================

Just run: python run.py

That's it. Everything starts automatically.
"""
import os
import sys
from pathlib import Path

def main():
    """Main entry point for MasterChief platform."""
    # Ensure we're in the right directory
    base_dir = Path(__file__).parent
    os.chdir(base_dir)
    
    # Ensure directories exist
    for dir_name in ['data', 'logs', 'plugins', 'backups', 'data/custom_scripts']:
        dir_path = base_dir / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Add core to path for Echo import
    sys.path.insert(0, str(base_dir))
    
    # Display Echo's greeting
    try:
        from core.echo import echo_startup_display
        print(echo_startup_display())
        print()  # Add spacing
    except ImportError:
        pass  # If Echo module isn't available, continue without it
    
    # Print banner
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║           MasterChief DevOps Automation Platform                  ║
    ╠═══════════════════════════════════════════════════════════════════╣
    ║  Web UI:     http://localhost:8080                                ║
    ║  API:        http://localhost:8080/api/v1                         ║
    ║  WebSocket:  ws://localhost:8080/socket.io                        ║
    ╠═══════════════════════════════════════════════════════════════════╣
    ║  Dashboard:  http://localhost:8080/dashboard                      ║
    ║  Scripts:    http://localhost:8080/scripts                        ║
    ║  Plugins:    http://localhost:8080/plugins                        ║
    ╠═══════════════════════════════════════════════════════════════════╣
    ║  CLI:        masterchief --help                                   ║
    ║  IRC Bot:    !help (when connected)                               ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # Add platform to path
    sys.path.insert(0, str(base_dir / 'platform'))
    
    try:
        from platform.app import create_app, run_server
        run_server()
    except ImportError as e:
        print(f"Error: Failed to import platform modules: {e}")
        print("\nMake sure you have installed the required dependencies:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nShutting down MasterChief platform...")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
