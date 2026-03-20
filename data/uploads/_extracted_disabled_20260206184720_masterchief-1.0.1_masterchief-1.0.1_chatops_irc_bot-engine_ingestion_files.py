"""File-based ingestion for IRC bot."""
import asyncio
import csv
import json
import logging
import os
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from .base import BaseIngestion, IngestionEvent, IngestionStatus

logger = logging.getLogger(__name__)


class FileChangeHandler(FileSystemEventHandler):
    """Handler for file system events."""
    
    def __init__(self, ingestion):
        self.ingestion = ingestion
    
    def on_created(self, event: FileSystemEvent):
        """Handle file creation."""
        if not event.is_directory:
            asyncio.create_task(self.ingestion._handle_file_event('created', event.src_path))
    
    def on_modified(self, event: FileSystemEvent):
        """Handle file modification."""
        if not event.is_directory:
            asyncio.create_task(self.ingestion._handle_file_event('modified', event.src_path))


class FileIngestion(BaseIngestion):
    """File-based ingestion with format support."""
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        """
        Initialize file ingestion.
        
        Config options:
            - path: Directory or file path to watch
            - pattern: Glob pattern for files (e.g., "*.json")
            - formats: List of supported formats (csv, json, yaml, xml)
            - recursive: Watch subdirectories (default: False)
            - initial_scan: Process existing files on start (default: True)
        """
        super().__init__(source_id, config)
        self.path = Path(config.get('path', '.'))
        self.pattern = config.get('pattern', '*')
        self.formats = config.get('formats', ['json', 'yaml', 'csv', 'xml'])
        self.recursive = config.get('recursive', False)
        self.initial_scan = config.get('initial_scan', True)
        self.observer = None
        self._processed_files = set()
    
    def _match_pattern(self, filepath: str) -> bool:
        """Check if file matches pattern."""
        from fnmatch import fnmatch
        return fnmatch(os.path.basename(filepath), self.pattern)
    
    def _parse_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Parse file based on extension."""
        try:
            path = Path(filepath)
            ext = path.suffix.lower().lstrip('.')
            
            if ext not in self.formats:
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                if ext == 'json':
                    return json.load(f)
                
                elif ext in ['yaml', 'yml']:
                    return yaml.safe_load(f)
                
                elif ext == 'csv':
                    reader = csv.DictReader(f)
                    return {'rows': list(reader)}
                
                elif ext == 'xml':
                    tree = ET.parse(f)
                    root = tree.getroot()
                    return self._xml_to_dict(root)
            
            return None
        
        except Exception as e:
            logger.error(f"Error parsing file {filepath}: {e}")
            return None
    
    def _xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """Convert XML element to dictionary."""
        result = {}
        
        # Add attributes
        if element.attrib:
            result['@attributes'] = element.attrib
        
        # Add text content
        if element.text and element.text.strip():
            result['@text'] = element.text.strip()
        
        # Add children
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                # Multiple children with same tag
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result
    
    async def _handle_file_event(self, event_type: str, filepath: str):
        """Handle a file event."""
        try:
            # Check if file matches pattern
            if not self._match_pattern(filepath):
                return
            
            # Check if already processed (for initial scan)
            file_key = f"{filepath}:{os.path.getmtime(filepath)}"
            if file_key in self._processed_files:
                return
            
            self._processed_files.add(file_key)
            
            # Parse file
            data = self._parse_file(filepath)
            if data is None:
                return
            
            # Create event
            event = IngestionEvent(
                source_type="file",
                source_id=self.source_id,
                data=data,
                metadata={
                    'filepath': filepath,
                    'filename': os.path.basename(filepath),
                    'event_type': event_type,
                    'size': os.path.getsize(filepath),
                    'mtime': os.path.getmtime(filepath)
                },
                timestamp=time.time()
            )
            
            await self._dispatch_event(event)
            
        except Exception as e:
            logger.error(f"Error handling file event for {filepath}: {e}")
    
    async def _initial_scan(self):
        """Scan for existing files."""
        try:
            if self.path.is_file():
                await self._handle_file_event('initial', str(self.path))
            elif self.path.is_dir():
                pattern_func = self.path.rglob if self.recursive else self.path.glob
                for filepath in pattern_func(self.pattern):
                    if filepath.is_file():
                        await self._handle_file_event('initial', str(filepath))
        except Exception as e:
            logger.error(f"Error during initial scan: {e}")
    
    async def start(self):
        """Start file watching."""
        self.status = IngestionStatus.STARTING
        try:
            # Initial scan if configured
            if self.initial_scan:
                await self._initial_scan()
            
            # Start watching
            if self.path.is_dir():
                self.observer = Observer()
                handler = FileChangeHandler(self)
                self.observer.schedule(handler, str(self.path), recursive=self.recursive)
                self.observer.start()
            
            self.status = IngestionStatus.RUNNING
            logger.info(f"File watching started for {self.path}")
        except Exception as e:
            self.status = IngestionStatus.ERROR
            logger.error(f"Failed to start file watching: {e}")
            raise
    
    async def stop(self):
        """Stop file watching."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        self.status = IngestionStatus.STOPPED
        logger.info(f"File watching stopped")
