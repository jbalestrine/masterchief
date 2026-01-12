#!/usr/bin/env python3
"""
Show Echo - Display Echo Starlite's Visual Representation
==========================================================

Simple script to display Echo's image or ASCII art.

Usage:
    python show_echo.py              # Show image path or ASCII art
    python show_echo.py --ascii      # Force ASCII art display
    python show_echo.py --image      # Show image path
    python show_echo.py --open       # Open image in default viewer (if possible)
"""
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.echo import Echo, echo_full_display, echo_image_path


def open_image(image_path):
    """Try to open the image in the default viewer."""
    import platform
    import subprocess
    
    try:
        system = platform.system()
        if system == 'Darwin':  # macOS
            subprocess.run(['open', image_path], check=True)
        elif system == 'Windows':
            subprocess.run(['start', image_path], shell=True, check=True)
        else:  # Linux and others
            # Try common image viewers
            viewers = ['xdg-open', 'display', 'eog', 'feh']
            for viewer in viewers:
                try:
                    subprocess.run([viewer, image_path], check=True)
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            return False
        return True
    except Exception as e:
        print(f"Could not open image viewer: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Display Echo Starlite's visual representation"
    )
    parser.add_argument(
        '--ascii',
        action='store_true',
        help='Show ASCII art instead of image'
    )
    parser.add_argument(
        '--image',
        action='store_true',
        help='Show image path only'
    )
    parser.add_argument(
        '--open',
        action='store_true',
        help='Open image in default viewer'
    )
    
    args = parser.parse_args()
    
    # Handle --ascii flag
    if args.ascii:
        print(echo_full_display())
        return
    
    # Handle --image or --open flags
    if args.image or args.open:
        if Echo.has_image():
            image_path = echo_image_path()
            print(f"🌙 Echo Starlite Image Location:")
            print(f"   {image_path}")
            print()
            
            if args.open:
                print("Opening Echo's image...")
                if open_image(str(image_path)):
                    print("✨ Image opened successfully!")
                else:
                    print("Could not open image automatically.")
                    print(f"Please open manually: {image_path}")
        else:
            print("❌ Echo's image is not available.")
            print("   Run: python scripts/generate_echo_image.py")
        return
    
    # Default behavior: show image path if available, otherwise ASCII art
    if Echo.has_image():
        image_path = echo_image_path()
        print("🌙 Echo Starlite")
        print("=" * 50)
        print()
        print("📷 Image available at:")
        print(f"   {image_path}")
        print()
        print("✨ Use --open to open in image viewer")
        print("✨ Use --ascii to see ASCII art version")
        print()
        print("💜 floating beside you, always 🌙")
    else:
        print("Echo's image is not yet generated.")
        print("Showing ASCII art version:")
        print()
        print(echo_full_display())
        print()
        print("To generate Echo's image, run:")
        print("  python scripts/generate_echo_image.py")


if __name__ == "__main__":
    main()
