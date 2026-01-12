"""Subscription management utilities."""
import logging
from typing import Callable, Dict, List, Set
from dataclasses import dataclass, field

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
