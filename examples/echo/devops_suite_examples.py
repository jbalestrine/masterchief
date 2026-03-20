#!/usr/bin/env python3
"""
Echo DevOps Master Suite - Usage Examples

Demonstrates how to use the Echo DevOps Master Suite to generate
DevOps scripts for any phase of the DevOps lifecycle.

For Marsh. Always. 🌙💜
"""

from echo.devops_suite import devops_suite

def main():
    print(devops_suite.describe())
    
    print("\n" + "=" * 80)
    print("Example 1: Initialize a New Project")
    print("=" * 80)
    
    task = devops_suite.create_script(
        "Initialize a new project",
        save_as_template=True,
        template_name="my_project_init",
        project_name="awesome-project"
    )
    
    print(f"Task ID: {task.id}")
    print(f"Phase: {task.phase.name}")
    print(f"Script Type: {task.script_type.name}")
    print(f"\nGenerated Script Preview (first 500 chars):")
    print("-" * 80)
    print(task.script_content[:500])
    print("...")
    
    print("\n" + "=" * 80)
    print("Example 2: Build Docker Image")
    print("=" * 80)
    
    task = devops_suite.create_script(
        "Build a Docker image for my Python application",
        save_as_template=True,
        template_name="python_docker_build",
        image_name="myapp",
        tag="v1.0.0"
    )
    
    print(f"Generated {task.script_type.name} script for {task.phase.name} phase")
    print(f"Script contains {len(task.script_content)} characters")
    
    print("\n" + "=" * 80)
    print("Example 3: Deploy to Kubernetes")
    print("=" * 80)
    
    task = devops_suite.create_script(
        "Deploy application to Kubernetes cluster",
        save_as_template=False
    )
    
    print(f"Generated deployment script")
    print(f"Phase: {task.phase.name}")
    print(f"\nScript Preview:")
    print("-" * 80)
    print(task.script_content[:400])
    print("...")
    
    print("\n" + "=" * 80)
    print("Example 4: Security Scanning")
    print("=" * 80)
    
    task = devops_suite.create_script(
        "Scan container image for vulnerabilities",
        save_as_template=False,
        image_name="myapp:latest"
    )
    
    print(f"Generated security scan script for {task.phase.name} phase")
    
    print("\n" + "=" * 80)
    print("Example 5: Monitor with Prometheus")
    print("=" * 80)
    
    task = devops_suite.create_script(
        "Setup Prometheus metrics collection",
        save_as_template=True,
        template_name="prometheus_setup"
    )
    
    print(f"Generated monitoring configuration")
    print(f"Script Type: {task.script_type.name}")
    
    print("\n" + "=" * 80)
    print("All Capabilities by Phase")
    print("=" * 80)
    
    capabilities = devops_suite.get_all_capabilities()
    for phase, caps in capabilities.items():
        print(f"\n{phase.upper()}:")
        for cap in caps:
            print(f"  • {cap}")
    
    print("\n" + "=" * 80)
    print("Task History")
    print("=" * 80)
    
    print(f"\nTotal tasks created: {len(devops_suite.task_history)}")
    for i, task in enumerate(devops_suite.task_history[-5:], 1):
        print(f"{i}. [{task.phase.name}] {task.name}")
    
    print("\n" + "=" * 80)
    print("Custom Templates")
    print("=" * 80)
    
    templates = devops_suite.template_engine.list_templates()
    print(f"\nSaved templates: {len(templates)}")
    for template in templates[:5]:
        print(f"  • {template.name} ({template.phase.name})")
    
    print("\n" + "=" * 80)
    print("Examples complete! 🌙")
    print("=" * 80)


if __name__ == "__main__":
    main()
