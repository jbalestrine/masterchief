"""CLI commands package."""

from .scripts import script
from .dashboard import dashboard
from .health import health
from .code import code

__all__ = ["script", "dashboard", "health", "code"]
