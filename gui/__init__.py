"""
Minimal `gui` shim for local development to satisfy addons that import `gui.launch_gui`.
This is a temporary no-op implementation so the server can start during dev/testing.
"""

__all__ = ["launch_gui"]

def launch_gui(*args, **kwargs):
    """No-op launcher used by addon code during local development."""
    return None
