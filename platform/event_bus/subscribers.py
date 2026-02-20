"""Subscription management utilities."""
import logging
from typing import Callable, Dict, List, Set
from dataclasses import dataclass, field
"""Subscription management and helper utilities."""
import logging
from typing import Callable, List, Optional
from functools import wraps

logger = logging.getLogger(__name__)


@dataclass
class Subscriber:
    """Represents a subscriber to events."""
    id: str
    event_types: Set[str] = field(default_factory=set)
    handler: Callable = None
    active: bool = True
    metadata: Dict = field(default_factory=dict)


class SubscriptionManager:
    """Manages event subscriptions."""
    
    def __init__(self):
        self.subscribers: Dict[str, Subscriber] = {}
        self.event_type_index: Dict[str, Set[str]] = {}  # event_type -> set of subscriber_ids
    
    def add_subscriber(self, subscriber_id: str, handler: Callable, metadata: Dict = None) -> Subscriber:
        """Add a new subscriber."""
        if subscriber_id in self.subscribers:
            logger.warning(f"Subscriber {subscriber_id} already exists, updating")
        
        subscriber = Subscriber(
            id=subscriber_id,
            handler=handler,
            metadata=metadata or {}
        )
        self.subscribers[subscriber_id] = subscriber
        logger.info(f"Added subscriber: {subscriber_id}")
        return subscriber
    
    def remove_subscriber(self, subscriber_id: str):
        """Remove a subscriber."""
        if subscriber_id in self.subscribers:
            subscriber = self.subscribers[subscriber_id]
            # Remove from event type index
            for event_type in subscriber.event_types:
                if event_type in self.event_type_index:
                    self.event_type_index[event_type].discard(subscriber_id)
            
            del self.subscribers[subscriber_id]
            logger.info(f"Removed subscriber: {subscriber_id}")
    
    def subscribe_to_event(self, subscriber_id: str, event_type: str):
        """Subscribe a subscriber to an event type."""
        if subscriber_id not in self.subscribers:
            logger.error(f"Subscriber {subscriber_id} not found")
            return
        
        subscriber = self.subscribers[subscriber_id]
        subscriber.event_types.add(event_type)
        
        if event_type not in self.event_type_index:
            self.event_type_index[event_type] = set()
        self.event_type_index[event_type].add(subscriber_id)
        
        logger.debug(f"Subscriber {subscriber_id} subscribed to {event_type}")
    
    def unsubscribe_from_event(self, subscriber_id: str, event_type: str):
        """Unsubscribe from an event type."""
        if subscriber_id not in self.subscribers:
            return
        
        subscriber = self.subscribers[subscriber_id]
        subscriber.event_types.discard(event_type)
        
        if event_type in self.event_type_index:
            self.event_type_index[event_type].discard(subscriber_id)
    
    def get_subscribers_for_event(self, event_type: str) -> List[Subscriber]:
        """Get all active subscribers for an event type."""
        if event_type not in self.event_type_index:
            return []
        
        subscriber_ids = self.event_type_index[event_type]
        return [
            self.subscribers[sid]
            for sid in subscriber_ids
            if sid in self.subscribers and self.subscribers[sid].active
        ]
    
    def get_stats(self) -> Dict:
        """Get subscription statistics."""
        return {
            "total_subscribers": len(self.subscribers),
            "active_subscribers": sum(1 for s in self.subscribers.values() if s.active),
            "event_types": len(self.event_type_index),
            "subscriptions": sum(len(s.event_types) for s in self.subscribers.values())
        }
class SubscriptionManager:
    """
    Manages event subscriptions with helper methods.
    
    This class provides a convenient interface for managing subscriptions
    to the event bus, including automatic cleanup and subscription groups.
    """
    
    def __init__(self, event_bus):
        """
        Initialize subscription manager.
        
        Args:
            event_bus: The event bus instance to manage subscriptions for
        """
        self.event_bus = event_bus
        self._subscriptions: List[tuple] = []
    
    def subscribe(self, event_type: str, handler: Callable):
        """
        Subscribe to an event type and track the subscription.
        
        Args:
            event_type: The event type to subscribe to
            handler: The handler function
        """
        self.event_bus.subscribe(event_type, handler)
        self._subscriptions.append((event_type, handler))
        logger.debug(f"Registered subscription: {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: The event type to unsubscribe from
            handler: The handler function
        """
        self.event_bus.unsubscribe(event_type, handler)
        if (event_type, handler) in self._subscriptions:
            self._subscriptions.remove((event_type, handler))
        logger.debug(f"Removed subscription: {event_type}")
    
    def unsubscribe_all(self):
        """Unsubscribe from all tracked subscriptions."""
        for event_type, handler in self._subscriptions:
            self.event_bus.unsubscribe(event_type, handler)
        self._subscriptions.clear()
        logger.info("Unsubscribed from all events")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup subscriptions."""
        self.unsubscribe_all()


def event_handler(event_type: str):
    """
    Decorator to mark a function as an event handler.
    
    Usage:
        @event_handler('plugin.created')
        def on_plugin_created(event_type, data):
            print(f"Plugin created: {data}")
    
    Args:
        event_type: The event type this handler processes
        
    Returns:
        Decorated function with event_type attribute
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        wrapper.event_type = event_type
        return wrapper
    
    return decorator


class EventHandlerRegistry:
    """
    Registry for event handlers with automatic subscription.
    
    This class allows you to register handlers and automatically
    subscribe them to the event bus.
    """
    
    def __init__(self, event_bus):
        """
        Initialize handler registry.
        
        Args:
            event_bus: The event bus to subscribe handlers to
        """
        self.event_bus = event_bus
        self._handlers: List[tuple] = []
    
    def register(self, handler: Callable):
        """
        Register a handler decorated with @event_handler.
        
        Args:
            handler: Handler function with event_type attribute
        """
        if not hasattr(handler, 'event_type'):
            raise ValueError(
                "Handler must be decorated with @event_handler"
            )
        
        event_type = handler.event_type
        self.event_bus.subscribe(event_type, handler)
        self._handlers.append((event_type, handler))
        logger.info(f"Registered handler for {event_type}: {handler.__name__}")
    
    def register_all(self, module):
        """
        Register all handlers from a module.
        
        Args:
            module: Python module containing event handlers
        """
        import inspect
        
        for name, obj in inspect.getmembers(module):
            if callable(obj) and hasattr(obj, 'event_type'):
                self.register(obj)
    
    def unregister_all(self):
        """Unregister all handlers."""
        for event_type, handler in self._handlers:
            self.event_bus.unsubscribe(event_type, handler)
        self._handlers.clear()
        logger.info("Unregistered all handlers")
