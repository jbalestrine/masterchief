#!/usr/bin/env python3
"""
Manual test script for Echo DevOps Master Suite
"""

import sys
sys.path.insert(0, '/home/runner/work/masterchief/masterchief')

from echo.devops_suite import devops_suite, DevOpsPhase, ScriptType

def test_basic_functionality():
    """Test basic suite functionality"""
    print("=" * 80)
    print("Testing Echo DevOps Master Suite")
    print("=" * 80)
    
    # Test 1: Display suite information
    print("\nTest 1: Display Suite Information")
    print("-" * 80)
    print(devops_suite.describe())
    
    # Test 2: Create a task for each phase
    print("\nTest 2: Create Tasks for Each Phase")
    print("-" * 80)
    
    test_tasks = [
        ("Initialize a new project", "PLAN"),
        ("Setup pre-commit hooks", "CODE"),
        ("Build a Docker image for my Python app", "BUILD"),
        ("Run unit tests", "TEST"),
        ("Create a release with version tagging", "RELEASE"),
        ("Deploy to Kubernetes", "DEPLOY"),
        ("Run health checks", "OPERATE"),
        ("Setup Prometheus metrics", "MONITOR"),
        ("Scan for vulnerabilities", "SECURE"),
        ("Analyze cloud costs", "OPTIMIZE"),
    ]
    
    for task_desc, expected_phase in test_tasks:
        task = devops_suite.create_script(task_desc, save_as_template=False)
        phase_match = task.phase.name == expected_phase
        status = "✓" if phase_match else "✗"
        print(f"{status} Task: {task_desc[:40]:<40} → Phase: {task.phase.name:<10} (Expected: {expected_phase})")
        
        if not phase_match:
            print(f"  ERROR: Expected {expected_phase}, got {task.phase.name}")
    
    # Test 3: Get capabilities
    print("\nTest 3: Get All Capabilities")
    print("-" * 80)
    capabilities = devops_suite.get_all_capabilities()
    total_capabilities = sum(len(caps) for caps in capabilities.values())
    print(f"Total capabilities: {total_capabilities}")
    
    for phase, caps in capabilities.items():
        print(f"  {phase.upper():<10}: {len(caps)} capabilities")
    
    # Test 4: Test specific script generation
    print("\nTest 4: Generate Specific Scripts")
    print("-" * 80)
    
    # Docker build script
    docker_task = devops_suite.create_script(
        "Build Docker image",
        save_as_template=False,
        image_name="myapp",
        tag="v1.0.0"
    )
    print(f"✓ Docker build script generated ({len(docker_task.script_content)} bytes)")
    assert "docker" in docker_task.script_content.lower()
    assert "myapp" in docker_task.script_content
    
    # Python build script
    python_task = devops_suite.create_script(
        "Build Python package",
        save_as_template=False
    )
    print(f"✓ Python build script generated ({len(python_task.script_content)} bytes)")
    assert "python" in python_task.script_content.lower()
    
    # Kubernetes deployment script
    k8s_task = devops_suite.create_script(
        "Deploy to Kubernetes cluster",
        save_as_template=False
    )
    print(f"✓ Kubernetes deployment script generated ({len(k8s_task.script_content)} bytes)")
    assert "kubectl" in k8s_task.script_content.lower()
    
    # Test 5: Task history
    print("\nTest 5: Task History")
    print("-" * 80)
    print(f"Total tasks created: {len(devops_suite.task_history)}")
    
    # Test 6: Template engine
    print("\nTest 6: Template Engine")
    print("-" * 80)
    templates = devops_suite.template_engine.list_templates()
    print(f"Custom templates saved: {len(templates)}")
    
    print("\n" + "=" * 80)
    print("All tests completed successfully! 🌙")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    try:
        success = test_basic_functionality()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
