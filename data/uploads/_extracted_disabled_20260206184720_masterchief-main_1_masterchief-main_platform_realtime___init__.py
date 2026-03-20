"""Real-time communication layer."""
from .server import socketio, init_socketio
from .channels import CHANNELS, Channel
from .handlers import register_handlers

__all__ = ["socketio", "init_socketio", "CHANNELS", "Channel", "register_handlers"]
