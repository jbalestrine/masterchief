"""WebSocket server using Flask-SocketIO."""
import logging
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask import request

logger = logging.getLogger(__name__)

# Initialize SocketIO
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode='eventlet',
    logger=True,
    engineio_logger=True
)


def init_socketio(app):
    """Initialize SocketIO with Flask app."""
    socketio.init_app(app)
    logger.info("SocketIO initialized")
    return socketio


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    client_id = request.sid
    logger.info(f"Client connected: {client_id}")
    
    emit('connected', {
        'client_id': client_id,
        'message': 'Connected to MasterChief WebSocket'
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    client_id = request.sid
    logger.info(f"Client disconnected: {client_id}")


@socketio.on('subscribe')
def handle_subscribe(data):
    """Handle channel subscription."""
    channel = data.get('channel')
    
    if not channel:
        emit('error', {'message': 'Channel name required'})
        return
    
    join_room(channel)
    logger.info(f"Client {request.sid} subscribed to {channel}")
    
    emit('subscribed', {
        'channel': channel,
        'status': 'ok',
        'message': f'Subscribed to {channel}'
    })


@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    """Handle channel unsubscription."""
    channel = data.get('channel')
    
    if not channel:
        emit('error', {'message': 'Channel name required'})
        return
    
    leave_room(channel)
    logger.info(f"Client {request.sid} unsubscribed from {channel}")
    
    emit('unsubscribed', {
        'channel': channel,
        'status': 'ok',
        'message': f'Unsubscribed from {channel}'
    })


@socketio.on('ping')
def handle_ping():
    """Handle ping for connection testing."""
    emit('pong', {'timestamp': str(request.sid)})


@socketio.on_error_default
def default_error_handler(e):
    """Handle errors."""
    logger.error(f"SocketIO error: {e}")
    emit('error', {'message': str(e)})
