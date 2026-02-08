"""WebSocket event handlers."""
import logging
from flask_socketio import emit
from .channels import Channel

logger = logging.getLogger(__name__)


def register_handlers(socketio, event_bus=None):
    """
    Register WebSocket handlers with event bus integration.
    
    Args:
        socketio: SocketIO instance
        event_bus: Event bus for subscribing to events
    """
    if event_bus:
        # Subscribe to events and broadcast to WebSocket channels
        event_bus.subscribe("deployment.started", lambda e: broadcast_deployment_event(socketio, e))
        event_bus.subscribe("deployment.progress", lambda e: broadcast_deployment_event(socketio, e))
        event_bus.subscribe("deployment.completed", lambda e: broadcast_deployment_event(socketio, e))
        event_bus.subscribe("deployment.failed", lambda e: broadcast_deployment_event(socketio, e))
        
        event_bus.subscribe("plugin.installed", lambda e: broadcast_plugin_event(socketio, e))
        event_bus.subscribe("plugin.configured", lambda e: broadcast_plugin_event(socketio, e))
        event_bus.subscribe("plugin.started", lambda e: broadcast_plugin_event(socketio, e))
        event_bus.subscribe("plugin.stopped", lambda e: broadcast_plugin_event(socketio, e))
        
        event_bus.subscribe("log.entry", lambda e: broadcast_log_event(socketio, e))
        event_bus.subscribe("system.health", lambda e: broadcast_system_event(socketio, e))
        event_bus.subscribe("system.alert", lambda e: broadcast_alert_event(socketio, e))
        
        logger.info("WebSocket handlers registered with event bus")


def broadcast_deployment_event(socketio, event):
    """Broadcast deployment event to WebSocket clients."""
    try:
        socketio.emit(
            'deployment_update',
            {
                'event_type': event.type,
                'data': event.data,
                'timestamp': event.timestamp
            },
            room=Channel.DEPLOYMENTS.value
        )
    except Exception as e:
        logger.error(f"Error broadcasting deployment event: {e}")


def broadcast_plugin_event(socketio, event):
    """Broadcast plugin event to WebSocket clients."""
    try:
        socketio.emit(
            'plugin_update',
            {
                'event_type': event.type,
                'data': event.data,
                'timestamp': event.timestamp
            },
            room=Channel.PLUGINS.value
        )
    except Exception as e:
        logger.error(f"Error broadcasting plugin event: {e}")


def broadcast_log_event(socketio, event):
    """Broadcast log event to WebSocket clients."""
    try:
        socketio.emit(
            'log_entry',
            {
                'level': event.data.get('level'),
                'message': event.data.get('message'),
                'metadata': event.data.get('metadata', {}),
                'timestamp': event.timestamp
            },
            room=Channel.LOGS.value
        )
    except Exception as e:
        logger.error(f"Error broadcasting log event: {e}")


def broadcast_system_event(socketio, event):
    """Broadcast system event to WebSocket clients."""
    try:
        socketio.emit(
            'system_update',
            {
                'status': event.data.get('status'),
                'metrics': event.data.get('metrics', {}),
                'timestamp': event.timestamp
            },
            room=Channel.SYSTEM.value
        )
    except Exception as e:
        logger.error(f"Error broadcasting system event: {e}")


def broadcast_alert_event(socketio, event):
    """Broadcast alert to WebSocket clients."""
    try:
        socketio.emit(
            'alert',
            {
                'severity': event.data.get('severity', 'info'),
                'message': event.data.get('message'),
                'details': event.data.get('details', {}),
                'timestamp': event.timestamp
            },
            room=Channel.ALERTS.value
        )
    except Exception as e:
        logger.error(f"Error broadcasting alert: {e}")


def broadcast_wizard_progress(socketio, session_id, step, progress, data=None):
    """Broadcast wizard progress update."""
    try:
        socketio.emit(
            'wizard_progress',
            {
                'session_id': session_id,
                'step': step,
                'progress': progress,
                'data': data or {}
            },
            room=Channel.WIZARD.value
        )
    except Exception as e:
        logger.error(f"Error broadcasting wizard progress: {e}")


def broadcast_chat_message(socketio, message, user, channel='general'):
    """Broadcast IRC chat message."""
    try:
        socketio.emit(
            'chat_message',
            {
                'message': message,
                'user': user,
                'channel': channel
            },
            room=Channel.CHAT.value
        )
    except Exception as e:
        logger.error(f"Error broadcasting chat message: {e}")
