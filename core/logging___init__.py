"""
Logging package initialization
"""

from .logger import PlatformLogger, initialize_logger, get_platform_logger

__all__ = ['PlatformLogger', 'initialize_logger', 'get_platform_logger']
