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
Flask Application Factory for MasterChief Platform
Creates and configures the Flask app with all extensions
"""
import os
import logging
from pathlib import Path
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global SocketIO instance
socketio = None


def create_app(config_override=None):
    """
    Create and configure Flask application.
    
    Args:
        config_override: Optional dict to override default config
        
    Returns:
        Flask app instance
    """
    # Import config here to avoid circular imports
    from platform.config import Config
    
    app = Flask(__name__)
    
    # Load configuration
    config = Config()
    if config_override:
        for key, value in config_override.items():
            setattr(config, key, value)
    
    # Basic Flask config
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['DEBUG'] = config.DEBUG
    
    # CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize SocketIO
    global socketio
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode='eventlet',
        logger=True,
        engineio_logger=False
    )
    
    # Register API blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Static files / React frontend
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        """Serve React frontend or API docs."""
        # For now, just return a simple HTML page
        # Later we'll serve the actual React build
        if path.startswith('api/'):
            return jsonify({'error': 'Not found'}), 404
        
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MasterChief DevOps Platform</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 1200px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #f5f5f5;
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 { color: #2c3e50; }
                .section { margin: 30px 0; }
                .endpoint { 
                    background: #ecf0f1;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 4px;
                    font-family: monospace;
                }
                .badge {
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 12px;
                    font-weight: bold;
                    margin-right: 10px;
                }
                .get { background: #3498db; color: white; }
                .post { background: #2ecc71; color: white; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎮 MasterChief DevOps Platform</h1>
                <p>Welcome to the MasterChief DevOps Automation Platform!</p>
                
                <div class="section">
                    <h2>📡 API Endpoints</h2>
                    <div class="endpoint">
                        <span class="badge get">GET</span>
                        <strong>/api/v1/health</strong> - Health check
                    </div>
                    <div class="endpoint">
                        <span class="badge get">GET</span>
                        <strong>/api/v1/scripts</strong> - List scripts
                    </div>
                    <div class="endpoint">
                        <span class="badge post">POST</span>
                        <strong>/api/v1/scripts/generate</strong> - Generate script from description
                    </div>
                    <div class="endpoint">
                        <span class="badge get">GET</span>
                        <strong>/api/v1/plugins</strong> - List plugins
                    </div>
                    <div class="endpoint">
                        <span class="badge post">POST</span>
                        <strong>/api/v1/plugins/wizard/start</strong> - Start plugin wizard
                    </div>
                    <div class="endpoint">
                        <span class="badge get">GET</span>
                        <strong>/api/v1/dashboard</strong> - Dashboard data
                    </div>
                </div>
                
                <div class="section">
                    <h2>🔌 WebSocket</h2>
                    <p>Connect to: <code>ws://localhost:8080/socket.io</code></p>
                    <p>Events: <code>connect</code>, <code>log_update</code>, <code>script_status</code>, <code>deployment_update</code></p>
                </div>
                
                <div class="section">
                    <h2>🤖 IRC Bot Commands</h2>
                    <ul>
                        <li><code>!script create &lt;description&gt;</code> - Generate a script</li>
                        <li><code>!script list</code> - List all scripts</li>
                        <li><code>!plugin wizard</code> - Start plugin wizard</li>
                        <li><code>!deploy status</code> - Check deployment status</li>
                        <li><code>!help</code> - Show all commands</li>
                    </ul>
                </div>
                
                <div class="section">
                    <h2>💻 CLI</h2>
                    <p>Use the <code>masterchief</code> command:</p>
                    <ul>
                        <li><code>masterchief start</code> - Start platform</li>
                        <li><code>masterchief script create &lt;desc&gt;</code> - Generate script</li>
                        <li><code>masterchief plugin wizard</code> - Plugin wizard</li>
                        <li><code>masterchief --help</code> - Show all commands</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
    
    logger.info("Flask app created successfully")
    return app


def register_blueprints(app):
    """Register all API blueprints."""
    try:
        # Import and register API modules
        from flask import Blueprint
        
        api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
        
        @api_v1.route('/health', methods=['GET'])
        def health():
            return jsonify({
                'status': 'healthy',
                'version': '1.0.0',
                'platform': 'MasterChief DevOps'
            })
        
        app.register_blueprint(api_v1)
        
        # Register Script Wizard API
        try:
            from platform.script_wizard.api import script_wizard_bp
            app.register_blueprint(script_wizard_bp)
            logger.info("Script Wizard API registered")
        except ImportError as e:
            logger.warning(f"Script Wizard API not available: {e}")
        
        logger.info("API blueprints registered")
        
    except Exception as e:
        logger.error(f"Error registering blueprints: {e}")


def register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {error}")
        return jsonify({'error': 'Internal server error'}), 500


def run_server():
    """Run the Flask server with SocketIO."""
    from platform.config import Config
    
    config = Config()
    app = create_app()
    
    logger.info(f"Starting MasterChief on {config.HOST}:{config.PORT}")
    logger.info(f"Debug mode: {config.DEBUG}")
    logger.info(f"Environment: {config.ENV}")
    
    # Use eventlet for WebSocket support
    socketio.run(
        app,
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        use_reloader=False  # Disable reloader in production
    )
