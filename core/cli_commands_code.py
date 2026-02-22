"""Code generation commands."""

import os
import sys
from pathlib import Path
import click


@click.group()
def code():
    """Generate code on demand with AI assistance."""
    pass


@code.command("generate")
@click.argument("description", required=False)
@click.option("--language", "-l",
              type=click.Choice(["bash", "python", "powershell"], case_sensitive=False),
              help="Target programming language (default: will ask)")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--model", default="codellama", help="Ollama model to use (default: codellama)")
@click.pass_context
def generate(ctx, description, language, output, model):
    """Generate code from a natural language description.

    This command provides an interactive way to generate code using AI.
    Simply describe what you want the code to do, and the AI will create it for you.

    Examples:
        # Fully interactive mode
        masterchief code generate

        # With description provided
        masterchief code generate "backup MySQL database to S3"

        # With all options
        masterchief code generate "deploy to k8s" -l python -o deploy.py
    """
    try:
        from addons.scripts.ai_generator import AIScriptGenerator
    except ImportError:
        click.echo("✗ AI Script Generator not available", err=True)
        click.echo("  Install dependencies: pip install -r requirements.txt")
        sys.exit(1)

    # Show welcome message
    click.echo("\n" + "=" * 70)
    click.echo("🤖 AI-Powered Code Generator")
    click.echo("=" * 70)
    click.echo("Generate code from natural language descriptions using AI")
    click.echo()

    # Initialize the AI generator
    generator = AIScriptGenerator(model=model)

    # Check if Ollama is available
    click.echo("🔍 Checking Ollama availability...")
    if not generator.check_availability():
        click.echo("✗ Ollama is not available or model is not loaded\n", err=True)
        click.echo("To use this feature:")
        click.echo("  1. Install Ollama from https://ollama.ai")
        click.echo(f"  2. Pull the model: ollama pull {model}")
        click.echo("  3. Ensure Ollama is running: ollama serve")
        click.echo()
        sys.exit(1)

    click.echo(f"✓ Ollama is available with model: {model}\n")

    # Get description interactively if not provided
    if not description:
        click.echo("📝 What would you like to create?")
        click.echo("Be as specific as possible. Include details about:")
        click.echo("  • What the code should do")
        click.echo("  • Any specific requirements or constraints")
        click.echo("  • Expected inputs and outputs")
        click.echo()

        description = click.prompt("Description", type=str)

        if not description or description.strip() == "":
            click.echo("✗ Description cannot be empty", err=True)
            sys.exit(1)

    # Get language if not provided
    if not language:
        click.echo("\n🔤 Select programming language:")
        language = click.prompt(
            "Language",
            type=click.Choice(["bash", "python", "powershell"], case_sensitive=False),
            default="bash"
        )

    # Show what we're generating
    click.echo("\n" + "-" * 70)
    click.echo("📋 Generation Settings:")
    click.echo(f"  Language:    {language}")
    click.echo(f"  Description: {description}")
    click.echo(f"  Model:       {model}")
    click.echo("-" * 70)

    # Confirm generation
    if not click.confirm("\nGenerate code now?", default=True):
        click.echo("Cancelled.")
        return

    # Generate the code
    click.echo("\n⏳ Generating code... (this may take 10-30 seconds)\n")

    try:
        generated = generator.generate(
            description=description,
            language=language,
            include_comments=True,
            include_error_handling=True
        )

        click.echo("✅ Code generated successfully!\n")
        click.echo("=" * 70)
        click.echo(generated.content)
        click.echo("=" * 70)

        # Handle output
        save_path = None
        if output:
            save_path = Path(output)
        else:
            # Ask if user wants to save it
            if click.confirm("\n💾 Save this code to a file?", default=True):
                default_name = generated.name
                save_path = Path(click.prompt("Enter file path", default=default_name, type=str))
            else:
                click.echo("\n✓ Done! Copy the code above to use it.")
                return

        # Save the file (save_path is guaranteed to be set here)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, 'w') as f:
            f.write(generated.content)

        # Make executable if it's a script
        if language in ["bash", "shell", "sh"]:
            os.chmod(save_path, 0o755)

        click.echo(f"\n✅ Code saved to: {save_path}")
        click.echo(f"   Language: {generated.language}")
        click.echo("   Ready to use!")

        # Show next steps
        click.echo("\n📚 Next steps:")
        if language == "bash":
            click.echo(f"  • Run it: ./{save_path}")
            click.echo(f"  • Validate: masterchief script validate {save_path}")
        elif language == "python":
            click.echo(f"  • Run it: python {save_path}")
        elif language == "powershell":
            click.echo(f"  • Run it: powershell {save_path}")

    except Exception as e:
        click.echo(f"\n✗ Error generating code: {e}", err=True)
        if ctx.obj and ctx.obj.get("verbose"):
            import traceback
            click.echo(traceback.format_exc())
        sys.exit(1)


@code.command("explain")
@click.argument("script_path", type=click.Path(exists=True))
@click.option("--model", default="codellama", help="Ollama model to use")
@click.pass_context
def explain(ctx, script_path, model):
    """Explain what a script does using AI.

    Examples:
        masterchief code explain deploy.sh
        masterchief code explain backup.py
    """
    try:
        from addons.scripts.ai_generator import AIScriptGenerator
    except ImportError:
        click.echo("✗ AI Script Generator not available", err=True)
        sys.exit(1)

    generator = AIScriptGenerator(model=model)

    # Check Ollama availability
    if not generator.check_availability():
        click.echo("✗ Ollama is not available", err=True)
        click.echo("  Run: ollama serve")
        sys.exit(1)

    # Read the script
    script_path = Path(script_path)
    with open(script_path, 'r') as f:
        script_content = f.read()

    click.echo(f"🔍 Analyzing: {script_path}")
    click.echo("⏳ Generating explanation...\n")

    try:
        explanation = generator.explain(script_content)

        click.echo("=" * 70)
        click.echo(explanation)
        click.echo("=" * 70)

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@code.command("improve")
@click.argument("script_path", type=click.Path(exists=True))
@click.option("--model", default="codellama", help="Ollama model to use")
@click.pass_context
def improve(ctx, script_path, model):
    """Get improvement suggestions for a script using AI.

    Examples:
        masterchief code improve deploy.sh
        masterchief code improve backup.py
    """
    try:
        from addons.scripts.ai_generator import AIScriptGenerator
    except ImportError:
        click.echo("✗ AI Script Generator not available", err=True)
        sys.exit(1)

    generator = AIScriptGenerator(model=model)

    # Check Ollama availability
    if not generator.check_availability():
        click.echo("✗ Ollama is not available", err=True)
        sys.exit(1)

    # Read the script
    script_path = Path(script_path)
    with open(script_path, 'r') as f:
        script_content = f.read()

    click.echo(f"🔍 Analyzing: {script_path}")
    click.echo("⏳ Generating improvement suggestions...\n")

    try:
        suggestions = generator.improve(script_content)

        click.echo("=" * 70)
        click.echo("💡 Improvement Suggestions:")
        click.echo("=" * 70)
        click.echo(suggestions)
        click.echo("=" * 70)

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)
