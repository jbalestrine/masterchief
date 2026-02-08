"""CORS middleware."""
import logging
from flask_cors import CORS

logger = logging.getLogger(__name__)


def setup_cors_middleware(app):
    """Setup CORS middleware."""
    app.config.setdefault('CORS_ORIGINS', '*')
    app.config.setdefault('CORS_ALLOW_HEADERS', ['Content-Type', 'Authorization'])
    app.config.setdefault('CORS_METHODS', ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
    
    CORS(
        app,
        origins=app.config['CORS_ORIGINS'],
        allow_headers=app.config['CORS_ALLOW_HEADERS'],
        methods=app.config['CORS_METHODS'],
        supports_credentials=True
    )
    
    logger.info("CORS middleware configured")
