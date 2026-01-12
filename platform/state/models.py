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
