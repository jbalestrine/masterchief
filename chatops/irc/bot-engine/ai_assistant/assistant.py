"""
Core AI Assistant logic for plugin guidance.
"""

import logging
from typing import Dict, Any, List, Optional

from .validators import AssistantValidators
from .suggestions import DefaultSuggestions
from .knowledge_base import PluginKnowledgeBase

logger = logging.getLogger(__name__)


class AIAssistant:
    """AI-powered assistant for plugin configuration and troubleshooting."""
    
    def __init__(self):
        """Initialize AI assistant."""
        self.validators = AssistantValidators()
        self.suggestions = DefaultSuggestions()
        self.knowledge_base = PluginKnowledgeBase()
        logger.info("AI Assistant initialized")
    
    def validate_plugin_config(
        self,
        plugin_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate plugin configuration and detect issues.
        
        Args:
            plugin_type: Type of plugin
            config: Configuration to validate
            
        Returns:
            Validation result with issues and suggestions
        """
        issues = []
        suggestions = []
        
        # Check for conflicts
        conflicts = self.validators.detect_conflicts(plugin_type, config)
        if conflicts:
            issues.extend(conflicts)
            
            # Get suggestions for conflicts
            for conflict in conflicts:
                fix = self.suggestions.suggest_conflict_fix(plugin_type, conflict)
                if fix:
                    suggestions.append(fix)
        
        # Check for misconfigurations
        misconfigs = self.validators.detect_misconfigurations(plugin_type, config)
        if misconfigs:
            issues.extend(misconfigs)
            
            # Get suggestions for misconfigurations
            for misconfig in misconfigs:
                fix = self.suggestions.suggest_config_fix(plugin_type, misconfig)
                if fix:
                    suggestions.append(fix)
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'suggestions': suggestions
        }
    
    def suggest_defaults(self, plugin_type: str) -> Dict[str, Any]:
        """
        Suggest sensible default configuration for a plugin type.
        
        Args:
            plugin_type: Type of plugin
            
        Returns:
            Suggested configuration
        """
        return self.suggestions.get_defaults(plugin_type)
    
    def check_permissions(self, plugin_path: str) -> Dict[str, Any]:
        """
        Check folder permissions for plugin.
        
        Args:
            plugin_path: Path to plugin directory
            
        Returns:
            Permission check result
        """
        return self.validators.check_folder_permissions(plugin_path)
    
    def answer_question(self, question: str) -> str:
        """
        Answer a plugin configuration question.
        
        Args:
            question: User question
            
        Returns:
            Answer or guidance
        """
        return self.knowledge_base.query(question)
    
    def troubleshoot(
        self,
        plugin_type: str,
        issue_description: str
    ) -> List[str]:
        """
        Provide troubleshooting steps for a plugin issue.
        
        Args:
            plugin_type: Type of plugin
            issue_description: Description of the issue
            
        Returns:
            List of troubleshooting steps
        """
        return self.knowledge_base.get_troubleshooting_steps(
            plugin_type,
            issue_description
        )
    
    def get_setup_guide(self, plugin_type: str) -> Dict[str, Any]:
        """
        Get setup guide for a plugin type.
        
        Args:
            plugin_type: Type of plugin
            
        Returns:
            Setup guide with steps and recommendations
        """
        return {
            'plugin_type': plugin_type,
            'steps': self.knowledge_base.get_setup_steps(plugin_type),
            'best_practices': self.knowledge_base.get_best_practices(plugin_type),
            'common_issues': self.knowledge_base.get_common_issues(plugin_type)
        }
