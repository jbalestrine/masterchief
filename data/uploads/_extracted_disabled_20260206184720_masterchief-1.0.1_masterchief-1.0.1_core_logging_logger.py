"""
Platform Logger - Centralized logging system
Provides structured logging with multiple outputs and log levels
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import json


class PlatformLogger:
    """
    Centralized logging system for the MasterChief platform
    """
    
    def __init__(self, 
                 log_dir: str = "logs",
                 log_level: str = "INFO",
                 enable_console: bool = True,
                 enable_file: bool = True):
        """
        Initialize the platform logger
        
        Args:
            log_dir: Directory for log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            enable_console: Enable console output
            enable_file: Enable file output
        """
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper())
        self.enable_console = enable_console
        self.enable_file = enable_file
        
        # Create logs directory
        if self.enable_file:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup root logger
        self.setup_logger()
    
    def setup_logger(self) -> None:
        """Setup the root logger with handlers and formatters"""
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Remove existing handlers
        root_logger.handlers = []
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # File handler
        if self.enable_file:
            log_file = self.log_dir / f"masterchief_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance for a specific module
        
        Args:
            name: Logger name (typically __name__)
            
        Returns:
            Logger instance
        """
        return logging.getLogger(name)
    
    def log_module_event(self, 
                        module_name: str, 
                        event: str, 
                        details: Optional[dict] = None) -> None:
        """
        Log a module lifecycle event
        
        Args:
            module_name: Name of the module
            event: Event type (loaded, started, stopped, error)
            details: Optional event details
        """
        logger = self.get_logger(f"module.{module_name}")
        
        message = f"Module event: {event}"
        if details:
            message += f" - {json.dumps(details)}"
        
        if event == "error":
            logger.error(message)
        else:
            logger.info(message)
    
    def log_deployment_event(self,
                            environment: str,
                            module: str,
                            action: str,
                            status: str,
                            details: Optional[dict] = None) -> None:
        """
        Log a deployment event
        
        Args:
            environment: Target environment
            module: Module being deployed
            action: Deployment action (plan, apply, destroy)
            status: Status (started, completed, failed)
            details: Optional deployment details
        """
        logger = self.get_logger("deployment")
        
        message = f"[{environment}] {module} - {action}: {status}"
        if details:
            message += f" - {json.dumps(details)}"
        
        if status == "failed":
            logger.error(message)
        elif status == "completed":
            logger.info(message)
        else:
            logger.debug(message)
    
    def set_log_level(self, level: str) -> None:
        """
        Change the log level dynamically
        
        Args:
            level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_level = getattr(logging, level.upper())
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        for handler in root_logger.handlers:
            handler.setLevel(self.log_level)


# Global logger instance
_platform_logger: Optional[PlatformLogger] = None


def initialize_logger(**kwargs) -> PlatformLogger:
    """
    Initialize the global platform logger
    
    Args:
        **kwargs: Arguments to pass to PlatformLogger
        
    Returns:
        PlatformLogger instance
    """
    global _platform_logger
    _platform_logger = PlatformLogger(**kwargs)
    return _platform_logger


def get_platform_logger() -> PlatformLogger:
    """
    Get the global platform logger instance
    
    Returns:
        PlatformLogger instance
    """
    global _platform_logger
    if _platform_logger is None:
        _platform_logger = initialize_logger()
    return _platform_logger
