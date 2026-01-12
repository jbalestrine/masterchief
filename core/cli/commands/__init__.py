"""CLI commands package."""

from .scripts import script
from .dashboard import dashboard
from .health import health

__all__ = ["script", "dashboard", "health"]
