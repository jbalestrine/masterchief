"""
Network Management Module
"""

import subprocess
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class NetworkManager:
    """Manage network interfaces and configuration"""
    
    def list_interfaces(self) -> List[Dict[str, Any]]:
        """List network interfaces"""
        try:
            result = subprocess.run(
                ['ip', '-j', 'addr'],
                capture_output=True,
                text=True,
                check=True
            )
            import json
            return json.loads(result.stdout)
        except Exception as e:
            logger.error(f"Failed to list interfaces: {e}")
            return []
    
    def get_routes(self) -> List[Dict[str, Any]]:
        """Get routing table"""
        try:
            result = subprocess.run(
                ['ip', '-j', 'route'],
                capture_output=True,
                text=True,
                check=True
            )
            import json
            return json.loads(result.stdout)
        except Exception as e:
            logger.error(f"Failed to get routes: {e}")
            return []
