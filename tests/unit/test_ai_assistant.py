"""
Unit tests for AI Assistant.
"""

import pytest
from chatops.irc.bot_engine.ai_assistant.assistant import AIAssistant
from chatops.irc.bot_engine.ai_assistant.validators import AssistantValidators
from chatops.irc.bot_engine.ai_assistant.suggestions import DefaultSuggestions
from chatops.irc.bot_engine.ai_assistant.knowledge_base import PluginKnowledgeBase


class TestAIAssistant:
    """Test AI assistant functionality."""
    
    @pytest.fixture
    def assistant(self):
        """Create AI assistant instance."""
        return AIAssistant()
    
    def test_validate_plugin_config(self, assistant):
        """Test plugin configuration validation."""
        config = {
            'memory_limit': '256M',
            'upload_max_filesize': '64M',
            'post_max_size': '64M'
        }
        
        result = assistant.validate_plugin_config('php', config)
        
        assert 'valid' in result
        assert 'issues' in result
        assert 'suggestions' in result
    
    def test_suggest_defaults(self, assistant):
        """Test default suggestions."""
        defaults = assistant.suggest_defaults('python')
        
        assert defaults is not None
        assert 'python_version' in defaults
        assert 'venv_enabled' in defaults
    
    def test_answer_question_php(self, assistant):
        """Test answering PHP-related question."""
        answer = assistant.answer_question('How do I fix PHP memory issues?')
        
        assert 'memory' in answer.lower()
        assert len(answer) > 0
    
    def test_answer_question_python(self, assistant):
        """Test answering Python-related question."""
        answer = assistant.answer_question('How do I set up Python virtual environment?')
        
        assert 'venv' in answer.lower() or 'virtual' in answer.lower()
        assert len(answer) > 0
    
    def test_get_setup_guide(self, assistant):
        """Test getting setup guide."""
        guide = assistant.get_setup_guide('python')
        
        assert 'plugin_type' in guide
        assert 'steps' in guide
        assert 'best_practices' in guide
        assert 'common_issues' in guide
        assert len(guide['steps']) > 0


class TestAssistantValidators:
    """Test assistant validators."""
    
    @pytest.fixture
    def validators(self):
        """Create validators instance."""
        return AssistantValidators()
    
    def test_detect_php_conflicts(self, validators):
        """Test detecting PHP conflicts."""
        config = {
            'memory_limit': '256M',
            'upload_max_filesize': '512M',  # Larger than memory limit
            'post_max_size': '64M'  # Smaller than upload max
        }
        
        conflicts = validators.detect_conflicts('php', config)
        
        assert len(conflicts) > 0
    
    def test_detect_powershell_conflicts(self, validators):
        """Test detecting PowerShell conflicts."""
        config = {
            'execution_policy': 'RemoteSigned',
            'script_signing': False
        }
        
        conflicts = validators.detect_conflicts('powershell', config)
        
        # Should detect warning about policy vs signing
        assert isinstance(conflicts, list)
    
    def test_detect_misconfigurations(self, validators):
        """Test detecting misconfigurations."""
        config = {
            'execution_policy': 'Unrestricted'  # Security risk
        }
        
        issues = validators.detect_misconfigurations('powershell', config)
        
        assert len(issues) > 0
        assert any('security' in i.get('type', '').lower() for i in issues)


class TestDefaultSuggestions:
    """Test default suggestions engine."""
    
    @pytest.fixture
    def suggestions(self):
        """Create suggestions instance."""
        return DefaultSuggestions()
    
    def test_get_php_defaults(self, suggestions):
        """Test getting PHP defaults."""
        defaults = suggestions.get_defaults('php')
        
        assert 'php_version' in defaults
        assert 'memory_limit' in defaults
        assert 'extensions' in defaults
    
    def test_get_python_defaults(self, suggestions):
        """Test getting Python defaults."""
        defaults = suggestions.get_defaults('python')
        
        assert 'python_version' in defaults
        assert 'venv_enabled' in defaults
        assert 'dependencies' in defaults
    
    def test_get_nodejs_defaults(self, suggestions):
        """Test getting Node.js defaults."""
        defaults = suggestions.get_defaults('nodejs')
        
        assert 'node_version' in defaults
        assert 'package_manager' in defaults
    
    def test_suggest_conflict_fix(self, suggestions):
        """Test suggesting fix for conflict."""
        conflict = {
            'field': 'memory_limit',
            'type': 'resource_conflict',
            'message': 'Memory limit too low'
        }
        
        fix = suggestions.suggest_conflict_fix('php', conflict)
        
        assert 'field' in fix
        assert 'suggested_value' in fix


class TestPluginKnowledgeBase:
    """Test plugin knowledge base."""
    
    @pytest.fixture
    def kb(self):
        """Create knowledge base instance."""
        return PluginKnowledgeBase()
    
    def test_get_setup_steps(self, kb):
        """Test getting setup steps."""
        steps = kb.get_setup_steps('python')
        
        assert len(steps) > 0
        assert any('virtual environment' in s.lower() for s in steps)
    
    def test_get_best_practices(self, kb):
        """Test getting best practices."""
        practices = kb.get_best_practices('python')
        
        assert len(practices) > 0
        assert any('virtual environment' in p.lower() for p in practices)
    
    def test_get_common_issues(self, kb):
        """Test getting common issues."""
        issues = kb.get_common_issues('python')
        
        assert len(issues) > 0
        assert all('issue' in i and 'solution' in i for i in issues)
    
    def test_query_php_question(self, kb):
        """Test querying PHP question."""
        answer = kb.query('How do I configure PHP memory limit?')
        
        assert len(answer) > 0
        assert 'memory' in answer.lower()
    
    def test_query_python_question(self, kb):
        """Test querying Python question."""
        answer = kb.query('How do I use Python virtual environment?')
        
        assert len(answer) > 0
        assert 'venv' in answer.lower() or 'virtual' in answer.lower()
    
    def test_get_troubleshooting_steps(self, kb):
        """Test getting troubleshooting steps."""
        steps = kb.get_troubleshooting_steps('python', 'module not found')
        
        assert len(steps) > 0
