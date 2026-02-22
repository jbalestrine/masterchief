"""Voice automation submodules."""

from .voice_automation import VoiceAutomation, VoiceAutomationConfig
from .wake_word import WakeWordDetector
from .command_processor import CommandProcessor, Intent
from .conversation import ConversationManager, ConversationContext
from .action_executor import ActionExecutor, ActionResult
from .response_builder import ResponseBuilder
from .feedback import AudioFeedback

__all__ = [
    "VoiceAutomation",
    "VoiceAutomationConfig",
    "WakeWordDetector",
    "CommandProcessor",
    "Intent",
    "ConversationManager",
    "ConversationContext",
    "ActionExecutor",
    "ActionResult",
    "ResponseBuilder",
    "AudioFeedback",
]
