"""
Service Manager - Control and monitor system services
"""

import subprocess
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"
    UNKNOWN = "unknown"

@dataclass
class Service:
    name: str
    status: ServiceStatus
    enabled: bool
    description: str = ""
    pid: Optional[int] = None
    uptime: Optional[str] = None

class ServiceManager:
    """Manage system services using systemd"""
    
    def list_services(self) -> List[Service]:
        """List all services"""
        services = []
        try:
            result = subprocess.run(
                ['systemctl', 'list-units', '--type=service', '--all', '--no-pager'],
                capture_output=True,
                text=True,
                check=True
            )
            
            for line in result.stdout.split('\n')[1:]:
                if not line.strip() or line.startswith('UNIT'):
                    continue
                parts = line.split()
                if len(parts) >= 4:
                    name = parts[0].replace('.service', '')
                    status = self._parse_status(parts[2])
                    enabled = self._is_enabled(name)
                    services.append(Service(
                        name=name,
                        status=status,
                        enabled=enabled
                    ))
        except Exception as e:
            logger.error(f"Failed to list services: {e}")
        
        return services
    
    def get_status(self, service: str) -> Optional[Service]:
        """Get status of a specific service"""
        try:
            result = subprocess.run(
                ['systemctl', 'status', service],
                capture_output=True,
                text=True
            )
            
            status = ServiceStatus.UNKNOWN
            if 'Active: active (running)' in result.stdout:
                status = ServiceStatus.RUNNING
            elif 'Active: inactive' in result.stdout:
                status = ServiceStatus.STOPPED
            elif 'Active: failed' in result.stdout:
                status = ServiceStatus.FAILED
            
            enabled = self._is_enabled(service)
            
            return Service(
                name=service,
                status=status,
                enabled=enabled,
                description=self._get_description(service)
            )
        except Exception as e:
            logger.error(f"Failed to get status for {service}: {e}")
            return None
    
    def start(self, service: str) -> bool:
        """Start a service"""
        return self._run_systemctl('start', service)
    
    def stop(self, service: str) -> bool:
        """Stop a service"""
        return self._run_systemctl('stop', service)
    
    def restart(self, service: str) -> bool:
        """Restart a service"""
        return self._run_systemctl('restart', service)
    
    def enable(self, service: str) -> bool:
        """Enable a service to start on boot"""
        return self._run_systemctl('enable', service)
    
    def disable(self, service: str) -> bool:
        """Disable a service from starting on boot"""
        return self._run_systemctl('disable', service)
    
    def get_logs(self, service: str, lines: int = 100) -> List[str]:
        """Get logs for a service"""
        try:
            result = subprocess.run(
                ['journalctl', '-u', service, '-n', str(lines), '--no-pager'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.split('\n')
        except Exception as e:
            logger.error(f"Failed to get logs for {service}: {e}")
            return []
    
    def _run_systemctl(self, action: str, service: str) -> bool:
        """Run a systemctl command"""
        try:
            subprocess.run(
                ['systemctl', action, service],
                check=True,
                capture_output=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to {action} {service}: {e}")
            return False
    
    def _is_enabled(self, service: str) -> bool:
        """Check if a service is enabled"""
        try:
            result = subprocess.run(
                ['systemctl', 'is-enabled', service],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _get_description(self, service: str) -> str:
        """Get service description"""
        try:
            result = subprocess.run(
                ['systemctl', 'show', service, '--property=Description', '--no-pager'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.split('=', 1)[1].strip()
        except:
            pass
        return ""
    
    def _parse_status(self, status_str: str) -> ServiceStatus:
        """Parse status string to ServiceStatus enum"""
        status_str = status_str.lower()
        if 'running' in status_str:
            return ServiceStatus.RUNNING
        elif 'failed' in status_str:
            return ServiceStatus.FAILED
        elif 'stopped' in status_str or 'inactive' in status_str:
            return ServiceStatus.STOPPED
        else:
            return ServiceStatus.UNKNOWN
