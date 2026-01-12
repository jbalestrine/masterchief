"""Dashboard management commands."""

import subprocess
import time
from pathlib import Path
import click


@click.group()
def dashboard():
    """Manage the Mission Control Dashboard."""
    pass


@dashboard.command("start")
@click.option("--port", default=5000, help="Port to run dashboard on")
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--dev", is_flag=True, help="Run in development mode")
@click.pass_context
def dashboard_start(ctx, port, host, dev):
    """Start the Mission Control Dashboard server."""
    click.echo("🚀 Starting Mission Control Dashboard...")
    click.echo(f"   Host: {host}")
    click.echo(f"   Port: {port}")
    click.echo(f"   Mode: {'Development' if dev else 'Production'}")
    click.echo("-" * 60)
    
    # Check if platform app exists
    app_file = Path("platform/app.py")
    if not app_file.exists():
        click.echo("✗ Dashboard application not found", err=True)
        return
    
    env = {
        "FLASK_APP": "platform.app",
        "FLASK_ENV": "development" if dev else "production",
        "DASHBOARD_PORT": str(port),
        "DASHBOARD_HOST": host
    }
    
    try:
        # Start Flask application
        cmd = ["python", "-m", "flask", "run", "--host", host, "--port", str(port)]
        
        if dev:
            click.echo("\n📊 Dashboard starting at http://{}:{}".format(host, port))
            click.echo("Press Ctrl+C to stop\n")
        
        subprocess.run(cmd, env={**subprocess.os.environ, **env})
        
    except KeyboardInterrupt:
        click.echo("\n\n✓ Dashboard stopped")
    except Exception as e:
        click.echo(f"\n✗ Error starting dashboard: {e}", err=True)


@dashboard.command("stop")
@click.pass_context
def dashboard_stop(ctx):
    """Stop the Mission Control Dashboard server."""
    click.echo("🛑 Stopping Mission Control Dashboard...")
    
    try:
        # Find and kill Flask process
        result = subprocess.run(
            ["pgrep", "-f", "flask run"],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                subprocess.run(["kill", pid])
            click.echo("✓ Dashboard stopped")
        else:
            click.echo("⚠ Dashboard is not running")
            
    except Exception as e:
        click.echo(f"✗ Error stopping dashboard: {e}", err=True)


@dashboard.command("status")
@click.pass_context
def dashboard_status(ctx):
    """Check Dashboard server status."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "flask run"],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            click.echo("✓ Dashboard is running")
            pids = result.stdout.strip().split('\n')
            click.echo(f"  PIDs: {', '.join(pids)}")
        else:
            click.echo("○ Dashboard is not running")
            
    except Exception as e:
        click.echo(f"✗ Error checking status: {e}", err=True)
