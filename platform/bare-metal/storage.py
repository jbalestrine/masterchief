"""
Storage Management Module
"""

import subprocess
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class StorageManager:
    """Manage disks, partitions, and filesystems"""
    
    def list_disks(self) -> List[Dict[str, Any]]:
        """List all disks and partitions"""
        try:
            result = subprocess.run(
                ['lsblk', '-J', '-o', 'NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,UUID'],
                capture_output=True,
                text=True,
                check=True
            )
            import json
            data = json.loads(result.stdout)
            return data.get('blockdevices', [])
        except Exception as e:
            logger.error(f"Failed to list disks: {e}")
            return []
    
    def get_disk_usage(self) -> List[Dict[str, Any]]:
        """Get disk space usage"""
        try:
            result = subprocess.run(
                ['df', '-h'],
                capture_output=True,
                text=True,
                check=True
            )
            
            filesystems = []
            for line in result.stdout.split('\n')[1:]:
                if not line.strip():
                    continue
                parts = line.split()
                if len(parts) >= 6:
                    filesystems.append({
                        'filesystem': parts[0],
                        'size': parts[1],
                        'used': parts[2],
                        'available': parts[3],
                        'use_percent': parts[4],
                        'mounted_on': parts[5]
                    })
            return filesystems
        except Exception as e:
            logger.error(f"Failed to get disk usage: {e}")
            return []
