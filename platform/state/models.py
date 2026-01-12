"""State data models."""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional
from datetime import datetime
from enum import Enum


class StateStatus(Enum):
    """State status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ERROR = "error"


@dataclass
class StateModel:
    """Base state model."""
    id: str
    status: StateStatus = StateStatus.ACTIVE
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['status'] = self.status.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary."""
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = StateStatus(data['status'])
        return cls(**data)


@dataclass
class DeploymentState(StateModel):
    """Deployment state model."""
    environment: str = ""
    target: str = ""
    progress: int = 0
    message: str = ""
    result: Optional[Dict[str, Any]] = None


@dataclass
class PluginState(StateModel):
    """Plugin state model."""
    name: str = ""
    version: str = ""
    enabled: bool = True
    configuration: Dict[str, Any] = field(default_factory=dict)
    health: str = "unknown"


@dataclass
class SystemState(StateModel):
    """System state model."""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    active_deployments: int = 0
    active_plugins: int = 0
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class StateEntry:
    """
    Represents a single state entry.
    
    This model is used for structured state management and can be
    stored in any of the state store backends.
    """
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if the entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'key': self.key,
            'value': self.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StateEntry':
        """Create from dictionary."""
        return cls(
            key=data['key'],
            value=data['value'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            metadata=data.get('metadata', {})
        )
