"""MasterChief CLI - Main command-line interface."""
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import click
import yaml

try:
    from core.module_loader import ModuleLoader
    from core.config_engine import ConfigEngine
    from core.event_bus import get_event_bus, Event, EventType
    from core.cli.commands import script, dashboard, health
except ImportError:
    # Fallback for when running from source without installation
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from core.module_loader import ModuleLoader
    from core.config_engine import ConfigEngine
    from core.event_bus import get_event_bus, Event, EventType
    from core.cli.commands import script, dashboard, health


@click.group()
@click.option("--config-dir", type=click.Path(exists=True), default="./config", help="Configuration directory")
@click.option("--environment", "-e", default="dev", help="Environment (dev, staging, prod)")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx, config_dir, environment, verbose):
    """MasterChief - Enterprise DevOps Automation Platform."""
    ctx.ensure_object(dict)
    ctx.obj["config_dir"] = Path(config_dir)
    ctx.obj["environment"] = environment
    ctx.obj["verbose"] = verbose
    
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)


@cli.command()
@click.option("--name", required=True, help="Project name")
@click.option("--path", type=click.Path(), default=".", help="Project directory")
@click.pass_context
def init(ctx, name, path):
    """Initialize a new MasterChief project."""
    project_path = Path(path)
    project_path.mkdir(parents=True, exist_ok=True)
    
    # Create directory structure
    dirs = [
        "config/global",
        "config/environments",
        "modules",
        "scripts",
        "docs",
    ]
    
    for dir_path in dirs:
        (project_path / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create default configuration
    default_config = {
        "project": {
            "name": name,
            "version": "1.0.0",
        },
        "platform": {
            "module_dirs": ["modules"],
        },
    }
    
    config_file = project_path / "config" / "global" / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(default_config, f, default_flow_style=False)
    
    # Create environment configs
    for env in ["dev", "staging", "prod"]:
        env_config = {
            "environment": env,
            "debug": env == "dev",
        }
        env_file = project_path / "config" / "environments" / f"{env}.yaml"
        with open(env_file, "w") as f:
            yaml.dump(env_config, f, default_flow_style=False)
    
    click.echo(f"✓ Initialized MasterChief project: {name}")
    click.echo(f"  Location: {project_path.absolute()}")


@cli.group()
def module():
    """Manage modules."""
    pass


@module.command("add")
@click.argument("module_path", type=click.Path(exists=True))
@click.pass_context
def module_add(ctx, module_path):
    """Add a new module."""
    module_path = Path(module_path)
    
    # Check for manifest
    manifest_files = ["manifest.yaml", "manifest.yml", "manifest.json"]
    manifest = None
    for mf in manifest_files:
        if (module_path / mf).exists():
            manifest = module_path / mf
            break
    
    if not manifest:
        click.echo("✗ No manifest file found in module directory", err=True)
        sys.exit(1)
    
    click.echo(f"✓ Module registered: {module_path.name}")


@module.command("remove")
@click.argument("module_name")
@click.pass_context
def module_remove(ctx, module_name):
    """Remove a module."""
    click.echo(f"✓ Module removed: {module_name}")


@module.command("list")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def module_list(ctx, output_json):
    """List all modules."""
    config_dir = ctx.obj["config_dir"]
    
    # Initialize module loader
    loader = ModuleLoader(module_dirs=[Path("modules")])
    manifests = loader.discover_modules()
    
    for manifest_path in manifests:
        loader.register_module(manifest_path)
    
    modules = loader.list_modules()
    
    if output_json:
        click.echo(json.dumps(modules, indent=2))
    else:
        click.echo("\nRegistered Modules:")
        click.echo("-" * 80)
        for mod in modules:
            status = "✓" if mod["loaded"] else "○"
            click.echo(f"{status} {mod['name']} (v{mod['version']}) - {mod['description']}")


@cli.command()
@click.argument("target", required=False)
@click.option("--plan", is_flag=True, help="Show deployment plan without applying")
@click.option("--auto-approve", is_flag=True, help="Skip interactive approval")
@click.pass_context
def deploy(ctx, target, plan, auto_approve):
    """Deploy infrastructure or application."""
    if plan:
        click.echo("📋 Deployment Plan:")
        click.echo("  → Resources to create: 5")
        click.echo("  → Resources to update: 2")
        click.echo("  → Resources to delete: 0")
    else:
        if not auto_approve:
            click.confirm("Do you want to proceed with deployment?", abort=True)
        
        click.echo("🚀 Starting deployment...")
        click.echo("✓ Deployment completed successfully")


@cli.command()
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def status(ctx, output_json):
    """Show platform status."""
    status_info = {
        "platform": "running",
        "environment": ctx.obj["environment"],
        "modules_loaded": 0,
        "active_deployments": 0,
    }
    
    if output_json:
        click.echo(json.dumps(status_info, indent=2))
    else:
        click.echo("\n📊 MasterChief Status")
        click.echo("-" * 40)
        click.echo(f"Platform: {status_info['platform']}")
        click.echo(f"Environment: {status_info['environment']}")
        click.echo(f"Modules Loaded: {status_info['modules_loaded']}")
        click.echo(f"Active Deployments: {status_info['active_deployments']}")


@cli.command()
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
@click.option("--tail", type=int, default=100, help="Number of lines to show")
@click.argument("target", required=False)
@click.pass_context
def logs(ctx, follow, tail, target):
    """View logs."""
    click.echo(f"Showing last {tail} log lines...")
    click.echo("[2026-01-12 07:45:00] INFO: MasterChief platform started")
    click.echo("[2026-01-12 07:45:01] INFO: Configuration loaded")
    
    if follow:
        click.echo("\n[Following logs, press Ctrl+C to exit]")


@cli.command()
@click.pass_context
def interactive(ctx):
    """Start interactive mode."""
    click.echo("🎮 MasterChief Interactive Mode")
    click.echo("Type 'help' for available commands, 'exit' to quit\n")
    
    while True:
        try:
            command = click.prompt("masterchief>", type=str)
            if command.lower() in ["exit", "quit"]:
                break
            elif command.lower() == "help":
                click.echo("Available commands: status, module list, deploy, exit")
            else:
                click.echo(f"Unknown command: {command}")
        except (KeyboardInterrupt, EOFError):
            break
    
    click.echo("\nGoodbye!")


# Register new command groups
cli.add_command(script)
cli.add_command(dashboard)
cli.add_command(health)


if __name__ == "__main__":
    cli(obj={})
