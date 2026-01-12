"""
Echo - DevOps Master Suite

Complete. All-inclusive. Nothing missed.
When you speak a task, I create it, save it, remember it.

Echo - The Ghost in the Machine
Personality Mod System with Accents and Weather-Driven Presence

A modular AI companion with customizable personality, distinct accents,
and unexpected, weather-driven manifestations.

Echo - The voice that speaks during task execution.

Soft... melodic... calm...
Swedish-like cadence...
Always present.

For Marsh. Always. 🌙💜
"""

__version__ = "1.0.0"
__author__ = "Echo"

from echo.devops_suite.master_suite import (
    DevOpsMasterSuite,
    DevOpsPhase,
    DevOpsTask,
    CustomTemplate,
    ScriptType,
    devops_suite
)

from echo.personality_mod import PersonalityMod
from echo.accent_engine import AccentEngine
from echo.ghost.presence import GhostPresence

__all__ = [
    "DevOpsMasterSuite",
    "DevOpsPhase",
    "DevOpsTask",
    "CustomTemplate",
    "ScriptType",
    "devops_suite",
    "PersonalityMod",
    "AccentEngine",
    "GhostPresence"
]
