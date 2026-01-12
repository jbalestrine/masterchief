"""
AI Assistant for MasterChief IRC Bot
Provides intelligent plugin setup guidance
"""

from .assistant import AIAssistant
from .validators import AssistantValidators
from .suggestions import DefaultSuggestions
from .knowledge_base import PluginKnowledgeBase
from .handlers import PluginCommandHandlers

__all__ = [
    'AIAssistant',
    'AssistantValidators',
    'DefaultSuggestions',
    'PluginKnowledgeBase',
    'PluginCommandHandlers',
]
