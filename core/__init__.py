"""
MasterChief - Modular DevOps Automation Platform
Core package initialization
"""

__version__ = "1.0.0"
__author__ = "Balestrine DevOps"

# Note: module-loader uses hyphen in directory name for convention,
# but Python imports use the full path
from core.config.manager import ConfigManager
from core.logging.logger import PlatformLogger
from core.api.interface import ModuleAPI

__all__ = ['ConfigManager', 'PlatformLogger', 'ModuleAPI']
