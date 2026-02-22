"""Tests for event bus."""
import pytest
import asyncio
from core.event_bus import EventBus, Event, EventType


@pytest.mark.asyncio
async def test_event_bus_publish_subscribe():
    """Test publishing and subscribing to events."""
    bus = EventBus(enable_logging=True)
    received_events = []
    
    def handler(event: Event):
        received_events.append(event)
    
    bus.subscribe(EventType.MODULE_LOADED.value, handler)
    
    event = Event(
        type=EventType.MODULE_LOADED.value,
        source="test",
        data={"module": "test-module"}
    )
    
    await bus.publish(event)
    
    assert len(received_events) == 1
    assert received_events[0].type == EventType.MODULE_LOADED.value


@pytest.mark.asyncio
async def test_event_bus_unsubscribe():
    """Test unsubscribing from events."""
    bus = EventBus()
    received_events = []
    
    def handler(event: Event):
        received_events.append(event)
    
    bus.subscribe(EventType.MODULE_LOADED.value, handler)
    bus.unsubscribe(EventType.MODULE_LOADED.value, handler)
    
    event = Event(
        type=EventType.MODULE_LOADED.value,
        source="test",
        data={}
    )
    
    await bus.publish(event)
    
    assert len(received_events) == 0


def test_event_bus_stats():
    """Test getting event bus statistics."""
    bus = EventBus()
    
    def handler(event: Event):
        pass
    
    bus.subscribe(EventType.MODULE_LOADED.value, handler)
    bus.subscribe(EventType.DEPLOYMENT_STARTED.value, handler)
    
    stats = bus.get_stats()
    
    assert stats["subscriber_count"] == 2
    assert EventType.MODULE_LOADED.value in stats["event_types"]
