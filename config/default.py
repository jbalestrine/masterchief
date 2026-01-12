"""Default configuration for MasterChief Platform."""

# Application
APP_NAME = "MasterChief DevOps Platform"
APP_VERSION = "2.0.0"
DEBUG = False
SECRET_KEY = "change-me-in-production"

# Database
DATABASE_URL = "postgresql://masterchief:changeme@localhost/masterchief"
DATABASE_POOL_SIZE = 10

# Redis
REDIS_URL = "redis://localhost:6379/0"

# WebSocket
WEBSOCKET_ASYNC_MODE = "eventlet"
WEBSOCKET_CORS_ORIGINS = "*"

# Event Bus
EVENT_BUS_BACKEND = "redis"
EVENT_BUS_CHANNEL_PREFIX = "masterchief"

# API
API_RATE_LIMIT_REQUESTS = 100
API_RATE_LIMIT_WINDOW = 60  # seconds
JWT_SECRET = "change-me-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# CORS
CORS_ORIGINS = "*"
CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]
CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

# Logging
LOG_LEVEL = "INFO"

# Cache
CACHE_DEFAULT_TTL = 300  # seconds
CACHE_MAX_LOGS = 10000
