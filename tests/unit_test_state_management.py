"""Tests for state management."""
import pytest
from unittest.mock import Mock, MagicMock
from platform.state import StateStore, StateModel, DeploymentState, PluginState
from platform.state.models import StateStatus


@pytest.mark.asyncio
async def test_state_store_set_get():
    """Test basic set and get operations."""
    redis_mock = Mock()
    redis_mock.set = MagicMock()
    redis_mock.get = MagicMock(return_value='{"test": "value"}')
    
    store = StateStore(redis_client=redis_mock)
    
    # Test set
    await store.set("test_key", {"test": "value"})
    redis_mock.set.assert_called_once()
    
    # Test get
    value = await store.get("test_key")
    assert value == {"test": "value"}


@pytest.mark.asyncio
async def test_state_store_ttl():
    """Test TTL support."""
    redis_mock = Mock()
    redis_mock.setex = MagicMock()
    
    store = StateStore(redis_client=redis_mock)
    
    await store.set("temp_key", {"data": "temporary"}, ttl=300)
    
    redis_mock.setex.assert_called_once()
    args = redis_mock.setex.call_args[0]
    assert args[1] == 300  # TTL


@pytest.mark.asyncio
async def test_state_store_delete():
    """Test delete operation."""
    redis_mock = Mock()
    redis_mock.delete = MagicMock()
    
    store = StateStore(redis_client=redis_mock)
    
    await store.delete("test_key")
    redis_mock.delete.assert_called_once()


@pytest.mark.asyncio
async def test_state_store_increment():
    """Test atomic increment."""
    redis_mock = Mock()
    redis_mock.incrby = MagicMock(return_value=5)
    
    store = StateStore(redis_client=redis_mock)
    
    result = await store.increment("counter", 1)
    assert result == 5
    redis_mock.incrby.assert_called_once()


def test_state_model_creation():
    """Test state model creation."""
    model = StateModel(id="test-1", status=StateStatus.ACTIVE)
    
    assert model.id == "test-1"
    assert model.status == StateStatus.ACTIVE
    assert model.created_at is not None
    assert model.updated_at is not None


def test_deployment_state_model():
    """Test deployment state model."""
    deployment = DeploymentState(
        id="deploy-123",
        environment="production",
        target="server-01",
        progress=50
    )
    
    assert deployment.id == "deploy-123"
    assert deployment.environment == "production"
    assert deployment.progress == 50
    
    data = deployment.to_dict()
    assert data["id"] == "deploy-123"
    assert data["progress"] == 50


def test_plugin_state_model():
    """Test plugin state model."""
    plugin = PluginState(
        id="plugin-456",
        name="test-plugin",
        version="1.0.0",
        enabled=True
    )
    
    assert plugin.id == "plugin-456"
    assert plugin.name == "test-plugin"
    assert plugin.enabled is True
    
    data = plugin.to_dict()
    assert data["name"] == "test-plugin"
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_state_store_snapshot():
    """Test snapshot functionality."""
    redis_mock = Mock()
    redis_mock.get = MagicMock(side_effect=[
        '{"key1": "value1"}',
        '{"key2": "value2"}'
    ])
    
    store = StateStore(redis_client=redis_mock)
    
    snapshot = await store.snapshot(["key1", "key2"])
    
    assert "key1" in snapshot
    assert "key2" in snapshot
    assert snapshot["key1"] == {"key1": "value1"}
