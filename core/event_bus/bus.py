"""Event bus for inter-component communication.

This module provides functionality for event-driven communication between components.
"""

from typing import Any, Callable, Dict, List, Optional
import uuid


class Event:
    """Represents an event in the system."""
    
    def __init__(self, event_type: str, data: Optional[Dict[str, Any]] = None):
        self.event_id = str(uuid.uuid4())
        self.event_type = event_type
        self.data = data or {}


class EventBus:
    """Manages event-driven communication between components."""
    
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}
        self.event_history: List[Event] = []
    
    def subscribe(self, event_type: str, handler: Callable) -> bool:
        """Subscribe to an event type.
        
        Args:
            event_type: The type of event to subscribe to
            handler: The callback function to handle the event
            
        Returns:
            True if subscription was successful
        """
        # Lines 32-33 - Fixed: Removed unused variables (event_type parameter already exists)
        # The subscribe method uses the event_type parameter directly
        
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        
        self.handlers[event_type].append(handler)
        return True
    
    def unsubscribe(self, event_type: str, handler: Callable) -> bool:
        """Unsubscribe from an event type.
        
        Args:
            event_type: The type of event to unsubscribe from
            handler: The callback function to remove
            
        Returns:
            True if unsubscription was successful
        """
        if event_type not in self.handlers:
            return False
        
        if handler in self.handlers[event_type]:
            self.handlers[event_type].remove(handler)
            return True
        
        return False
    
    def publish(self, event: Event) -> bool:
        """Publish an event to all subscribers.
        
        Args:
            event: The event to publish
            
        Returns:
            True if the event was published successfully
        """
        self.event_history.append(event)
        
        if event.event_type not in self.handlers:
            return True
        
        for handler in self.handlers[event.event_type]:
            try:
                handler(event)
            except Exception:
                pass
        
        return True
    
    def get_event_history(self, event_type: Optional[str] = None) -> List[Event]:
        """Get the event history, optionally filtered by type.
        
        Args:
            event_type: Optional event type to filter by
            
        Returns:
            List of events
        """
        if event_type:
            return [e for e in self.event_history if e.event_type == event_type]
        return self.event_history
