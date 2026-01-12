"""Rate limiting middleware."""
import logging
from flask import request, jsonify
from functools import wraps
import time
from collections import defaultdict

logger = logging.getLogger(__name__)

# In-memory rate limit store (use Redis in production)
rate_limit_store = defaultdict(list)


def setup_rate_limit_middleware(app):
    """Setup rate limiting middleware."""
    app.config.setdefault('RATE_LIMIT_REQUESTS', 100)
    app.config.setdefault('RATE_LIMIT_WINDOW', 60)  # seconds
    
    @app.before_request
    def check_rate_limit():
        """Check rate limit before processing request."""
        if request.endpoint and request.endpoint.startswith('health'):
            # Skip rate limiting for health checks
            return None
        
        client_ip = request.remote_addr
        now = time.time()
        
        # Clean old entries
        rate_limit_store[client_ip] = [
            ts for ts in rate_limit_store[client_ip]
            if now - ts < app.config['RATE_LIMIT_WINDOW']
        ]
        
        # Check limit
        if len(rate_limit_store[client_ip]) >= app.config['RATE_LIMIT_REQUESTS']:
            return jsonify({
                'error': 'Rate limit exceeded',
                'retry_after': app.config['RATE_LIMIT_WINDOW']
            }), 429
        
        # Record request
        rate_limit_store[client_ip].append(now)
        return None
    
    logger.info("Rate limiting middleware configured")


def rate_limit(max_requests: int = 100, window: int = 60):
    """
    Decorator for custom rate limiting.
    
    Args:
        max_requests: Maximum number of requests
        window: Time window in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            client_ip = request.remote_addr
            key = f"{f.__name__}:{client_ip}"
            now = time.time()
            
            # Clean old entries
            rate_limit_store[key] = [
                ts for ts in rate_limit_store[key]
                if now - ts < window
            ]
            
            # Check limit
            if len(rate_limit_store[key]) >= max_requests:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': window
                }), 429
            
            # Record request
            rate_limit_store[key].append(now)
            return f(*args, **kwargs)
        
        return decorated
    return decorator
