"""Event bus for internal pub/sub messaging and event-driven architecture."""
import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Standard event types."""
    MODULE_LOADED = "module.loaded"
    MODULE_UNLOADED = "module.unloaded"
    CONFIG_CHANGED = "config.changed"
    DEPLOYMENT_STARTED = "deployment.started"
    DEPLOYMENT_COMPLETED = "deployment.completed"
    DEPLOYMENT_FAILED = "deployment.failed"
    ALERT_TRIGGERED = "alert.triggered"
    WEBHOOK_RECEIVED = "webhook.received"
    CUSTOM = "custom"


@dataclass
class Event:
    """Event data structure."""
    type: str
    source: str
    data: Dict[str, Any]
    timestamp: str = None
    id: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
        if self.id is None:
            import uuid
            self.id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict())


class EventBus:
    """Internal pub/sub event bus for module communication."""

    def __init__(self, enable_logging: bool = True):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_log: List[Event] = []
        self.enable_logging = enable_logging
        self.webhook_handlers: Dict[str, Callable] = {}
        self._lock = asyncio.Lock()

    async def publish(self, event: Event):
        """Publish an event to all subscribers."""
        logger.debug(f"Publishing event: {event.type} from {event.source}")
        
        async with self._lock:
            # Log event if enabled
            if self.enable_logging:
                self.event_log.append(event)
        
        # Notify subscribers (outside lock to prevent deadlock)
        event_type = event.type
        if event_type in self.subscribers:
            tasks = []
            for handler in self.subscribers[event_type]:
                # Support both sync and async handlers
                if asyncio.iscoroutinefunction(handler):
                    tasks.append(handler(event))
                else:
                    try:
                        handler(event)
                    except Exception as e:
                        logger.error(f"Error in event handler: {e}")
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to events of a specific type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(handler)
        logger.info(f"Subscribed handler to event type: {event_type}")

    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from events."""
        if event_type in self.subscribers:
            if handler in self.subscribers[event_type]:
                self.subscribers[event_type].remove(handler)
                logger.info(f"Unsubscribed handler from event type: {event_type}")

    def register_webhook_handler(self, webhook_name: str, handler: Callable):
        """Register a handler for external webhooks."""
        self.webhook_handlers[webhook_name] = handler
        logger.info(f"Registered webhook handler: {webhook_name}")

    async def dispatch_webhook(self, webhook_name: str, payload: Dict[str, Any]) -> bool:
        """Dispatch a webhook to its registered handler."""
        if webhook_name in self.webhook_handlers:
            try:
                handler = self.webhook_handlers[webhook_name]
                if asyncio.iscoroutinefunction(handler):
                    await handler(payload)
                else:
                    handler(payload)
                
                # Publish webhook event
                event = Event(
                    type=EventType.WEBHOOK_RECEIVED.value,
                    source="webhook",
                    data={"webhook_name": webhook_name, "payload": payload}
                )
                await self.publish(event)
                return True
            except Exception as e:
                logger.error(f"Error dispatching webhook {webhook_name}: {e}")
                return False
        else:
            logger.warning(f"No handler registered for webhook: {webhook_name}")
            return False

    def get_event_log(self, limit: Optional[int] = None, event_type: Optional[str] = None) -> List[Event]:
        """Get event log with optional filtering."""
        events = self.event_log
        
        if event_type:
            events = [e for e in events if e.type == event_type]
        
        if limit:
            events = events[-limit:]
        
        return events

    def clear_event_log(self):
        """Clear the event log."""
        self.event_log.clear()
        logger.info("Event log cleared")

    async def replay_events(self, events: List[Event]):
        """Replay a sequence of events."""
        logger.info(f"Replaying {len(events)} events")
        for event in events:
            await self.publish(event)

    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        return {
            "total_events": len(self.event_log),
            "subscriber_count": sum(len(handlers) for handlers in self.subscribers.values()),
            "event_types": list(self.subscribers.keys()),
            "webhook_handlers": list(self.webhook_handlers.keys()),
        }


# Singleton instance
_event_bus_instance: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get or create the global event bus instance."""
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus()
    return _event_bus_instance
