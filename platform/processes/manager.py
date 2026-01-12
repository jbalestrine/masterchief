"""
Process Manager Module
"""

import psutil
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ProcessManager:
    """Manage and monitor system processes"""
    
    def list_processes(self, sort_by: str = 'cpu') -> List[Dict[str, Any]]:
        """List all processes with resource usage"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'user': pinfo['username'],
                    'cpu_percent': pinfo['cpu_percent'],
                    'memory_percent': pinfo['memory_percent'],
                    'status': pinfo['status'],
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by specified field
        if sort_by == 'cpu':
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        elif sort_by == 'memory':
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
        
        return processes
    
    def get_process(self, pid: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a process"""
        try:
            proc = psutil.Process(pid)
            return {
                'pid': proc.pid,
                'name': proc.name(),
                'user': proc.username(),
                'status': proc.status(),
                'cpu_percent': proc.cpu_percent(interval=0.1),
                'memory_percent': proc.memory_percent(),
                'create_time': proc.create_time(),
                'cmdline': proc.cmdline(),
                'cwd': proc.cwd(),
                'num_threads': proc.num_threads(),
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Failed to get process {pid}: {e}")
            return None
    
    def kill_process(self, pid: int, signal: str = 'TERM') -> bool:
        """Kill a process"""
        try:
            proc = psutil.Process(pid)
            if signal == 'KILL':
                proc.kill()
            else:
                proc.terminate()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Failed to kill process {pid}: {e}")
            return False
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system resource statistics"""
        return {
            'cpu': {
                'percent': psutil.cpu_percent(interval=1),
                'count': psutil.cpu_count(),
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent,
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'percent': psutil.disk_usage('/').percent,
            },
        }
