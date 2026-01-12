"""
MasterChief Platform Application Factory.

This module creates and configures the Flask application with all extensions,
blueprints, and services for the DevOps Web GUI platform.
"""
import logging
from flask import Flask
from flask_socketio import SocketIO

logger = logging.getLogger(__name__)


def create_app(config=None):
    """
    Create and configure the Flask application.
    
    Args:
        config: Configuration object or dict
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config or 'config.default')
    app.config.setdefault('SECRET_KEY', 'change-me-in-production')
    app.config.setdefault('JWT_SECRET', 'change-me-in-production')
    
    # Initialize logging
    setup_logging(app)
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Setup event bus integration
    setup_event_bus(app)
    
    logger.info("MasterChief Platform application created")
    return app


def init_extensions(app):
    """Initialize Flask extensions."""
    # Initialize Redis
    redis_client = init_redis(app)
    app.extensions['redis'] = redis_client
    
    # Initialize SocketIO
    from platform.realtime import init_socketio
    socketio = init_socketio(app)
    app.extensions['socketio'] = socketio
    
    # Initialize state store
    from platform.state import get_state_store
    state_store = get_state_store(redis_client=redis_client)
    app.extensions['state_store'] = state_store
    
    # Initialize log storage
    from platform.logs import LogStorage
    log_storage = LogStorage(redis_client=redis_client)
    app.extensions['log_storage'] = log_storage
    
    # Initialize log API
    from platform.logs.api import init_logs_api
    init_logs_api(log_storage)
    
    logger.info("Extensions initialized")


def init_redis(app):
    """Initialize Redis client."""
    import redis
    redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
    
    try:
        client = redis.from_url(redis_url, decode_responses=True)
        client.ping()
        logger.info(f"Connected to Redis: {redis_url}")
        return client
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}")
        return None


def register_blueprints(app):
    """Register Flask blueprints."""
    # API Gateway
    from platform.gateway import gateway_bp, health_bp
    app.register_blueprint(gateway_bp, url_prefix='/api/v1')
    app.register_blueprint(health_bp)
    
    # Logs API
    from platform.logs import logs_bp
    app.register_blueprint(logs_bp, url_prefix='/api/v1')
    
    # Data Upload API
    from platform.data import data_bp
    app.register_blueprint(data_bp, url_prefix='/api/v1/data')
    
    # Platform API (existing)
    try:
        from platform.api import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
    except ImportError:
        logger.warning("Platform API blueprint not found")
    
    logger.info("Blueprints registered")


def setup_event_bus(app):
    """Setup event bus and integrate with WebSocket."""
    from core.event_bus import get_event_bus
    from platform.realtime import register_handlers
    
    event_bus = get_event_bus()
    socketio = app.extensions.get('socketio')
    
    if socketio:
        register_handlers(socketio, event_bus)
        logger.info("Event bus integrated with WebSocket")
    
    app.extensions['event_bus'] = event_bus


def setup_logging(app):
    """Setup application logging."""
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def run_app(app, host='0.0.0.0', port=8080, debug=False):
    """
    Run the Flask application with SocketIO.
    
    Args:
        app: Flask application
        host: Host address
        port: Port number
        debug: Debug mode
    """
    socketio = app.extensions.get('socketio')
    
    if socketio:
        logger.info(f"Starting MasterChief Platform on {host}:{port}")
        socketio.run(app, host=host, port=port, debug=debug)
    else:
        logger.info(f"Starting MasterChief Platform (no WebSocket) on {host}:{port}")
        app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    app = create_app()
    run_app(app, debug=True)
