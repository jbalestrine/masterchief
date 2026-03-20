"""
TF Wizard App module.

Provides module-level attributes consumed by main.py:
- ``__file__``  – used to locate sibling ``templates/`` and ``static/`` dirs
- ``templates.autoescape`` – Jinja2 autoescape setting
"""

from __future__ import annotations


class _TemplateConfig:
    """Lightweight config object so ``tf_wizard_app.templates.autoescape``
    resolves correctly in main.py's Jinja2 Environment constructor."""
    autoescape = True


templates = _TemplateConfig()


def main():
    """Entry point for the ``tf-wizard`` console script.

    Prints usage info directing users to the web UI.
    """
    print("TF Wizard is available at http://localhost:8888/tf_wizard")
    print("Start the MasterChief server with: python main.py")
