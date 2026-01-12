"""
Echo Voice System - Integration Examples

Shows how to integrate Echo's voice into existing DevOps workflows.
"""

# Example 1: Basic integration with Echo speaking
from echo.devops_suite.voice import TaskState, EchoVoice

def deploy_application():
    """Simple deployment with Echo speaking."""
    EchoVoice.print_speak(TaskState.STARTING, "Application Deployment")
    
    # Your deployment logic here
    # ...
    
    EchoVoice.print_speak(TaskState.SUCCESS, "Application Deployment")


# Example 2: Using the decorator (simplest approach)
from echo.devops_suite.voice import echo_speaks

@echo_speaks("Docker Build")
def build_docker_image():
    """Build Docker image - Echo speaks automatically."""
    # Your build logic here
    # ...
    return {"image": "myapp:latest"}


@echo_speaks("Kubernetes Deployment")
def deploy_to_kubernetes():
    """Deploy to K8s - Echo speaks automatically."""
    # Your deployment logic here
    # ...
    return {"status": "deployed"}


# Example 3: Progress reporting during long-running tasks
from echo.devops_suite.voice import TaskState, EchoVoice

def long_running_build():
    """Show progress during execution."""
    EchoVoice.print_speak(TaskState.STARTING, "Multi-Stage Build")
    
    # Stage 1
    EchoVoice.print_speak(TaskState.RUNNING, "Multi-Stage Build", progress=25)
    # ... build stage 1
    
    # Stage 2
    EchoVoice.print_speak(TaskState.RUNNING, "Multi-Stage Build", progress=50)
    # ... build stage 2
    
    # Stage 3
    EchoVoice.print_speak(TaskState.RUNNING, "Multi-Stage Build", progress=75)
    # ... build stage 3
    
    EchoVoice.print_speak(TaskState.SUCCESS, "Multi-Stage Build")


# Example 4: Error handling with comfort
from echo.devops_suite.voice import TaskState, EchoVoice

def deploy_with_error_handling():
    """Deploy with proper error handling."""
    EchoVoice.print_speak(TaskState.STARTING, "Production Deployment")
    
    try:
        # Your deployment logic
        # ...
        EchoVoice.print_speak(TaskState.SUCCESS, "Production Deployment")
    except Exception as e:
        # Echo comforts on failure
        EchoVoice.print_speak(
            TaskState.FAILED,
            "Production Deployment",
            error=str(e)
        )
        raise


# Example 5: Wrapping an existing DevOps suite
from echo.devops_suite import SpeakingDevOpsSuite

class MyDevOpsSuite:
    """Example DevOps suite."""
    
    def create_script(self, description, **kwargs):
        # Create script logic
        return {"script": f"#!/bin/bash\n# {description}"}
    
    def execute(self, script_content, **kwargs):
        # Execute script logic
        return {"status": "success"}
    
    def load_template(self, template_name, **kwargs):
        # Load template logic
        return {"template": template_name}


def use_speaking_suite():
    """Use the speaking wrapper."""
    # Create your suite
    suite = MyDevOpsSuite()
    
    # Wrap it with Echo's voice
    speaking_suite = SpeakingDevOpsSuite(suite)
    
    # Now every operation speaks!
    script = speaking_suite.create_script("Build application")
    speaking_suite.execute(script["script"], "Build Task")
    speaking_suite.load_template("docker-compose.yml")


# Example 6: Using warnings and waiting states
from echo.devops_suite.voice import TaskState, EchoVoice

def health_check_with_warnings():
    """Health check that may have warnings."""
    EchoVoice.print_speak(TaskState.STARTING, "Health Check")
    
    # Check health
    health_status = check_system_health()
    
    if health_status == "warning":
        EchoVoice.print_speak(TaskState.WARNING, "Health Check")
    
    EchoVoice.print_speak(TaskState.SUCCESS, "Health Check")


def wait_for_approval():
    """Wait for user approval."""
    EchoVoice.print_speak(TaskState.WAITING, "Deployment Approval")
    
    # Wait for approval
    # ...
    
    EchoVoice.print_speak(TaskState.SUCCESS, "Deployment Approval")


# Example 7: CI/CD Pipeline integration
from echo.devops_suite.voice import echo_speaks

class CIPipeline:
    """Example CI/CD pipeline with Echo."""
    
    @echo_speaks("Code Checkout")
    def checkout(self):
        # Git checkout logic
        pass
    
    @echo_speaks("Run Tests")
    def test(self):
        # Test execution logic
        pass
    
    @echo_speaks("Build Artifacts")
    def build(self):
        # Build logic
        pass
    
    @echo_speaks("Deploy to Production")
    def deploy(self):
        # Deployment logic
        pass
    
    def run_pipeline(self):
        """Run the full pipeline - Echo speaks for each stage."""
        self.checkout()
        self.test()
        self.build()
        self.deploy()


# Example 8: Infrastructure as Code with Echo
from echo.devops_suite.voice import echo_speaks

@echo_speaks("Terraform Plan")
def terraform_plan():
    """Run terraform plan."""
    # terraform plan logic
    return {"changes": 5}


@echo_speaks("Terraform Apply")
def terraform_apply():
    """Run terraform apply."""
    # terraform apply logic
    return {"applied": True}


@echo_speaks("Ansible Playbook")
def run_ansible_playbook():
    """Run ansible playbook."""
    # ansible playbook logic
    return {"hosts_updated": 10}


# Example 9: Monitoring and Alerting
from echo.devops_suite.voice import TaskState, EchoVoice

def monitor_system():
    """Monitor system with Echo notifications."""
    EchoVoice.print_speak(TaskState.STARTING, "System Monitoring")
    
    metrics = collect_metrics()
    
    if metrics["cpu"] > 80:
        EchoVoice.print_speak(TaskState.WARNING, "High CPU Usage")
    
    if metrics["memory"] > 90:
        EchoVoice.print_speak(TaskState.WARNING, "High Memory Usage")
    
    EchoVoice.print_speak(TaskState.SUCCESS, "System Monitoring")


# Example 10: Backup and Recovery
from echo.devops_suite.voice import echo_speaks

@echo_speaks("Database Backup")
def backup_database():
    """Backup database with Echo."""
    # Backup logic
    return {"backup_file": "db_backup_20260112.sql"}


@echo_speaks("Database Restore")
def restore_database(backup_file):
    """Restore database with Echo."""
    # Restore logic
    return {"restored": True}


def check_system_health():
    """Mock health check."""
    return "ok"


def collect_metrics():
    """Mock metrics collection."""
    return {"cpu": 75, "memory": 60}


if __name__ == "__main__":
    print("\nEcho Voice System - Integration Examples")
    print("=" * 64)
    print("\nThese examples show how to integrate Echo into your workflows.")
    print("Echo will speak for every task, providing comfort and presence.")
    print("\nFor Marsh. 🌙💜\n")
