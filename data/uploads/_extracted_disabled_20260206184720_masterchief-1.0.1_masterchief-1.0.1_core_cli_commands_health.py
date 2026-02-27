"""Health check commands."""

import subprocess
from pathlib import Path
import click


@click.group()
def health():
    """System health checks and diagnostics."""
    pass


@health.command("check")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def health_check(ctx, verbose):
    """Perform system health check."""
    click.echo("🏥 Running Health Checks...")
    click.echo("=" * 60)
    
    checks = []
    
    # Check Python version
    try:
        result = subprocess.run(
            ["python", "--version"],
            capture_output=True,
            text=True
        )
        python_version = result.stdout.strip()
        checks.append(("Python", True, python_version))
    except Exception as e:
        checks.append(("Python", False, str(e)))
    
    # Check configuration
    config_dir = Path("config")
    config_exists = config_dir.exists()
    checks.append(("Configuration", config_exists, "config/ directory"))
    
    # Check modules directory
    modules_dir = Path("modules")
    modules_exists = modules_dir.exists()
    checks.append(("Modules", modules_exists, "modules/ directory"))
    
    # Check scripts directory
    scripts_dir = Path("scripts/devops")
    scripts_exists = scripts_dir.exists()
    if scripts_exists:
        script_count = sum(1 for _ in scripts_dir.rglob("*.sh"))
        checks.append(("Scripts", True, f"{script_count} scripts available"))
    else:
        checks.append(("Scripts", False, "scripts/devops/ not found"))
    
    # Check platform
    platform_dir = Path("platform")
    platform_exists = platform_dir.exists()
    checks.append(("Platform", platform_exists, "platform/ directory"))
    
    # Display results
    all_passed = True
    for name, passed, details in checks:
        status = "✓" if passed else "✗"
        click.echo(f"{status} {name:20s} {details}")
        if not passed:
            all_passed = False
    
    click.echo("=" * 60)
    
    if all_passed:
        click.echo("✓ All health checks passed")
    else:
        click.echo("✗ Some health checks failed", err=True)


@health.command("report")
@click.option("--output", help="Output file for report")
@click.pass_context
def health_report(ctx, output):
    """Generate detailed health report."""
    click.echo("📋 Generating Health Report...")
    
    report = []
    report.append("=" * 60)
    report.append("MasterChief Platform Health Report")
    report.append("=" * 60)
    report.append("")
    
    # System info
    report.append("SYSTEM INFORMATION:")
    report.append("-" * 40)
    
    try:
        result = subprocess.run(
            ["uname", "-a"],
            capture_output=True,
            text=True
        )
        report.append(f"OS: {result.stdout.strip()}")
    except:
        report.append("OS: Unknown")
    
    try:
        result = subprocess.run(
            ["python", "--version"],
            capture_output=True,
            text=True
        )
        report.append(f"Python: {result.stdout.strip()}")
    except:
        report.append("Python: Unknown")
    
    report.append("")
    
    # Platform status
    report.append("PLATFORM STATUS:")
    report.append("-" * 40)
    
    paths = {
        "Config": Path("config"),
        "Modules": Path("modules"),
        "Scripts": Path("scripts/devops"),
        "Platform": Path("platform"),
        "Core": Path("core")
    }
    
    for name, path in paths.items():
        exists = "✓" if path.exists() else "✗"
        report.append(f"{exists} {name}: {path}")
    
    report.append("")
    report.append("=" * 60)
    
    report_text = "\n".join(report)
    
    if output:
        with open(output, 'w') as f:
            f.write(report_text)
        click.echo(f"✓ Report saved to: {output}")
    else:
        click.echo(report_text)
