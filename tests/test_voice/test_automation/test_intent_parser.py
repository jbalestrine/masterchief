"""Test intent parser."""

import pytest
from chatops.irc.bot_engine.voice.automation.intent_parser import IntentParser, Intent


class TestIntentParser:
    """Tests for IntentParser."""
    
    def test_parse_create_script(self):
        """Test parsing create script intent."""
        parser = IntentParser()
        
        intent = parser.parse("create a script to backup the database")
        
        assert intent.name == "create_script"
        assert "description" in intent.entities
        assert "backup the database" in intent.entities["description"]
        assert intent.confidence > 0.5
    
    def test_parse_run_script(self):
        """Test parsing run script intent."""
        parser = IntentParser()
        
        intent = parser.parse("run script backup_db")
        
        assert intent.name == "run_script"
        assert intent.entities.get("name") == "backup_db"
    
    def test_parse_list_scripts(self):
        """Test parsing list scripts intent."""
        parser = IntentParser()
        
        intent = parser.parse("list all scripts")
        
        assert intent.name == "list_scripts"
    
    def test_parse_system_status(self):
        """Test parsing system status intent."""
        parser = IntentParser()
        
        intent = parser.parse("what's the system status?")
        
        assert intent.name == "system_status"
    
    def test_parse_deploy(self):
        """Test parsing deploy intent."""
        parser = IntentParser()
        
        intent = parser.parse("deploy to production")
        
        assert intent.name == "deploy"
        assert intent.entities.get("environment") == "production"
        assert intent.requires_confirmation
    
    def test_parse_stop_listening(self):
        """Test parsing stop listening intent."""
        parser = IntentParser()
        
        intent = parser.parse("that's all")
        
        assert intent.name == "stop_listening"
    
    def test_parse_help(self):
        """Test parsing help intent."""
        parser = IntentParser()
        
        intent = parser.parse("what can you do?")
        
        assert intent.name == "help"
    
    def test_parse_unknown(self):
        """Test parsing unknown intent."""
        parser = IntentParser()
        
        intent = parser.parse("foobar baz qux")
        
        assert intent.name == "unknown"
        assert intent.confidence == 0.0
    
    def test_intent_description(self):
        """Test intent description property."""
        intent = Intent(
            name="create_script",
            entities={"description": "test script"},
            confidence=0.9,
            original_text="create a script to test",
            requires_confirmation=False
        )
        
        assert "test script" in intent.description
