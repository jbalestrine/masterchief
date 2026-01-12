"""
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
        # Import and register API modules as they're created
        # For now, just register basic health endpoint
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
