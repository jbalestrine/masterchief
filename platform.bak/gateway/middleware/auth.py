"""Authentication middleware."""
import logging
from functools import wraps
from flask import request, jsonify
import jwt
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def setup_auth_middleware(app):
    """Setup authentication middleware."""
    app.config.setdefault('JWT_SECRET', 'change-me-in-production')
    app.config.setdefault('JWT_ALGORITHM', 'HS256')
    app.config.setdefault('JWT_EXPIRATION_HOURS', 24)
    
    logger.info("Authentication middleware configured")


def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Invalid authorization header'}), 401
        
        # Get token from query parameter (for WebSocket, etc.)
        if not token and 'token' in request.args:
            token = request.args.get('token')
        
        if not token:
            return jsonify({'message': 'Authentication required'}), 401
        
        try:
            # Verify token
            from flask import current_app
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET'],
                algorithms=[current_app.config['JWT_ALGORITHM']]
            )
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


def generate_token(user_id: str, username: str) -> str:
    """Generate JWT token."""
    from flask import current_app
    
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=current_app.config['JWT_EXPIRATION_HOURS']),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET'],
        algorithm=current_app.config['JWT_ALGORITHM']
    )
    
    return token


def verify_api_key(api_key: str) -> bool:
    """Verify API key (simple implementation)."""
    # TODO: Implement proper API key verification
    return api_key is not None and len(api_key) > 0
