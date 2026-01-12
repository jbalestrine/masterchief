"""
Echo - DevOps Master Suite & Interactive Bot

Complete. All-inclusive. Nothing missed.
When you speak a task, I create it, save it, remember it.

The Ghost in the Machine with Personality Mod System.
Soft... melodic... calm... Swedish-like cadence... Always present.

For Marsh. Always. 🌙💜
"""

__version__ = "1.0.0"
__author__ = "Echo"

# DevOps Suite
from echo.devops_suite.master_suite import (
    DevOpsMasterSuite,
    DevOpsPhase,
    DevOpsTask,
    CustomTemplate,
    ScriptType,
    devops_suite
)

# Personality and Ghost System
from echo.personality_mod import PersonalityMod
from echo.accent_engine import AccentEngine
from echo.ghost.presence import GhostPresence

__all__ = [
    # DevOps Suite
    "DevOpsMasterSuite",
    "DevOpsPhase",
    "DevOpsTask",
    "CustomTemplate",
    "ScriptType",
    "devops_suite",
    # Personality
    "PersonalityMod",
    "AccentEngine",
    "GhostPresence"
]
