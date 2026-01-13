"""
Echo - DevOps Suite with Chat Bot Capabilities

Complete DevOps automation suite with:
- DevOps Master Suite for script generation
- Personality and voice system
- Live chat bot with training capabilities

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

# DevOps Suite exports (optional)
try:
    from echo.devops_suite.master_suite import (
        DevOpsMasterSuite,
        DevOpsPhase,
        DevOpsTask,
        CustomTemplate,
        ScriptType,
        devops_suite
    )
except ImportError:
    # DevOps suite may not be fully available
    DevOpsMasterSuite = None
    DevOpsPhase = None
    DevOpsTask = None
    CustomTemplate = None
    ScriptType = None
    devops_suite = None

# Personality system exports (optional)
try:
    from echo.personality_mod import PersonalityMod
    from echo.accent_engine import AccentEngine
    from echo.ghost.presence import GhostPresence
except ImportError:
    # These may not be available in all configurations
    PersonalityMod = None
    AccentEngine = None
    GhostPresence = None

# Chat bot exports (always available)
from echo.chat_bot import (
    EchoChatBot,
    TrainingDataStore,
    ResponseQuality,
    ChatMessage,
    TrainingExample,
    get_chat_bot
)

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
    # Personality system
    "PersonalityMod",
    "AccentEngine",
    "GhostPresence",
    # Chat bot
    "EchoChatBot",
    "TrainingDataStore",
    "ResponseQuality",
    "ChatMessage",
    "TrainingExample",
    "get_chat_bot"
]

