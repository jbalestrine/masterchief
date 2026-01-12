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
