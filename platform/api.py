"""
Flask API for MasterChief platform
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

logger = logging.getLogger(__name__)

def create_app(config):
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.config.from_mapping(config)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    from services.api import services_bp
    from bare_metal.api import bare_metal_bp
    from processes.api import processes_bp
    from packages.api import packages_bp
    from users.api import users_bp
    from cmdb.api import cmdb_bp
    from backup.api import backup_bp
    from monitoring.api import monitoring_bp
    
    app.register_blueprint(services_bp, url_prefix='/api/services')
    app.register_blueprint(bare_metal_bp, url_prefix='/api/bare-metal')
    app.register_blueprint(processes_bp, url_prefix='/api/processes')
    app.register_blueprint(packages_bp, url_prefix='/api/packages')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(cmdb_bp, url_prefix='/api/cmdb')
    app.register_blueprint(backup_bp, url_prefix='/api/backup')
    app.register_blueprint(monitoring_bp, url_prefix='/api/monitoring')
    
    @app.route('/')
    def index():
        return jsonify({
            'name': 'MasterChief DevOps Platform',
            'version': '1.0.0',
            'status': 'running',
        })
    
    @app.route('/api/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'components': {
                'api': 'up',
                'database': 'up',
                'monitoring': 'up',
            }
        })
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app
