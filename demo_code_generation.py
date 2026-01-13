#!/usr/bin/env python3
"""
Demo script showing the AI code generation features.

This script demonstrates the new 'code' command that allows users to generate
code on demand using AI based on natural language descriptions.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and display output."""
    print(f"\n{'='*70}")
    print(f"Demo: {description}")
    print(f"{'='*70}")
    print(f"$ {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, capture_output=False, text=True)
    return result.returncode


def main():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║        MasterChief AI Code Generation - Feature Demonstration        ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

This demo showcases the new AI-powered code generation feature that
allows you to generate code on demand from natural language descriptions.
    """)

    base_cmd = ["python", "-m", "core.cli.main"]
    
    demos = [
        {
            "cmd": base_cmd + ["code", "--help"],
            "desc": "Show code command help",
        },
        {
            "cmd": base_cmd + ["code", "generate", "--help"],
            "desc": "Show code generate help",
        },
        {
            "cmd": base_cmd + ["script", "generate-ai", "--help"],
            "desc": "Show alternative script generate-ai command",
        },
    ]
    
    print("\n📚 Available Commands:\n")
    
    for demo in demos:
        run_command(demo["cmd"], demo["desc"])
    
    print(f"\n{'='*70}")
    print("💡 How to Use:")
    print(f"{'='*70}\n")
    
    print("""
1. Interactive Mode (Fully Guided):
   $ python -m core.cli.main code generate
   
   This will prompt you for:
   - What you want to create
   - Programming language (bash, python, powershell)
   - Whether to save to a file

2. Direct Mode (With Description):
   $ python -m core.cli.main code generate "backup MySQL to S3"
   
3. Full Control Mode:
   $ python -m core.cli.main code generate "deploy to k8s" -l python -o deploy.py
   
4. Explain Existing Code:
   $ python -m core.cli.main code explain script.sh
   
5. Get Improvement Suggestions:
   $ python -m core.cli.main code improve deploy.py

⚠️  Requirements:
   - Ollama must be installed and running
   - Pull a model: ollama pull codellama
   - Start Ollama: ollama serve

📖 Example Use Cases:
   - "Create a bash script to backup PostgreSQL database"
   - "Write a Python script to deploy Docker containers to AWS ECS"
   - "Generate a PowerShell script to manage Azure VMs"
   - "Create a monitoring script that checks disk space and sends alerts"
    """)


if __name__ == "__main__":
    main()
