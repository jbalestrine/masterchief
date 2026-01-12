"""Script management commands."""

import os
import sys
import subprocess
from pathlib import Path
import click


@click.group()
def script():
    """Manage and execute DevOps scripts."""
    pass


@script.command("list")
@click.option("--category", help="Filter by category (deployment, monitoring, etc.)")
@click.pass_context
def script_list(ctx, category):
    """List available DevOps scripts."""
    scripts_dir = Path("scripts/devops")
    
    if not scripts_dir.exists():
        click.echo("✗ Scripts directory not found", err=True)
        return
    
    click.echo("\n📜 Available Scripts:")
    click.echo("=" * 80)
    
    categories = {}
    
    for cat_dir in scripts_dir.iterdir():
        if cat_dir.is_dir():
            cat_name = cat_dir.name
            if category and cat_name != category:
                continue
            
            scripts = [f for f in cat_dir.glob("*.sh") if f.is_file()]
            if scripts:
                categories[cat_name] = scripts
    
    for cat_name, scripts in sorted(categories.items()):
        click.echo(f"\n{cat_name.upper()}:")
        click.echo("-" * 40)
        for script_path in sorted(scripts):
            click.echo(f"  • {script_path.name}")
    
    total = sum(len(s) for s in categories.values())
    click.echo(f"\nTotal: {total} scripts across {len(categories)} categories")


@script.command("run")
@click.argument("script_name")
@click.argument("args", nargs=-1)
@click.option("--category", help="Script category")
@click.pass_context
def script_run(ctx, script_name, args, category):
    """Execute a DevOps script.
    
    Examples:
        masterchief script run deploy-app.sh --app myapp --env prod
        masterchief script run check-health.sh --category monitoring --url http://localhost
    """
    scripts_dir = Path("scripts/devops")
    
    # Find script
    script_path = None
    if category:
        # Look in specific category
        cat_path = scripts_dir / category / script_name
        if cat_path.exists():
            script_path = cat_path
    else:
        # Search all categories
        for cat_dir in scripts_dir.iterdir():
            if cat_dir.is_dir():
                potential_path = cat_dir / script_name
                if potential_path.exists():
                    script_path = potential_path
                    break
    
    if not script_path:
        click.echo(f"✗ Script not found: {script_name}", err=True)
        click.echo("Use 'masterchief script list' to see available scripts")
        return
    
    # Execute script
    click.echo(f"🚀 Executing: {script_path}")
    click.echo("-" * 40)
    
    try:
        result = subprocess.run(
            [str(script_path)] + list(args),
            cwd=os.getcwd(),
            check=False
        )
        
        if result.returncode == 0:
            click.echo("-" * 40)
            click.echo("✓ Script completed successfully")
        else:
            click.echo("-" * 40)
            click.echo(f"✗ Script failed with exit code: {result.returncode}", err=True)
            
    except Exception as e:
        click.echo(f"✗ Error executing script: {e}", err=True)


@script.command("generate")
@click.option("--template", help="Template to use", required=True)
@click.option("--output", help="Output path for generated script")
@click.pass_context
def script_generate(ctx, template, output):
    """Generate a custom script using the Script Wizard."""
    try:
        from platform.script_wizard import ScriptWizard
        
        wizard = ScriptWizard()
        templates = wizard.list_templates()
        
        # Check if template exists
        template_ids = [t["id"] for t in templates]
        if template not in template_ids:
            click.echo(f"✗ Template not found: {template}", err=True)
            click.echo(f"Available templates: {', '.join(template_ids)}")
            return
        
        # Collect parameters interactively
        click.echo(f"📝 Generating script from template: {template}")
        click.echo("=" * 60)
        
        parameters = {}
        
        # Example: deployment template parameters
        if template == "deployment":
            parameters["app_name"] = click.prompt("Application name")
            parameters["environment"] = click.prompt(
                "Environment",
                type=click.Choice(["dev", "staging", "prod"])
            )
        elif template == "monitoring":
            parameters["target"] = click.prompt("Monitoring target")
        
        # Generate script
        script_content = wizard.generate_script(template, parameters)
        
        if output:
            with open(output, 'w') as f:
                f.write(script_content)
            os.chmod(output, 0o755)
            click.echo(f"\n✓ Script generated: {output}")
        else:
            click.echo("\nGenerated script:")
            click.echo("=" * 60)
            click.echo(script_content)
            
    except ImportError:
        click.echo("✗ Script Wizard module not available", err=True)
        click.echo("  Install dependencies: pip install -r requirements.txt")
    except Exception as e:
        click.echo(f"✗ Error generating script: {e}", err=True)


@script.command("validate")
@click.argument("script_path", type=click.Path(exists=True))
@click.pass_context
def script_validate(ctx, script_path):
    """Validate a shell script using shellcheck (if available)."""
    script_file = Path(script_path)
    
    if not script_file.suffix == ".sh":
        click.echo("✗ Not a shell script", err=True)
        return
    
    click.echo(f"🔍 Validating: {script_path}")
    
    # Try shellcheck if available
    try:
        result = subprocess.run(
            ["shellcheck", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # Run shellcheck
            result = subprocess.run(
                ["shellcheck", script_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                click.echo("✓ Script validation passed")
            else:
                click.echo("✗ Validation issues found:")
                click.echo(result.stdout)
        else:
            click.echo("⚠ shellcheck not available, skipping validation")
    except FileNotFoundError:
        click.echo("⚠ shellcheck not installed, skipping validation")
        click.echo("  Install with: apt-get install shellcheck")


@script.command("generate-ai")
@click.option("--description", "-d", help="Description of what the code should do")
@click.option("--language", "-l", 
              type=click.Choice(["bash", "python", "powershell"], case_sensitive=False),
              default="bash",
              help="Target programming language")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--no-comments", is_flag=True, help="Exclude comments from generated code")
@click.option("--no-error-handling", is_flag=True, help="Exclude error handling")
@click.option("--model", default="codellama", help="Ollama model to use (default: codellama)")
@click.pass_context
def generate_ai(ctx, description, language, output, no_comments, no_error_handling, model):
    """Generate code using AI based on natural language description.
    
    Examples:
        # Interactive mode (will prompt for description)
        masterchief script generate-ai
        
        # Direct mode with description
        masterchief script generate-ai -d "backup database to S3" -l python -o backup.py
        
        # Generate bash script with minimal options
        masterchief script generate-ai -d "deploy app to kubernetes" --no-comments
    """
    try:
        from addons.scripts.ai_generator import AIScriptGenerator
    except ImportError:
        click.echo("✗ AI Script Generator not available", err=True)
        click.echo("  Install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    
    # Initialize the AI generator
    generator = AIScriptGenerator(model=model)
    
    # Check if Ollama is available
    click.echo("🔍 Checking Ollama availability...")
    if not generator.check_availability():
        click.echo("✗ Ollama is not available or model is not loaded", err=True)
        click.echo("\nTo use this feature:")
        click.echo("  1. Install Ollama: https://ollama.ai")
        click.echo(f"  2. Pull the model: ollama pull {model}")
        click.echo("  3. Ensure Ollama is running: ollama serve")
        sys.exit(1)
    
    click.echo(f"✓ Ollama is available with model: {model}\n")
    
    # Get description interactively if not provided
    if not description:
        click.echo("🤖 AI-Powered Code Generator")
        click.echo("=" * 60)
        click.echo("Describe what you want the code to do. Be as specific as possible.\n")
        
        description = click.prompt(
            "What should the code do?",
            type=str
        )
        
        if not description or description.strip() == "":
            click.echo("✗ Description cannot be empty", err=True)
            sys.exit(1)
    
    # Show generation parameters
    click.echo("\n📝 Generation Parameters:")
    click.echo(f"  • Language: {language}")
    click.echo(f"  • Description: {description}")
    click.echo(f"  • Include comments: {not no_comments}")
    click.echo(f"  • Include error handling: {not no_error_handling}")
    click.echo(f"  • Model: {model}")
    
    # Confirm generation
    if not click.confirm("\nProceed with code generation?", default=True):
        click.echo("Cancelled.")
        return
    
    # Generate the code
    click.echo("\n🚀 Generating code... (this may take a moment)")
    
    try:
        generated = generator.generate(
            description=description,
            language=language,
            include_comments=not no_comments,
            include_error_handling=not no_error_handling
        )
        
        click.echo("✓ Code generated successfully!\n")
        
        # Display or save the generated code
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                f.write(generated.content)
            
            # Make executable if it's a script
            if language in ["bash", "shell", "sh"]:
                os.chmod(output_path, 0o755)
            
            click.echo(f"💾 Code saved to: {output_path}")
            click.echo(f"   Language: {generated.language}")
            click.echo(f"   Description: {generated.description}")
            
            # Ask if user wants to see the code
            if click.confirm("\nDisplay the generated code?", default=True):
                click.echo("\n" + "=" * 60)
                click.echo(generated.content)
                click.echo("=" * 60)
        else:
            # Display the code
            click.echo("Generated code:")
            click.echo("=" * 60)
            click.echo(generated.content)
            click.echo("=" * 60)
            
            # Ask if user wants to save it
            if click.confirm("\nSave this code to a file?", default=False):
                save_path = click.prompt(
                    "Enter file path",
                    default=generated.name,
                    type=str
                )
                
                save_path = Path(save_path)
                save_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(save_path, 'w') as f:
                    f.write(generated.content)
                
                # Make executable if it's a script
                if language in ["bash", "shell", "sh"]:
                    os.chmod(save_path, 0o755)
                
                click.echo(f"✓ Code saved to: {save_path}")
        
    except Exception as e:
        click.echo(f"✗ Error generating code: {e}", err=True)
        if ctx.obj.get("verbose"):
            import traceback
            click.echo(traceback.format_exc())
        sys.exit(1)
