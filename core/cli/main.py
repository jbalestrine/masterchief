"""Command-line interface for MasterChief.

This module provides the main CLI interface for the MasterChief platform.
"""

import click
import sys
# Line 9 - Missing type stubs for yaml - will be fixed by adding types-PyYAML
import yaml

from typing import Optional


@click.group()
def cli():
    """MasterChief Platform CLI"""
    pass


@cli.command()
@click.option('--config', '-c', default='config.yml', help='Configuration file path')
def init(config: str):
    """Initialize the MasterChief platform."""
    click.echo(f"Initializing MasterChief platform with config: {config}")
    
    try:
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
            click.echo("Configuration loaded successfully")
    except Exception as e:
        click.echo(f"Error loading configuration: {e}", err=True)
        sys.exit(1)


@cli.command()
def status():
    """Show platform status."""
    click.echo("MasterChief Platform Status")
    click.echo("===========================")
    click.echo("Status: Running")


@cli.command()
@click.argument('module_name')
def load(module_name: str):
    """Load a module."""
    click.echo(f"Loading module: {module_name}")


@cli.command()
@click.argument('module_name')
def unload(module_name: str):
    """Unload a module."""
    click.echo(f"Unloading module: {module_name}")


if __name__ == '__main__':
    cli()
