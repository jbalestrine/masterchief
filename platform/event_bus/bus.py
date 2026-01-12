"""Core event bus implementation with backend abstraction."""
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class EventBus:
    """Abstract event bus interface."""
    
    def subscribe(self, event_type: str, handler):
        """Subscribe to an event type."""
        raise NotImplementedError
    
    def unsubscribe(self, event_type: str, handler):
        """Unsubscribe from an event type."""
        raise NotImplementedError
    
    def publish(self, event_type: str, data: dict):
        """Publish an event."""
        raise NotImplementedError
    
    async def publish_async(self, event_type: str, data: dict):
        """Publish an event asynchronously."""
        raise NotImplementedError


def create_event_bus(backend: str = None) -> EventBus:
    """
    Create an event bus with the specified backend.
    
    Args:
        backend: Backend type ('memory' or 'redis'). 
                 If None, uses EVENT_BUS_BACKEND env var or defaults to 'memory'.
    
    Returns:
        EventBus instance
    """
    if backend is None:
        backend = os.environ.get('EVENT_BUS_BACKEND', 'memory')
    
    backend = backend.lower()
    
    if backend == 'redis':
        try:
            from .redis_backend import RedisEventBus
            logger.info("Using Redis event bus backend")
            return RedisEventBus()
        except ImportError:
            logger.warning("Redis not available, falling back to in-memory event bus")
            backend = 'memory'
    
    if backend == 'memory':
        from .memory_backend import InMemoryEventBus
        logger.info("Using in-memory event bus backend")
        return InMemoryEventBus()
    
    raise ValueError(f"Unknown event bus backend: {backend}")
