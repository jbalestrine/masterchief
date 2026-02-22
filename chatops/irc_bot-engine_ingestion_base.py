"""Base classes for data ingestion system."""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class IngestionStatus(Enum):
    """Status of ingestion sources."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"
    PAUSED = "paused"


@dataclass
class IngestionEvent:
    """Event from an ingestion source."""
    source_type: str  # webhook, api, file, etc.
    source_id: str  # Unique identifier for the source
    data: Dict[str, Any]  # Event data
    metadata: Dict[str, Any]  # Additional metadata
    timestamp: float  # Event timestamp


class BaseIngestion(ABC):
    """Base class for all ingestion sources."""
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        """
        Initialize ingestion source.
        
        Args:
            source_id: Unique identifier for this source
            config: Configuration dictionary
        """
        self.source_id = source_id
        self.config = config
        self.status = IngestionStatus.STOPPED
        self.handlers: List[Callable[[IngestionEvent], None]] = []
        
    @abstractmethod
    async def start(self):
        """Start the ingestion source."""
        pass
    
    @abstractmethod
    async def stop(self):
        """Stop the ingestion source."""
        pass
    
    def add_handler(self, handler: Callable[[IngestionEvent], None]):
        """Add an event handler."""
        self.handlers.append(handler)
        logger.debug(f"Added handler to {self.source_id}")
    
    def remove_handler(self, handler: Callable[[IngestionEvent], None]):
        """Remove an event handler."""
        if handler in self.handlers:
            self.handlers.remove(handler)
            logger.debug(f"Removed handler from {self.source_id}")
    
    async def _dispatch_event(self, event: IngestionEvent):
        """Dispatch event to all handlers."""
        for handler in self.handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in handler for {self.source_id}: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get status information about this source."""
        return {
            "source_id": self.source_id,
            "source_type": self.__class__.__name__,
            "status": self.status.value,
            "config": self.config,
            "handler_count": len(self.handlers)
        }


class IngestionManager:
    """Manages all ingestion sources."""
    
    def __init__(self):
        """Initialize the ingestion manager."""
        self.sources: Dict[str, BaseIngestion] = {}
        self.running = False
        
    def register_source(self, source: BaseIngestion):
        """Register an ingestion source."""
        if source.source_id in self.sources:
            logger.warning(f"Source {source.source_id} already registered, replacing")
        self.sources[source.source_id] = source
        logger.info(f"Registered ingestion source: {source.source_id}")
    
    def unregister_source(self, source_id: str):
        """Unregister an ingestion source."""
        if source_id in self.sources:
            del self.sources[source_id]
            logger.info(f"Unregistered ingestion source: {source_id}")
    
    def get_source(self, source_id: str) -> Optional[BaseIngestion]:
        """Get an ingestion source by ID."""
        return self.sources.get(source_id)
    
    async def start_all(self):
        """Start all registered ingestion sources."""
        self.running = True
        for source_id, source in self.sources.items():
            try:
                await source.start()
                logger.info(f"Started ingestion source: {source_id}")
            except Exception as e:
                logger.error(f"Failed to start source {source_id}: {e}")
    
    async def stop_all(self):
        """Stop all registered ingestion sources."""
        self.running = False
        for source_id, source in self.sources.items():
            try:
                await source.stop()
                logger.info(f"Stopped ingestion source: {source_id}")
            except Exception as e:
                logger.error(f"Failed to stop source {source_id}: {e}")
    
    def get_all_status(self) -> List[Dict[str, Any]]:
        """Get status of all ingestion sources."""
        return [source.get_status() for source in self.sources.values()]
