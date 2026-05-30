"""
MasterChief entry point — launches the Flask web GUI directly.

This replaces the old core.cli.main entry point which routed through
the legacy CLI framework.  Now `masterchief` (or `masterchief --port 9090`)
starts the web dashboard immediately.
"""
import os
import sys
import subprocess
from pathlib import Path


def _find_main_py():
    """Locate main.py in priority order."""
    candidates = [
        # 1. Current working directory (dev / repo checkout)
        Path.cwd() / "main.py",
        # 2. Alongside this file (source tree)
        Path(__file__).resolve().parent / "main.py",
        # 3. Installed data_files: {sys.prefix}/share/masterchief/
        Path(sys.prefix) / "share" / "masterchief" / "main.py",
        # 4. Venv base prefix
        Path(sys.base_prefix) / "share" / "masterchief" / "main.py",
    ]
    for c in candidates:
        if c.exists():
            return c.resolve()
    return None


def main():
    """Entry point for `masterchief` console_script."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="masterchief",
        description="MasterChief DevOps Platform — Web Dashboard",
    )
    parser.add_argument(
        "--port", "-p", type=int, default=8080,
        help="Port to run on (default: 8080)",
    )
    parser.add_argument(
        "--host", type=str, default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--debug", "-d", action="store_true",
        help="Run in debug mode",
    )

    args = parser.parse_args()

    main_py = _find_main_py()
    if not main_py:
        print("Error: Cannot find main.py (web GUI)")
        print("")
        print("Options:")
        print("  1. Run from the repo directory:  cd masterchief && masterchief")
        print("  2. Re-install the package:       pip install --force-reinstall masterchief")
        raise SystemExit(1)

    print("=" * 70)
    print("MasterChief DevOps Platform  —  Web Dashboard")
    print("=" * 70)
    print(f"  main.py : {main_py}")
    print(f"  host    : {args.host}")
    print(f"  port    : {args.port}")
    print(f"  debug   : {args.debug}")
    print("=" * 70)

    cmd = [sys.executable, str(main_py), "--port", str(args.port)]
    if args.debug:
        cmd.append("--debug")

    try:
        # cwd = main.py's parent so relative HTML / static paths resolve
        subprocess.run(cmd, cwd=str(main_py.parent))
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
