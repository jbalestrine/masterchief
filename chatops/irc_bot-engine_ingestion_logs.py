"""Log ingestion for IRC bot."""
import asyncio
import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

from .base import BaseIngestion, IngestionEvent, IngestionStatus

logger = logging.getLogger(__name__)


class LogIngestion(BaseIngestion):
    """Log file tailing and parsing ingestion."""
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        """
        Initialize log ingestion.
        
        Config options:
            - path: Path to log file
            - format: Log format (syslog, json, custom)
            - pattern: Regex pattern for custom format
            - follow: Follow file (tail -f style) (default: True)
            - from_beginning: Start from beginning of file (default: False)
            - rotation_check_interval: Check for rotation (default: 5)
        """
        super().__init__(source_id, config)
        self.path = Path(config.get('path'))
        self.format = config.get('format', 'generic')
        self.pattern = config.get('pattern')
        self.follow = config.get('follow', True)
        self.from_beginning = config.get('from_beginning', False)
        self.rotation_check_interval = config.get('rotation_check_interval', 5)
        self._task = None
        self._file = None
        self._inode = None
        self._position = 0
    
    def _parse_syslog(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse syslog format line."""
        # RFC 3164 syslog format
        # <priority>timestamp hostname tag: message
        pattern = r'<(\d+)>(\w+\s+\d+\s+\d+:\d+:\d+)\s+(\S+)\s+([^:]+):\s*(.*)'
        match = re.match(pattern, line)
        
        if match:
            priority, timestamp, hostname, tag, message = match.groups()
            return {
                'priority': int(priority),
                'timestamp': timestamp,
                'hostname': hostname,
                'tag': tag,
                'message': message
            }
        
        # Try simpler format without priority
        pattern = r'(\w+\s+\d+\s+\d+:\d+:\d+)\s+(\S+)\s+([^:]+):\s*(.*)'
        match = re.match(pattern, line)
        
        if match:
            timestamp, hostname, tag, message = match.groups()
            return {
                'timestamp': timestamp,
                'hostname': hostname,
                'tag': tag,
                'message': message
            }
        
        return None
    
    def _parse_json(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse JSON format line."""
        try:
            import json
            return json.loads(line)
        except json.JSONDecodeError:
            return None
    
    def _parse_custom(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse custom format line using regex pattern."""
        if not self.pattern:
            return {'message': line}
        
        match = re.match(self.pattern, line)
        if match:
            return match.groupdict()
        
        return None
    
    def _parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a log line based on format."""
        if not line or not line.strip():
            return None
        
        if self.format == 'syslog':
            return self._parse_syslog(line)
        elif self.format == 'json':
            return self._parse_json(line)
        elif self.format == 'custom':
            return self._parse_custom(line)
        else:
            # Generic format
            return {'message': line.strip()}
    
    async def _check_rotation(self) -> bool:
        """Check if log file has been rotated."""
        try:
            stat = self.path.stat()
            current_inode = stat.st_ino
            
            if self._inode is not None and current_inode != self._inode:
                logger.info(f"Log rotation detected for {self.path}")
                return True
            
            self._inode = current_inode
            return False
        except FileNotFoundError:
            return True
    
    async def _reopen_file(self):
        """Reopen log file (handles rotation)."""
        if self._file:
            self._file.close()
        
        try:
            self._file = open(self.path, 'r')
            stat = self.path.stat()
            self._inode = stat.st_ino
            
            if not self.from_beginning and self._position == 0:
                # Start at end of file
                self._file.seek(0, 2)
            elif self._position > 0:
                # Resume from last position
                self._file.seek(self._position)
            
            logger.info(f"Opened log file: {self.path}")
        except Exception as e:
            logger.error(f"Failed to open log file {self.path}: {e}")
            raise
    
    async def _tail_loop(self):
        """Main log tailing loop."""
        last_rotation_check = time.time()
        
        while self.status == IngestionStatus.RUNNING:
            try:
                # Check for rotation periodically
                if time.time() - last_rotation_check >= self.rotation_check_interval:
                    if await self._check_rotation():
                        await self._reopen_file()
                    last_rotation_check = time.time()
                
                # Read lines
                line = self._file.readline()
                
                if line:
                    # Update position
                    self._position = self._file.tell()
                    
                    # Parse and dispatch
                    parsed = self._parse_line(line)
                    if parsed:
                        event = IngestionEvent(
                            source_type="log",
                            source_id=self.source_id,
                            data=parsed,
                            metadata={
                                'filepath': str(self.path),
                                'format': self.format,
                                'position': self._position,
                                'raw_line': line.strip()
                            },
                            timestamp=time.time()
                        )
                        
                        await self._dispatch_event(event)
                else:
                    # No data available
                    if self.follow:
                        # Wait a bit before checking again
                        await asyncio.sleep(0.1)
                    else:
                        # Not following, we're done
                        break
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in tail loop: {e}")
                await asyncio.sleep(1)
    
    async def start(self):
        """Start log tailing."""
        self.status = IngestionStatus.STARTING
        try:
            await self._reopen_file()
            self.status = IngestionStatus.RUNNING
            self._task = asyncio.create_task(self._tail_loop())
            logger.info(f"Log tailing started for {self.path}")
        except Exception as e:
            self.status = IngestionStatus.ERROR
            logger.error(f"Failed to start log tailing: {e}")
            raise
    
    async def stop(self):
        """Stop log tailing."""
        self.status = IngestionStatus.STOPPED
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        if self._file:
            self._file.close()
        
        logger.info(f"Log tailing stopped")
