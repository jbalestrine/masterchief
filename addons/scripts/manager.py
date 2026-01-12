"""
Custom Script Manager
Upload, manage, and execute custom scripts
"""

import os
import subprocess
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import hashlib
import time

logger = logging.getLogger(__name__)

class ScriptManager:
    """Manage custom scripts"""
    
    def __init__(self):
        self.scripts_dir = Path("/var/lib/masterchief/scripts")
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
    
    def list_scripts(self) -> List[Dict[str, Any]]:
        """List all uploaded scripts"""
        scripts = []
        for script_file in self.scripts_dir.glob("*.sh"):
            scripts.append({
                'name': script_file.name,
                'path': str(script_file),
                'size': script_file.stat().st_size,
                'modified': script_file.stat().st_mtime,
                'executable': os.access(script_file, os.X_OK)
            })
        return scripts
    
    def upload_script(self, name: str, content: str) -> bool:
        """Upload a new script"""
        try:
            script_path = self.scripts_dir / name
            with open(script_path, 'w') as f:
                f.write(content)
            
            # Make executable
            os.chmod(script_path, 0o755)
            
            logger.info(f"Script uploaded: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload script {name}: {e}")
            return False
    
    def execute_script(self, name: str, args: List[str] = None) -> Dict[str, Any]:
        """Execute a script"""
        try:
            script_path = self.scripts_dir / name
            if not script_path.exists():
                return {
                    'success': False,
                    'error': 'Script not found'
                }
            
            cmd = [str(script_path)]
            if args:
                cmd.extend(args)
            
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            execution_time = time.time() - start_time
            
            return {
                'success': result.returncode == 0,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'execution_time': execution_time
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Script execution timed out'
            }
        except Exception as e:
            logger.error(f"Failed to execute script {name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_script(self, name: str) -> bool:
        """Delete a script"""
        try:
            script_path = self.scripts_dir / name
            if script_path.exists():
                script_path.unlink()
                logger.info(f"Script deleted: {name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete script {name}: {e}")
            return False
    
    def get_script_content(self, name: str) -> Optional[str]:
        """Get script content"""
        try:
            script_path = self.scripts_dir / name
            if script_path.exists():
                with open(script_path, 'r') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Failed to read script {name}: {e}")
        return None
