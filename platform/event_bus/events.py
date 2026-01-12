"""Event type definitions and utilities."""
from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, Optional
from datetime import datetime
import uuid


class EventPriority(Enum):
    """Event priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class PlatformEvent:
    """Enhanced event with additional metadata."""
    type: str
    source: str
    data: Dict[str, Any]
    priority: EventPriority = EventPriority.NORMAL
    timestamp: Optional[str] = None
    id: Optional[str] = None
    correlation_id: Optional[str] = None  # For tracing related events
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
        if self.id is None:
            self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "source": self.source,
            "data": self.data,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "id": self.id,
            "correlation_id": self.correlation_id
        }
"""Event type definitions and event data structures."""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
import uuid
import json


class EventType(Enum):
    """Standard event types for the platform."""
    
    # Module events
    MODULE_LOADED = "module.loaded"
    MODULE_UNLOADED = "module.unloaded"
    MODULE_ERROR = "module.error"
    
    # Configuration events
    CONFIG_CHANGED = "config.changed"
    CONFIG_VALIDATED = "config.validated"
    CONFIG_ERROR = "config.error"
    
    # Deployment events
    DEPLOYMENT_STARTED = "deployment.started"
    DEPLOYMENT_COMPLETED = "deployment.completed"
    DEPLOYMENT_FAILED = "deployment.failed"
    DEPLOYMENT_PROGRESS = "deployment.progress"
    
    # Plugin events
    PLUGIN_CREATED = "plugin.created"
    PLUGIN_UPDATED = "plugin.updated"
    PLUGIN_DELETED = "plugin.deleted"
    PLUGIN_ENABLED = "plugin.enabled"
    PLUGIN_DISABLED = "plugin.disabled"
    
    # System events
    SYSTEM_STARTED = "system.started"
    SYSTEM_STOPPED = "system.stopped"
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"
    
    # Alert events
    ALERT_TRIGGERED = "alert.triggered"
    ALERT_RESOLVED = "alert.resolved"
    
    # Webhook events
    WEBHOOK_RECEIVED = "webhook.received"
    
    # Real-time events
    WEBSOCKET_CONNECTED = "websocket.connected"
    WEBSOCKET_DISCONNECTED = "websocket.disconnected"
    WEBSOCKET_MESSAGE = "websocket.message"
    
    # Task events
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_PROGRESS = "task.progress"
    
    # Custom events
    CUSTOM = "custom"


@dataclass
class Event:
    """
    Event data structure.
    
    Represents a single event in the system with metadata and payload.
    """
    type: str
    source: str
    data: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Event':
        """Create event from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


def create_event(
    event_type: EventType,
    source: str,
    data: Dict[str, Any],
    correlation_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> Event:
    """
    Create an event with the given parameters.
    
    Args:
        event_type: The type of event (EventType enum)
        source: The source of the event (e.g., 'plugin_wizard', 'deployment_engine')
        data: Event payload data
        correlation_id: Optional correlation ID for tracking related events
        user_id: Optional user ID who triggered the event
        
    Returns:
        Event instance
    """
    return Event(
        type=event_type.value,
        source=source,
        data=data,
        correlation_id=correlation_id,
        user_id=user_id
    )
