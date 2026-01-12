"""Platform-level event bus with Redis pub/sub support."""
from core.event_bus import EventBus, Event, EventType as CoreEventType, get_event_bus

# Re-export core components
__all__ = ["EventBus", "Event", "EventType", "get_event_bus", "PlatformEventBus"]

# Extended event types for platform
class EventType(CoreEventType):
    """Extended event types for platform features."""
    # Deployment events
    DEPLOYMENT_STARTED = "deployment.started"
    DEPLOYMENT_PROGRESS = "deployment.progress"
    DEPLOYMENT_COMPLETED = "deployment.completed"
    DEPLOYMENT_FAILED = "deployment.failed"
    
    # Plugin events
    PLUGIN_INSTALLED = "plugin.installed"
    PLUGIN_CONFIGURED = "plugin.configured"
    PLUGIN_STARTED = "plugin.started"
    PLUGIN_STOPPED = "plugin.stopped"
    PLUGIN_ERROR = "plugin.error"
    
    # System events
    SYSTEM_HEALTH = "system.health"
    SYSTEM_ALERT = "system.alert"
    
    # Log events
    LOG_ENTRY = "log.entry"
    LOG_ERROR = "log.error"
    
    # Config events
    CONFIG_CHANGED = "config.changed"
    CONFIG_VALIDATED = "config.validated"
    
    # IRC/ChatOps events
    IRC_COMMAND = "irc.command"
    IRC_NOTIFICATION = "irc.notification"


# Alias for backward compatibility
PlatformEventBus = EventBus
"""Event bus for the platform - pub/sub messaging system."""
from .bus import EventBus, create_event_bus
from .events import EventType, Event
from .subscribers import SubscriptionManager

__all__ = ["EventBus", "create_event_bus", "EventType", "Event", "SubscriptionManager"]
