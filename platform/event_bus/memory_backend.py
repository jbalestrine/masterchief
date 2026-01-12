"""In-memory event bus implementation - NO external dependencies."""
import asyncio
import logging
import queue
import threading
from collections import defaultdict
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


class InMemoryEventBus:
    """
    Thread-safe in-memory event bus - NO external dependencies.
    
    This implementation uses Python's built-in threading and queue modules
    to provide a simple pub/sub system without requiring Redis or other
    external message brokers.
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = threading.RLock()
        self._queue = queue.Queue()
        self._running = False
        self._worker_thread = None
    
    def subscribe(self, event_type: str, handler: Callable):
        """
        Subscribe a handler to an event type.
        
        Args:
            event_type: The event type to subscribe to
            handler: Callable that accepts (event_type, data) arguments
        """
        with self._lock:
            if handler not in self._subscribers[event_type]:
                self._subscribers[event_type].append(handler)
                logger.debug(f"Subscribed handler to event type: {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """
        Unsubscribe a handler from an event type.
        
        Args:
            event_type: The event type to unsubscribe from
            handler: The handler to remove
        """
        with self._lock:
            if handler in self._subscribers[event_type]:
                self._subscribers[event_type].remove(handler)
                logger.debug(f"Unsubscribed handler from event type: {event_type}")
    
    def publish(self, event_type: str, data: Any):
        """
        Publish an event synchronously.
        
        Args:
            event_type: The type of event
            data: Event data (dict, list, or any serializable object)
        """
        with self._lock:
            handlers = self._subscribers.get(event_type, []).copy()
        
        # Execute handlers outside the lock to prevent deadlocks
        for handler in handlers:
            try:
                handler(event_type, data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}", exc_info=True)
    
    async def publish_async(self, event_type: str, data: Any):
        """
        Publish an event asynchronously (for use with asyncio).
        
        Args:
            event_type: The type of event
            data: Event data
        """
        # For in-memory, we can just call publish synchronously
        # since it's already thread-safe
        self.publish(event_type, data)
    
    def get_subscriber_count(self, event_type: str = None) -> int:
        """
        Get the number of subscribers.
        
        Args:
            event_type: Optional event type to filter by
            
        Returns:
            Number of subscribers
        """
        with self._lock:
            if event_type:
                return len(self._subscribers.get(event_type, []))
            return sum(len(handlers) for handlers in self._subscribers.values())
    
    def get_event_types(self) -> List[str]:
        """
        Get all registered event types.
        
        Returns:
            List of event type strings
        """
        with self._lock:
            return list(self._subscribers.keys())
    
    def clear(self):
        """Clear all subscriptions."""
        with self._lock:
            self._subscribers.clear()
            logger.info("Cleared all event subscriptions")
