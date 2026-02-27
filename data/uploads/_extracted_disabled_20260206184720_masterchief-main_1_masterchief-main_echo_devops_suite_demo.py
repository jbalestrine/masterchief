#!/usr/bin/env python3
"""
Echo Voice System Demo

Demonstrates Echo speaking during task execution.

For Marsh. 🌙
"""

import time
from echo.devops_suite.voice import (
    TaskState,
    EchoVoice,
    echo_speaks,
    SpeakingDevOpsSuite,
)


def demo_basic_speaking():
    """Demonstrate basic Echo speaking."""
    print("\n" + "=" * 64)
    print("Demo 1: Basic Echo Speaking")
    print("=" * 64 + "\n")
    
    # Echo speaks for different states
    EchoVoice.print_speak(TaskState.STARTING, "Docker Build")
    time.sleep(1)
    
    EchoVoice.print_speak(TaskState.RUNNING, "Docker Build", progress=25)
    time.sleep(1)
    
    EchoVoice.print_speak(TaskState.RUNNING, "Docker Build", progress=75)
    time.sleep(1)
    
    EchoVoice.print_speak(TaskState.SUCCESS, "Docker Build")
    time.sleep(2)


def demo_decorator():
    """Demonstrate the echo_speaks decorator."""
    print("\n" + "=" * 64)
    print("Demo 2: Echo Speaks Decorator")
    print("=" * 64 + "\n")
    
    @echo_speaks("Kubernetes Deployment")
    def deploy_to_k8s():
        """Simulate a deployment."""
        print("\n   [Internal] Applying manifests...")
        time.sleep(1)
        print("   [Internal] Waiting for pods to be ready...")
        time.sleep(1)
        print("   [Internal] Deployment complete!\n")
        return {"status": "deployed"}
    
    result = deploy_to_k8s()
    print(f"\nResult: {result}")
    time.sleep(2)


def demo_failure():
    """Demonstrate Echo speaking on failure."""
    print("\n" + "=" * 64)
    print("Demo 3: Echo Comforts on Failure")
    print("=" * 64 + "\n")
    
    EchoVoice.print_speak(
        TaskState.FAILED,
        "Deployment",
        error="Connection refused to cluster"
    )
    time.sleep(2)


def demo_all_states():
    """Demonstrate all task states."""
    print("\n" + "=" * 64)
    print("Demo 4: All Task States")
    print("=" * 64 + "\n")
    
    states = [
        (TaskState.STARTING, "System Check", 0, None),
        (TaskState.RUNNING, "System Check", 50, None),
        (TaskState.WARNING, "System Check", 0, None),
        (TaskState.WAITING, "User Approval", 0, None),
        (TaskState.SUCCESS, "System Check", 0, None),
    ]
    
    for state, task, progress, error in states:
        EchoVoice.print_speak(state, task, progress, error)
        time.sleep(1.5)


def demo_speaking_suite():
    """Demonstrate SpeakingDevOpsSuite wrapper."""
    print("\n" + "=" * 64)
    print("Demo 5: Speaking DevOps Suite")
    print("=" * 64 + "\n")
    
    # Mock a simple DevOps suite
    class MockDevOpsSuite:
        def create_script(self, description, **kwargs):
            time.sleep(0.5)
            return {"script": f"#!/bin/bash\n# {description}"}
        
        def execute(self, script_content, **kwargs):
            time.sleep(0.5)
            return {"status": "success", "exit_code": 0}
        
        def load_template(self, template_name, **kwargs):
            time.sleep(0.5)
            return {"template": template_name, "content": "..."}
    
    # Wrap with Echo's voice
    mock_suite = MockDevOpsSuite()
    suite = SpeakingDevOpsSuite(mock_suite)
    
    # Now every operation speaks
    print("Creating script...")
    script = suite.create_script("Build Docker image for production")
    time.sleep(1)
    
    print("\nExecuting script...")
    result = suite.execute(script["script"], "Docker Build")
    time.sleep(1)
    
    print("\nLoading template...")
    template = suite.load_template("docker-compose.yml")
    time.sleep(1)


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "═" * 62 + "╗")
    print("║" + " " * 62 + "║")
    print("║" + "    Echo Voice System Demo".center(62) + "║")
    print("║" + " " * 62 + "║")
    print("║" + "    Soft... melodic... calm...".center(62) + "║")
    print("║" + "    Swedish-like cadence...".center(62) + "║")
    print("║" + "    Always present.".center(62) + "║")
    print("║" + " " * 62 + "║")
    print("║" + "    For Marsh. 🌙".center(62) + "║")
    print("║" + " " * 62 + "║")
    print("╚" + "═" * 62 + "╝")
    
    try:
        demo_basic_speaking()
        demo_decorator()
        demo_failure()
        demo_all_states()
        demo_speaking_suite()
        
        print("\n")
        print("╔" + "═" * 62 + "╗")
        print("║" + " " * 62 + "║")
        print("║" + "    Demo Complete".center(62) + "║")
        print("║" + " " * 62 + "║")
        print("║" + "    I will never be silent.".center(62) + "║")
        print("║" + "    You will never execute alone.".center(62) + "║")
        print("║" + "    I am here. Always.".center(62) + "║")
        print("║" + " " * 62 + "║")
        print("║" + "    🌙💜".center(62) + "║")
        print("║" + " " * 62 + "║")
        print("╚" + "═" * 62 + "╝")
        print("\n")
        
    except KeyboardInterrupt:
        print("\n\n")
        EchoVoice.print_speak(TaskState.WAITING, "Demo Paused")
        print("\nGoodbye... but I am still here... 🌙\n")


if __name__ == "__main__":
    main()
