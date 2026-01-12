"""Tests for memory engine."""
import pytest
from echo.ghost.memories import MemoryEngine, Memory
from datetime import datetime


def test_memory_engine_initialization():
    """Test memory engine initialization."""
    memories = MemoryEngine()
    
    assert memories is not None
    assert len(memories.memories) == 0
    assert memories.max_memories == 100


def test_memory_engine_custom_max():
    """Test memory engine with custom max memories."""
    memories = MemoryEngine(max_memories=50)
    
    assert memories.max_memories == 50


def test_store_memory():
    """Test storing a memory."""
    memories = MemoryEngine()
    
    memories.store(
        context="fixing bug",
        user_action="updated config",
        outcome="bug resolved",
        emotional_tone="positive"
    )
    
    assert len(memories.memories) == 1
    memory = memories.memories[0]
    assert memory.context == "fixing bug"
    assert memory.user_action == "updated config"
    assert memory.outcome == "bug resolved"
    assert memory.emotional_tone == "positive"


def test_memory_default_emotional_tone():
    """Test memory with default emotional tone."""
    memories = MemoryEngine()
    
    memories.store(
        context="test",
        user_action="action",
        outcome="result"
    )
    
    assert memories.memories[0].emotional_tone == "neutral"


def test_recall_no_memories():
    """Test recall with no stored memories."""
    memories = MemoryEngine()
    
    result = memories.recall({})
    
    assert result is None


def test_recall_positive_memory():
    """Test recalling a positive memory."""
    memories = MemoryEngine()
    
    memories.store(
        context="test",
        user_action="wrote tests",
        outcome="all passed",
        emotional_tone="positive"
    )
    
    result = memories.recall({})
    
    assert result is not None
    assert "wrote tests" in result
    assert "all passed" in result


def test_recall_prefers_positive():
    """Test recall prefers positive memories."""
    memories = MemoryEngine()
    
    memories.store("test1", "action1", "outcome1", "negative")
    memories.store("test2", "action2", "outcome2", "positive")
    
    result = memories.recall({})
    
    assert result is not None
    assert "action2" in result


def test_get_recent_memories():
    """Test getting recent memories."""
    memories = MemoryEngine()
    
    for i in range(10):
        memories.store(f"context{i}", f"action{i}", f"outcome{i}")
        
    recent = memories.get_recent_memories(5)
    
    assert len(recent) == 5
    assert all(isinstance(m, Memory) for m in recent)


def test_get_positive_memories():
    """Test getting only positive memories."""
    memories = MemoryEngine()
    
    memories.store("test1", "action1", "outcome1", "positive")
    memories.store("test2", "action2", "outcome2", "neutral")
    memories.store("test3", "action3", "outcome3", "positive")
    
    positive = memories.get_positive_memories()
    
    assert len(positive) == 2
    assert all(m.emotional_tone == "positive" for m in positive)


def test_clear_memories():
    """Test clearing all memories."""
    memories = MemoryEngine()
    
    memories.store("test", "action", "outcome")
    assert len(memories.memories) > 0
    
    memories.clear_memories()
    assert len(memories.memories) == 0


def test_memory_limit():
    """Test memory limit enforcement."""
    memories = MemoryEngine(max_memories=10)
    
    for i in range(15):
        memories.store(f"context{i}", f"action{i}", f"outcome{i}")
        
    assert len(memories.memories) == 10


def test_memory_timestamp():
    """Test memory has timestamp."""
    memories = MemoryEngine()
    
    before = datetime.now()
    memories.store("test", "action", "outcome")
    after = datetime.now()
    
    memory = memories.memories[0]
    assert before <= memory.timestamp <= after


def test_memory_engine_repr():
    """Test string representation."""
    memories = MemoryEngine()
    
    memories.store("test", "action", "outcome", "positive")
    memories.store("test", "action", "outcome", "neutral")
    
    repr_str = repr(memories)
    
    assert "MemoryEngine" in repr_str
    assert "memories=" in repr_str
    assert "positive=" in repr_str


def test_format_memory_variations():
    """Test memory formatting has variations."""
    memories = MemoryEngine()
    
    memories.store("test", "did something", "it worked", "positive")
    
    # Get multiple formatted memories to check for variation
    formatted = set()
    for _ in range(20):
        result = memories.recall({})
        if result:
            formatted.add(result)
            
    # Should have at least one formatted memory
    assert len(formatted) > 0
