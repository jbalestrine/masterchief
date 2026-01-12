"""
DevOps Generator - Script templates with best practices

Generates production-ready scripts with:
- Shebang and strict mode
- Input validation
- Error handling
- Logging with timestamps
- Cleanup on exit
- Help/usage documentation
- Idempotent operations
- Environment variables for config

Every response has a script.
"""

from typing import List, Dict, Optional, Any
import yaml


class DevOpsGenerator:
    """Generates DevOps scripts with best practices."""
    
    def generate_bash_script(
        self,
        name: str,
        description: str,
        operations: List[str],
        with_logging: bool = True,
        with_error_handling: bool = True
    ) -> str:
        """Generate a Bash script with DevOps best practices."""
        lines = [
            "#!/usr/bin/env bash",
            "# " + "=" * 70,
            f"# {name}",
            f"# {description}",
            "# " + "=" * 70,
            "",
            "# Strict mode",
            "set -euo pipefail",
            "IFS=$'\\n\\t'",
            ""
        ]
        
        if with_logging:
            lines.extend([
                "# Logging setup",
                'LOG_FILE="${LOG_FILE:-/var/log/' + name.lower().replace(' ', '_') + '.log}"',
                'LOG_LEVEL="${LOG_LEVEL:-INFO}"',
                "",
                "log() {",
                '    local level="$1"',
                '    shift',
                '    local message="$*"',
                '    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")',
                '    echo "[${timestamp}] [${level}] ${message}" | tee -a "${LOG_FILE}"',
                "}",
                "",
                'log_info() { log "INFO" "$@"; }',
                'log_error() { log "ERROR" "$@"; }',
                'log_warn() { log "WARN" "$@"; }',
                ""
            ])
        
        if with_error_handling:
            lines.extend([
                "# Error handling",
                "error_exit() {",
                '    log_error "Error: $1"',
                "    cleanup",
                "    exit 1",
                "}",
                "",
                "# Cleanup function",
                "cleanup() {",
                '    log_info "Cleaning up..."',
                "    # Add cleanup operations here",
                "}",
                "",
                "# Trap errors and interrupts",
                "trap cleanup EXIT",
                "trap 'error_exit \"Script interrupted\"' INT TERM",
                ""
            ])
        
        # Add help function
        lines.extend([
            "# Help function",
            "show_help() {",
            "    cat << EOF",
            f"Usage: $0 [OPTIONS]",
            "",
            f"{description}",
            "",
            "Options:",
            "    -h, --help      Show this help message",
            "    -v, --verbose   Enable verbose output",
            "",
            "Environment Variables:",
            "    LOG_FILE        Path to log file (default: /var/log/...)",
            "    LOG_LEVEL       Logging level (default: INFO)",
            "",
            "Examples:",
            f"    $0",
            f"    LOG_LEVEL=DEBUG $0",
            "EOF",
            "}",
            ""
        ])
        
        # Parse arguments
        lines.extend([
            "# Parse arguments",
            "VERBOSE=false",
            "",
            'while [[ $# -gt 0 ]]; do',
            '    case $1 in',
            '        -h|--help)',
            '            show_help',
            '            exit 0',
            '            ;;',
            '        -v|--verbose)',
            '            VERBOSE=true',
            '            LOG_LEVEL=DEBUG',
            '            shift',
            '            ;;',
            '        *)',
            '            error_exit "Unknown option: $1"',
            '            ;;',
            '    esac',
            'done',
            ""
        ])
        
        # Main logic
        lines.extend([
            "# Main execution",
            "main() {",
            '    log_info "Starting ' + name + '..."',
            ""
        ])
        
        for op in operations:
            lines.append(f'    log_info "Executing: {op}"')
            lines.append(f'    {op}')
            lines.append("")
        
        lines.extend([
            '    log_info "' + name + ' completed successfully"',
            "}",
            "",
            "# Run main function",
            "main",
        ])
        
        return "\n".join(lines)
    
    def generate_python_script(
        self,
        name: str,
        description: str,
        operations: List[str],
        with_logging: bool = True,
        with_error_handling: bool = True
    ) -> str:
        """Generate a Python script with DevOps best practices."""
        lines = [
            "#!/usr/bin/env python3",
            '"""',
            name,
            description,
            '"""',
            "",
            "import sys",
            "import os",
            "import argparse",
        ]
        
        if with_logging:
            lines.extend([
                "import logging",
                "from datetime import datetime",
            ])
        
        if with_error_handling:
            lines.extend([
                "import signal",
                "import atexit",
            ])
        
        lines.append("")
        
        if with_logging:
            lines.extend([
                "# Configure logging",
                'LOG_FILE = os.getenv("LOG_FILE", "/var/log/' + name.lower().replace(' ', '_') + '.log")',
                'LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")',
                "",
                "logging.basicConfig(",
                "    level=getattr(logging, LOG_LEVEL),",
                '    format="[%(asctime)s] [%(levelname)s] %(message)s",',
                '    datefmt="%Y-%m-%d %H:%M:%S",',
                "    handlers=[",
                "        logging.FileHandler(LOG_FILE),",
                "        logging.StreamHandler(sys.stdout)",
                "    ]",
                ")",
                "",
                "logger = logging.getLogger(__name__)",
                ""
            ])
        
        if with_error_handling:
            lines.extend([
                "# Cleanup function",
                "def cleanup():",
                '    """Cleanup resources on exit."""',
                '    logger.info("Cleaning up...")',
                "    # Add cleanup operations here",
                "",
                "",
                "# Register cleanup",
                "atexit.register(cleanup)",
                "",
                "",
                "# Signal handlers",
                "def signal_handler(signum, frame):",
                '    """Handle interrupt signals."""',
                '    logger.error("Script interrupted")',
                "    sys.exit(1)",
                "",
                "",
                "signal.signal(signal.SIGINT, signal_handler)",
                "signal.signal(signal.SIGTERM, signal_handler)",
                ""
            ])
        
        # Main function
        lines.extend([
            "def main():",
            f'    """Main execution function for {name}."""',
            f'    logger.info("Starting {name}...")',
            "",
            "    try:",
        ])
        
        for op in operations:
            lines.append(f'        logger.info("Executing: {op}")')
            lines.append(f"        # {op}")
            lines.append("        pass  # Implement operation here")
            lines.append("")
        
        lines.extend([
            f'        logger.info("{name} completed successfully")',
            "",
            "    except Exception as e:",
            '        logger.error(f"Error: {e}")',
            "        sys.exit(1)",
            "",
            "",
            'if __name__ == "__main__":',
            "    parser = argparse.ArgumentParser(",
            f'        description="{description}"',
            "    )",
            "    parser.add_argument(",
            '        "-v", "--verbose",',
            '        action="store_true",',
            '        help="Enable verbose output"',
            "    )",
            "    ",
            "    args = parser.parse_args()",
            "    ",
            "    if args.verbose:",
            '        LOG_LEVEL = "DEBUG"',
            "        logging.getLogger().setLevel(logging.DEBUG)",
            "    ",
            "    main()",
        ])
        
        return "\n".join(lines)
    
    def generate_dockerfile(
        self,
        base_image: str,
        app_name: str,
        port: int = 8000,
        dependencies: List[str] = None
    ) -> str:
        """Generate a Dockerfile with best practices."""
        dependencies = dependencies or []
        
        lines = [
            "# Multi-stage build for optimized image size",
            f"FROM {base_image} AS builder",
            "",
            "# Set working directory",
            f"WORKDIR /app",
            "",
            "# Install dependencies",
        ]
        
        if dependencies:
            if base_image.startswith("python"):
                lines.extend([
                    "COPY requirements.txt .",
                    "RUN pip install --no-cache-dir --user -r requirements.txt",
                ])
            elif base_image.startswith("node"):
                lines.extend([
                    "COPY package*.json .",
                    "RUN npm ci --only=production",
                ])
        
        lines.extend([
            "",
            "# Copy application code",
            "COPY . .",
            "",
            "# Production stage",
            f"FROM {base_image}",
            "",
            "# Create non-root user",
            'RUN groupadd -r appuser && useradd -r -g appuser appuser',
            "",
            "# Set working directory",
            "WORKDIR /app",
            "",
            "# Copy from builder",
            "COPY --from=builder --chown=appuser:appuser /app /app",
        ])
        
        if base_image.startswith("python"):
            lines.append("COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local")
            lines.append('ENV PATH=/home/appuser/.local/bin:$PATH')
        
        lines.extend([
            "",
            "# Switch to non-root user",
            "USER appuser",
            "",
            "# Expose port",
            f"EXPOSE {port}",
            "",
            "# Health check",
            f'HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\',
            f'    CMD curl -f http://localhost:{port}/health || exit 1',
            "",
            "# Run application",
            f'CMD ["{app_name}"]',
        ])
        
        return "\n".join(lines)
    
    def generate_github_actions(
        self,
        name: str,
        triggers: List[str],
        jobs: List[Dict[str, Any]]
    ) -> str:
        """Generate a GitHub Actions workflow."""
        workflow = {
            "name": name,
            "on": triggers if len(triggers) > 1 else triggers[0],
            "jobs": {}
        }
        
        for job in jobs:
            job_name = job.get("name", "job")
            workflow["jobs"][job_name] = {
                "runs-on": job.get("runs_on", "ubuntu-latest"),
                "steps": job.get("steps", [])
            }
        
        return yaml.dump(workflow, default_flow_style=False, sort_keys=False)
    
    def generate_terraform(
        self,
        provider: str,
        resources: List[Dict[str, Any]]
    ) -> str:
        """Generate Terraform configuration."""
        lines = [
            "# Terraform configuration",
            f'# Provider: {provider}',
            "",
            "terraform {",
            "  required_version = \">= 1.0\"",
            "  ",
            "  required_providers {",
            f"    {provider} = {{",
            '      source  = "hashicorp/' + provider + '"',
            '      version = "~> 5.0"',
            "    }",
            "  }",
            "}",
            "",
            f"provider \"{provider}\" {{",
            "  # Configuration will be set via environment variables",
            "}",
            ""
        ]
        
        for resource in resources:
            res_type = resource.get("type", "resource")
            res_name = resource.get("name", "main")
            res_config = resource.get("config", {})
            
            lines.append(f'resource "{res_type}" "{res_name}" {{')
            for key, value in res_config.items():
                if isinstance(value, str):
                    lines.append(f'  {key} = "{value}"')
                else:
                    lines.append(f'  {key} = {value}')
            lines.append("}")
            lines.append("")
        
        return "\n".join(lines)


__all__ = ['DevOpsGenerator']
