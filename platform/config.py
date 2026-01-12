"""
Smart configuration - automatically detects environment.
ZERO configuration needed for development.
"""
import os
from pathlib import Path


class Config:
    """Configuration that just works everywhere."""
    
    # Auto-detect environment
    ENV = os.environ.get('MASTERCHIEF_ENV', 'local')
    IS_AZURE = bool(os.environ.get('WEBSITE_SITE_NAME'))
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / 'data'
    LOGS_DIR = BASE_DIR / 'logs'
    PLUGINS_DIR = BASE_DIR / 'plugins'
    SCRIPTS_DIR = DATA_DIR / 'custom_scripts'
    BACKUPS_DIR = BASE_DIR / 'backups'
    
    # Database - SQLite by default
    @property
    def DATABASE_URL(self):
        return os.environ.get(
            'DATABASE_URL', 
            f"sqlite:///{self.DATA_DIR}/masterchief.db"
        )
    
    # Redis - optional
    REDIS_URL = os.environ.get('REDIS_URL')
    REDIS_ENABLED = os.environ.get('REDIS_ENABLED', 'false').lower() == 'true'
    
    # Server
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 8080))
    DEBUG = os.environ.get('DEBUG', 'true').lower() == 'true'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
    
    # IRC Bot
    IRC_ENABLED = os.environ.get('IRC_ENABLED', 'false').lower() == 'true'
    IRC_SERVER = os.environ.get('IRC_SERVER', 'localhost')
    IRC_PORT = int(os.environ.get('IRC_PORT', 6667))
    IRC_NICKNAME = os.environ.get('IRC_NICKNAME', 'masterchief')
    IRC_CHANNELS = os.environ.get('IRC_CHANNELS', '#devops').split(',')
    
    def __init__(self):
        """Ensure required directories exist."""
        for directory in [self.DATA_DIR, self.LOGS_DIR, self.PLUGINS_DIR, 
                         self.SCRIPTS_DIR, self.BACKUPS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


# Global config instance
config = Config()
