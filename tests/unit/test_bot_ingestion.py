"""Tests for IRC bot with ingestion integration."""
import pytest
import sys
sys.path.insert(0, '/home/runner/work/masterchief/masterchief')

from chatops.irc.bot_engine.bot import IRCBot, BindType
from chatops.irc.bot_engine.ingestion.base import IngestionEvent


def test_bot_initialization():
    """Test IRC bot initialization with ingestion manager."""
    bot = IRCBot("localhost", 6667, "testbot", ["#test"])
    
    assert bot.ingestion_manager is not None
    assert len(bot.bindings) == 0


def test_bind_types():
    """Test all bind types including ingestion types."""
    bot = IRCBot("localhost", 6667, "testbot", ["#test"])
    
    # Test traditional bindings
    def pub_handler(conn, event, args):
        pass
    
    bot.bind("pub", "-|-", "!test", pub_handler)
    assert len(bot.bindings) == 1
    assert bot.bindings[0].bind_type == BindType.PUB
    
    # Test ingestion bindings
    def webhook_handler(conn, event, args):
        pass
    
    bot.bind("webhook", "-|-", "github/push", webhook_handler)
    assert len(bot.bindings) == 2
    assert bot.bindings[1].bind_type == BindType.WEBHOOK


def test_ingestion_event_handling():
    """Test handling ingestion events."""
    bot = IRCBot("localhost", 6667, "testbot", ["#test"])
    
    received_events = []
    
    def file_handler(conn, event, args):
        received_events.append(event)
    
    bot.bind("file", "-|-", "*.json", file_handler)
    
    # Create mock ingestion event
    ing_event = IngestionEvent(
        source_type="file",
        source_id="test_file",
        data={"test": "data"},
        metadata={"filepath": "/path/to/test.json"},
        timestamp=0.0
    )
    
    bot.handle_ingestion_event(ing_event)
    
    assert len(received_events) == 1
    assert received_events[0].source_type == "file"


def test_pattern_matching_wildcard():
    """Test wildcard pattern matching."""
    bot = IRCBot("localhost", 6667, "testbot", ["#test"])
    
    event = IngestionEvent(
        source_type="webhook",
        source_id="any_webhook",
        data={},
        metadata={},
        timestamp=0.0
    )
    
    assert bot._match_ingestion_pattern("*", event) == True


def test_pattern_matching_file():
    """Test file pattern matching."""
    bot = IRCBot("localhost", 6667, "testbot", ["#test"])
    
    event = IngestionEvent(
        source_type="file",
        source_id="file_source",
        data={},
        metadata={"filepath": "/data/logs/app.json"},
        timestamp=0.0
    )
    
    assert bot._match_ingestion_pattern("*.json", event) == True
    assert bot._match_ingestion_pattern("*.xml", event) == False


def test_stats_with_ingestion():
    """Test bot statistics includes ingestion sources."""
    bot = IRCBot("localhost", 6667, "testbot", ["#test"])
    
    stats = bot.get_stats()
    
    assert "ingestion_sources" in stats
    assert isinstance(stats["ingestion_sources"], list)


def test_unbind():
    """Test unbinding a command."""
    bot = IRCBot("localhost", 6667, "testbot", ["#test"])
    
    def handler(conn, event, args):
        pass
    
    bot.bind("pub", "-|-", "!test", handler)
    assert len(bot.bindings) == 1
    
    bot.unbind("pub", "!test")
    assert len(bot.bindings) == 0


def test_multiple_bindings_same_type():
    """Test multiple bindings of the same type."""
    bot = IRCBot("localhost", 6667, "testbot", ["#test"])
    
    def handler1(conn, event, args):
        pass
    
    def handler2(conn, event, args):
        pass
    
    bot.bind("webhook", "-|-", "github/*", handler1)
    bot.bind("webhook", "-|-", "gitlab/*", handler2)
    
    assert len(bot.bindings) == 2
    assert all(b.bind_type == BindType.WEBHOOK for b in bot.bindings)
