"""
Package Manager Hub - Unified package management
"""

import subprocess
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class PackageManager:
    """Unified package management across multiple package managers"""
    
    SUPPORTED_MANAGERS = ['apt', 'pip', 'npm', 'docker']
    
    def search(self, query: str, manager: str = 'all') -> List[Dict[str, Any]]:
        """Search for packages"""
        results = []
        
        managers = self.SUPPORTED_MANAGERS if manager == 'all' else [manager]
        
        for mgr in managers:
            if mgr == 'apt':
                results.extend(self._search_apt(query))
            elif mgr == 'pip':
                results.extend(self._search_pip(query))
            elif mgr == 'npm':
                results.extend(self._search_npm(query))
        
        return results
    
    def list_installed(self, manager: str = 'all') -> List[Dict[str, Any]]:
        """List installed packages"""
        packages = []
        
        managers = self.SUPPORTED_MANAGERS if manager == 'all' else [manager]
        
        for mgr in managers:
            if mgr == 'apt':
                packages.extend(self._list_apt())
            elif mgr == 'pip':
                packages.extend(self._list_pip())
            elif mgr == 'npm':
                packages.extend(self._list_npm())
        
        return packages
    
    def install(self, package: str, manager: str = 'apt') -> bool:
        """Install a package"""
        try:
            if manager == 'apt':
                subprocess.run(['apt-get', 'install', '-y', package], check=True)
            elif manager == 'pip':
                subprocess.run(['pip3', 'install', package], check=True)
            elif manager == 'npm':
                subprocess.run(['npm', 'install', '-g', package], check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to install {package} with {manager}: {e}")
            return False
    
    def remove(self, package: str, manager: str = 'apt') -> bool:
        """Remove a package"""
        try:
            if manager == 'apt':
                subprocess.run(['apt-get', 'remove', '-y', package], check=True)
            elif manager == 'pip':
                subprocess.run(['pip3', 'uninstall', '-y', package], check=True)
            elif manager == 'npm':
                subprocess.run(['npm', 'uninstall', '-g', package], check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to remove {package} with {manager}: {e}")
            return False
    
    def update_all(self, manager: str = 'apt') -> bool:
        """Update all packages"""
        try:
            if manager == 'apt':
                subprocess.run(['apt-get', 'update'], check=True)
                subprocess.run(['apt-get', 'upgrade', '-y'], check=True)
            elif manager == 'pip':
                subprocess.run(['pip3', 'list', '--outdated'], check=True)
            elif manager == 'npm':
                subprocess.run(['npm', 'update', '-g'], check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to update packages with {manager}: {e}")
            return False
    
    def _search_apt(self, query: str) -> List[Dict[str, Any]]:
        """Search APT packages"""
        packages = []
        try:
            result = subprocess.run(
                ['apt-cache', 'search', query],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.split('\n'):
                if ' - ' in line:
                    name, desc = line.split(' - ', 1)
                    packages.append({
                        'name': name.strip(),
                        'description': desc.strip(),
                        'manager': 'apt'
                    })
        except Exception as e:
            logger.error(f"APT search failed: {e}")
        return packages
    
    def _list_apt(self) -> List[Dict[str, Any]]:
        """List installed APT packages"""
        packages = []
        try:
            result = subprocess.run(
                ['dpkg', '-l'],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.split('\n'):
                if line.startswith('ii'):
                    parts = line.split()
                    if len(parts) >= 3:
                        packages.append({
                            'name': parts[1],
                            'version': parts[2],
                            'manager': 'apt'
                        })
        except Exception as e:
            logger.error(f"Failed to list APT packages: {e}")
        return packages
    
    def _search_pip(self, query: str) -> List[Dict[str, Any]]:
        """Search pip packages"""
        # Simplified - would use PyPI API in production
        return []
    
    def _list_pip(self) -> List[Dict[str, Any]]:
        """List installed pip packages"""
        packages = []
        try:
            result = subprocess.run(
                ['pip3', 'list', '--format=json'],
                capture_output=True,
                text=True,
                check=True
            )
            import json
            for pkg in json.loads(result.stdout):
                packages.append({
                    'name': pkg['name'],
                    'version': pkg['version'],
                    'manager': 'pip'
                })
        except Exception as e:
            logger.error(f"Failed to list pip packages: {e}")
        return packages
    
    def _search_npm(self, query: str) -> List[Dict[str, Any]]:
        """Search npm packages"""
        # Simplified - would use npm registry API in production
        return []
    
    def _list_npm(self) -> List[Dict[str, Any]]:
        """List installed npm packages"""
        packages = []
        try:
            result = subprocess.run(
                ['npm', 'list', '-g', '--json', '--depth=0'],
                capture_output=True,
                text=True,
                check=True
            )
            import json
            data = json.loads(result.stdout)
            for name, info in data.get('dependencies', {}).items():
                packages.append({
                    'name': name,
                    'version': info.get('version', ''),
                    'manager': 'npm'
                })
        except Exception as e:
            logger.error(f"Failed to list npm packages: {e}")
        return packages
