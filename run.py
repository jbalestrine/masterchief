#!/usr/bin/env python3
"""
MasterChief DevOps Platform
===========================

ONE FILE TO RUN IT ALL!

Just run: python run.py

Everything starts automatically including:
- Web GUI for data upload
- REST API 
- All platform features
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
    for dir_name in ['data', 'logs', 'plugins', 'backups', 'data/custom_scripts',
                     'data/uploads', 'data/training']:
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
    ║  🌙 DATA UPLOAD WEB GUI:                                          ║
    ║     http://localhost:8080/api/v1/data/upload                      ║
    ║                                                                    ║
    ║  Other Features:                                                   ║
    ║     API:        http://localhost:8080/api/v1                      ║
    ║     Dashboard:  http://localhost:8080/dashboard                   ║
    ╠═══════════════════════════════════════════════════════════════════╣
    ║  📤 Upload training data for Echo                                 ║
    ║  📁 Browse and manage files                                       ║
    ║  ⚙️  View statistics and analytics                                ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # Add platform to path
    sys.path.insert(0, str(base_dir / 'platform'))
    
    try:
        from platform.app import create_app, run_app
        
        print("\n🚀 Starting MasterChief Platform...")
        print("   This may take a few seconds...\n")
        
        # Create the app
        app = create_app()
        
        # Run the server
        print("✅ Platform ready!")
        print("   Open your browser to: http://localhost:8080/api/v1/data/upload\n")
        
        run_app(app, host='0.0.0.0', port=8080, debug=False)
        
    except ImportError as e:
        print(f"❌ Error: Failed to import platform modules: {e}")
        print("\n💡 Make sure you have installed the required dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down MasterChief platform...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
