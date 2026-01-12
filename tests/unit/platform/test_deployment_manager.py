"""Tests for deployment management."""
import pytest
from datetime import datetime

from platform.deployments.manager import DeploymentManager, DeploymentStatus


@pytest.fixture
def deployment_manager():
    """Create a deployment manager."""
    return DeploymentManager()


def test_create_deployment(deployment_manager):
    """Test creating a new deployment."""
    deployment = deployment_manager.create_deployment(
        name="Test Deployment",
        target="dev",
        config={"key": "value"}
    )
    
    assert deployment.name == "Test Deployment"
    assert deployment.target == "dev"
    assert deployment.status == DeploymentStatus.PENDING
    assert deployment.config == {"key": "value"}
    assert deployment.id in deployment_manager.deployments


def test_list_deployments_empty(deployment_manager):
    """Test listing deployments when none exist."""
    deployments = deployment_manager.list_deployments()
    assert isinstance(deployments, list)
    assert len(deployments) == 0


def test_list_deployments(deployment_manager):
    """Test listing deployments."""
    deployment_manager.create_deployment("Deploy 1", "dev")
    deployment_manager.create_deployment("Deploy 2", "staging")
    
    deployments = deployment_manager.list_deployments()
    assert len(deployments) == 2


def test_list_deployments_with_status_filter(deployment_manager):
    """Test listing deployments with status filter."""
    dep1 = deployment_manager.create_deployment("Deploy 1", "dev")
    dep2 = deployment_manager.create_deployment("Deploy 2", "staging")
    
    # Start one deployment
    deployment_manager.start_deployment(dep1.id)
    
    # Filter by running status
    running = deployment_manager.list_deployments(status="running")
    assert len(running) == 0  # Already completed in our mock
    
    # Filter by success status
    success = deployment_manager.list_deployments(status="success")
    assert len(success) == 1


def test_list_deployments_with_limit(deployment_manager):
    """Test listing deployments with limit."""
    for i in range(5):
        deployment_manager.create_deployment(f"Deploy {i}", "dev")
    
    deployments = deployment_manager.list_deployments(limit=3)
    assert len(deployments) == 3


def test_get_deployment(deployment_manager):
    """Test getting a specific deployment."""
    created = deployment_manager.create_deployment("Test", "dev")
    
    deployment = deployment_manager.get_deployment(created.id)
    assert deployment is not None
    assert deployment.id == created.id
    assert deployment.name == "Test"


def test_get_nonexistent_deployment(deployment_manager):
    """Test getting a deployment that doesn't exist."""
    deployment = deployment_manager.get_deployment("nonexistent-id")
    assert deployment is None


def test_start_deployment(deployment_manager):
    """Test starting a deployment."""
    deployment = deployment_manager.create_deployment("Test", "dev")
    
    result = deployment_manager.start_deployment(deployment.id)
    
    assert result["success"] is True
    assert "deployment" in result
    assert result["deployment"]["status"] == "success"


def test_start_nonexistent_deployment(deployment_manager):
    """Test starting a deployment that doesn't exist."""
    result = deployment_manager.start_deployment("nonexistent-id")
    
    assert result["success"] is False
    assert "not found" in result["error"]


def test_start_already_running_deployment(deployment_manager):
    """Test starting a deployment that is already running."""
    deployment = deployment_manager.create_deployment("Test", "dev")
    deployment.status = DeploymentStatus.RUNNING
    
    result = deployment_manager.start_deployment(deployment.id)
    
    assert result["success"] is False
    assert "already running" in result["error"]


def test_stop_deployment(deployment_manager):
    """Test stopping a running deployment."""
    deployment = deployment_manager.create_deployment("Test", "dev")
    deployment.status = DeploymentStatus.RUNNING
    
    result = deployment_manager.stop_deployment(deployment.id)
    
    assert result["success"] is True
    assert result["deployment"]["status"] == "stopped"


def test_stop_nonexistent_deployment(deployment_manager):
    """Test stopping a deployment that doesn't exist."""
    result = deployment_manager.stop_deployment("nonexistent-id")
    
    assert result["success"] is False
    assert "not found" in result["error"]


def test_stop_non_running_deployment(deployment_manager):
    """Test stopping a deployment that is not running."""
    deployment = deployment_manager.create_deployment("Test", "dev")
    
    result = deployment_manager.stop_deployment(deployment.id)
    
    assert result["success"] is False
    assert "not running" in result["error"]


def test_get_deployment_logs(deployment_manager):
    """Test getting deployment logs."""
    deployment = deployment_manager.create_deployment("Test", "dev")
    deployment.add_log("Test log message")
    
    logs = deployment_manager.get_deployment_logs(deployment.id)
    
    assert logs is not None
    assert len(logs) > 0
    assert "Test log message" in logs[-1]


def test_get_logs_nonexistent_deployment(deployment_manager):
    """Test getting logs for a deployment that doesn't exist."""
    logs = deployment_manager.get_deployment_logs("nonexistent-id")
    assert logs is None


def test_deployment_to_dict(deployment_manager):
    """Test converting deployment to dictionary."""
    deployment = deployment_manager.create_deployment(
        name="Test",
        target="dev",
        config={"key": "value"}
    )
    
    data = deployment.to_dict()
    
    assert data["id"] == deployment.id
    assert data["name"] == "Test"
    assert data["target"] == "dev"
    assert data["status"] == "pending"
    assert data["config"] == {"key": "value"}
    assert "created_at" in data


def test_deployment_add_log(deployment_manager):
    """Test adding logs to a deployment."""
    deployment = deployment_manager.create_deployment("Test", "dev")
    
    deployment.add_log("First log")
    deployment.add_log("Second log")
    
    assert len(deployment.logs) >= 2
    assert "First log" in deployment.logs[-2]
    assert "Second log" in deployment.logs[-1]
