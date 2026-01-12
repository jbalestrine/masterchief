"""Logging middleware."""
import logging
import time
from flask import request, g
import uuid

logger = logging.getLogger(__name__)


def setup_logging_middleware(app):
    """Setup request/response logging middleware."""
    
    @app.before_request
    def before_request():
        """Log request and set request ID."""
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()
        
        logger.info(
            f"Request started: {request.method} {request.path}",
            extra={
                'request_id': g.request_id,
                'method': request.method,
                'path': request.path,
                'remote_addr': request.remote_addr
            }
        )
    
    @app.after_request
    def after_request(response):
        """Log response."""
        if hasattr(g, 'start_time'):
            elapsed = time.time() - g.start_time
            
            logger.info(
                f"Request completed: {request.method} {request.path} - {response.status_code}",
                extra={
                    'request_id': g.request_id if hasattr(g, 'request_id') else 'unknown',
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'elapsed_time': elapsed
                }
            )
        
        # Add request ID to response headers
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        
        return response
    
    logger.info("Logging middleware configured")
