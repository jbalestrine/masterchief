"""Tests for platform event bus."""
import pytest
import asyncio
from platform.event_bus import EventType, EventPublisher
from core.event_bus import Event, EventBus


@pytest.mark.asyncio
async def test_extended_event_types():
    """Test that extended event types are available."""
    assert hasattr(EventType, 'DEPLOYMENT_STARTED')
    assert hasattr(EventType, 'PLUGIN_INSTALLED')
    assert hasattr(EventType, 'SYSTEM_HEALTH')
    assert hasattr(EventType, 'LOG_ENTRY')
    assert hasattr(EventType, 'IRC_COMMAND')
    
    assert EventType.DEPLOYMENT_STARTED.value == "deployment.started"
    assert EventType.PLUGIN_INSTALLED.value == "plugin.installed"


@pytest.mark.asyncio
async def test_event_publisher_deployment():
    """Test event publisher for deployment events."""
    bus = EventBus()
    publisher = EventPublisher(source="test", event_bus=bus)
    
    received_events = []
    
    def handler(event: Event):
        received_events.append(event)
    
    bus.subscribe("deployment.started", handler)
    bus.subscribe("deployment.progress", handler)
    bus.subscribe("deployment.completed", handler)
    
    # Test deployment started
    await publisher.publish_deployment_started("deploy-123", {"env": "prod"})
    assert len(received_events) == 1
    assert received_events[0].type == "deployment.started"
    assert received_events[0].data["deployment_id"] == "deploy-123"
    
    # Test deployment progress
    await publisher.publish_deployment_progress("deploy-123", 50, "Halfway done")
    assert len(received_events) == 2
    assert received_events[1].data["progress"] == 50
    
    # Test deployment completed
    await publisher.publish_deployment_completed("deploy-123", {"status": "success"})
    assert len(received_events) == 3
    assert received_events[2].type == "deployment.completed"


@pytest.mark.asyncio
async def test_event_publisher_plugin():
    """Test event publisher for plugin events."""
    bus = EventBus()
    publisher = EventPublisher(source="test", event_bus=bus)
    
    received_events = []
    
    def handler(event: Event):
        received_events.append(event)
    
    bus.subscribe("plugin.installed", handler)
    
    await publisher.publish_plugin_event("plugin.installed", "test-plugin", {"version": "1.0.0"})
    
    assert len(received_events) == 1
    assert received_events[0].data["plugin_id"] == "test-plugin"
    assert received_events[0].data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_event_publisher_logs():
    """Test event publisher for log events."""
    bus = EventBus()
    publisher = EventPublisher(source="test", event_bus=bus)
    
    received_events = []
    
    def handler(event: Event):
        received_events.append(event)
    
    bus.subscribe("log.entry", handler)
    
    await publisher.publish_log_entry("INFO", "Test message", {"extra": "data"})
    
    assert len(received_events) == 1
    assert received_events[0].data["level"] == "INFO"
    assert received_events[0].data["message"] == "Test message"


@pytest.mark.asyncio
async def test_event_publisher_system_health():
    """Test event publisher for system health events."""
    bus = EventBus()
    publisher = EventPublisher(source="test", event_bus=bus)
    
    received_events = []
    
    def handler(event: Event):
        received_events.append(event)
    
    bus.subscribe("system.health", handler)
    
    await publisher.publish_system_health("healthy", {"cpu": 45.2, "memory": 60.5})
    
    assert len(received_events) == 1
    assert received_events[0].data["status"] == "healthy"
    assert received_events[0].data["metrics"]["cpu"] == 45.2
