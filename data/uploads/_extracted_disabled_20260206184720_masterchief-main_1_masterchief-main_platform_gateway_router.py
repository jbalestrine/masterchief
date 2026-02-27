"""Main API Gateway router."""
from flask import Blueprint, jsonify, request
import logging

logger = logging.getLogger(__name__)

gateway_bp = Blueprint('gateway', __name__)


@gateway_bp.route('/', methods=['GET'])
def index():
    """API Gateway index."""
    return jsonify({
        "service": "MasterChief API Gateway",
        "version": "2.0.0",
        "endpoints": {
            "/plugins": "Plugin Service",
            "/deployments": "Deployment Service",
            "/config": "Configuration Service",
            "/logs": "Log Service",
            "/metrics": "Metrics Service",
            "/system": "System Service",
            "/wizard": "Plugin Wizard",
            "/dashboard": "Dashboard Aggregator"
        }
    })


@gateway_bp.route('/routes', methods=['GET'])
def list_routes():
    """List all available routes."""
    routes = []
    # This will be populated dynamically based on registered services
    return jsonify({"routes": routes})


def create_gateway(app):
    """
    Create and configure the API gateway.
    
    Args:
        app: Flask application instance
    """
    # Import and register middleware
    from .middleware.auth import setup_auth_middleware
    from .middleware.rate_limit import setup_rate_limit_middleware
    from .middleware.logging import setup_logging_middleware
    from .middleware.cors import setup_cors_middleware
    
    # Setup middleware (order matters)
    setup_cors_middleware(app)
    setup_logging_middleware(app)
    setup_rate_limit_middleware(app)
    setup_auth_middleware(app)
    
    # Register gateway blueprint
    app.register_blueprint(gateway_bp, url_prefix='/api/v1')
    
    logger.info("API Gateway configured")
    return app
