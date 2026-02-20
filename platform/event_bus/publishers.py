"""Publishing utilities for events."""
import logging
from typing import Dict, Any, Optional
from core.event_bus import Event, get_event_bus

logger = logging.getLogger(__name__)


class EventPublisher:
    """Utility class for publishing events with common patterns."""
    
    def __init__(self, source: str, event_bus=None):
        self.source = source
        self.event_bus = event_bus or get_event_bus()
    
    async def publish_deployment_started(self, deployment_id: str, metadata: Dict[str, Any]):
        """Publish deployment started event."""
        event = Event(
            type="deployment.started",
            source=self.source,
            data={
                "deployment_id": deployment_id,
                "metadata": metadata
            }
        )
        await self.event_bus.publish(event)
        logger.info(f"Published deployment started: {deployment_id}")
    
    async def publish_deployment_progress(self, deployment_id: str, progress: int, message: str):
        """Publish deployment progress event."""
        event = Event(
            type="deployment.progress",
            source=self.source,
            data={
                "deployment_id": deployment_id,
                "progress": progress,
                "message": message
            }
        )
        await self.event_bus.publish(event)
    
    async def publish_deployment_completed(self, deployment_id: str, result: Dict[str, Any]):
        """Publish deployment completed event."""
        event = Event(
            type="deployment.completed",
            source=self.source,
            data={
                "deployment_id": deployment_id,
                "result": result
            }
        )
        await self.event_bus.publish(event)
        logger.info(f"Published deployment completed: {deployment_id}")
    
    async def publish_deployment_failed(self, deployment_id: str, error: str):
        """Publish deployment failed event."""
        event = Event(
            type="deployment.failed",
            source=self.source,
            data={
                "deployment_id": deployment_id,
                "error": error
            }
        )
        await self.event_bus.publish(event)
        logger.error(f"Published deployment failed: {deployment_id}")
    
    async def publish_plugin_event(self, event_type: str, plugin_id: str, data: Dict[str, Any]):
        """Publish plugin-related event."""
        event = Event(
            type=event_type,
            source=self.source,
            data={
                "plugin_id": plugin_id,
                **data
            }
        )
        await self.event_bus.publish(event)
    
    async def publish_log_entry(self, level: str, message: str, metadata: Optional[Dict] = None):
        """Publish log entry event."""
        event = Event(
            type="log.entry",
            source=self.source,
            data={
                "level": level,
                "message": message,
                "metadata": metadata or {}
            }
        )
        await self.event_bus.publish(event)
    
    async def publish_system_health(self, status: str, metrics: Dict[str, Any]):
        """Publish system health event."""
        event = Event(
            type="system.health",
            source=self.source,
            data={
                "status": status,
                "metrics": metrics
            }
        )
        await self.event_bus.publish(event)
    
    async def publish_irc_command(self, command: str, args: list, user: str):
        """Publish IRC command event."""
        event = Event(
            type="irc.command",
            source=self.source,
            data={
                "command": command,
                "args": args,
                "user": user
            }
        )
        await self.event_bus.publish(event)
