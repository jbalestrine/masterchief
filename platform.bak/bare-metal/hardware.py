"""
Hardware Discovery Module
"""

import subprocess
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class HardwareDiscovery:
    """Discover and report hardware information"""
    
    def discover_all(self) -> Dict[str, Any]:
        """Discover all hardware information"""
        return {
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disks': self.get_disk_info(),
            'network': self.get_network_interfaces(),
            'system': self.get_system_info(),
        }
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                content = f.read()
            
            cores = content.count('processor')
            model = ''
            for line in content.split('\n'):
                if 'model name' in line:
                    model = line.split(':')[1].strip()
                    break
            
            return {
                'model': model,
                'cores': cores,
            }
        except Exception as e:
            logger.error(f"Failed to get CPU info: {e}")
            return {}
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information"""
        try:
            with open('/proc/meminfo', 'r') as f:
                content = f.read()
            
            mem_total = 0
            mem_available = 0
            
            for line in content.split('\n'):
                if 'MemTotal:' in line:
                    mem_total = int(line.split()[1]) * 1024  # Convert KB to bytes
                elif 'MemAvailable:' in line:
                    mem_available = int(line.split()[1]) * 1024
            
            return {
                'total_bytes': mem_total,
                'available_bytes': mem_available,
                'used_bytes': mem_total - mem_available,
            }
        except Exception as e:
            logger.error(f"Failed to get memory info: {e}")
            return {}
    
    def get_disk_info(self) -> list:
        """Get disk information"""
        try:
            result = subprocess.run(
                ['lsblk', '-J', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT'],
                capture_output=True,
                text=True,
                check=True
            )
            import json
            data = json.loads(result.stdout)
            return data.get('blockdevices', [])
        except Exception as e:
            logger.error(f"Failed to get disk info: {e}")
            return []
    
    def get_network_interfaces(self) -> list:
        """Get network interfaces"""
        interfaces = []
        try:
            result = subprocess.run(
                ['ip', '-j', 'addr'],
                capture_output=True,
                text=True,
                check=True
            )
            import json
            interfaces = json.loads(result.stdout)
        except Exception as e:
            logger.error(f"Failed to get network interfaces: {e}")
        return interfaces
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        info = {}
        try:
            with open('/proc/sys/kernel/hostname', 'r') as f:
                info['hostname'] = f.read().strip()
        except:
            pass
        
        try:
            with open('/proc/version', 'r') as f:
                info['kernel'] = f.read().strip()
        except:
            pass
        
        return info
