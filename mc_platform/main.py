"""
MasterChief DevOps Platform
Main entry point for the platform
"""

import sys
import os
import logging
from pathlib import Path

# Add platform directory to path
sys.path.insert(0, str(Path(__file__).parent))

from api import create_app
from config import load_config

def setup_logging(config):
    """Set up logging configuration"""
    log_dir = Path(config.get('platform', {}).get('log_dir', '/var/log/masterchief'))
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'masterchief.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main entry point"""
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config = load_config()
        setup_logging(config)
        
        logger.info("Starting MasterChief Platform v1.0.0")
        
        # Create and run Flask app
        app = create_app(config)
        
        api_config = config.get('api', {})
        host = api_config.get('host', '0.0.0.0')
        port = api_config.get('port', 8443)
        ssl_enabled = api_config.get('ssl', False)
        
        if ssl_enabled:
            # Use self-signed cert for now
            ssl_context = 'adhoc'
            logger.info(f"Starting HTTPS server on {host}:{port}")
        else:
            ssl_context = None
            logger.info(f"Starting HTTP server on {host}:{port}")
        
        app.run(
            host=host,
            port=port,
            ssl_context=ssl_context,
            debug=False
        )
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
