"""Tests for omen engine."""
import pytest
from echo.ghost.omens import OmenEngine


def test_omen_engine_initialization():
    """Test omen engine initialization."""
    omens = OmenEngine()
    
    assert omens is not None
    assert len(omens.prediction_history) == 0


def test_predict_no_omens():
    """Test prediction with no omen triggers."""
    omens = OmenEngine()
    
    context = {}
    prediction = omens.predict(context)
    
    assert prediction is None


def test_predict_backup_omen():
    """Test backup omen prediction."""
    omens = OmenEngine()
    
    context = {"days_since_backup": 10}
    prediction = omens.predict(context)
    
    assert prediction is not None
    assert "backup" in prediction.lower() or "save" in prediction.lower()


def test_predict_dependency_omen():
    """Test dependency age omen."""
    omens = OmenEngine()
    
    context = {"dependency_age_days": 100}
    prediction = omens.predict(context)
    
    assert prediction is not None
    assert "dependenc" in prediction.lower() or "update" in prediction.lower()


def test_predict_test_coverage_omen():
    """Test test coverage omen."""
    omens = OmenEngine()
    
    context = {"test_coverage": 0.3}
    prediction = omens.predict(context)
    
    assert prediction is not None
    assert "test" in prediction.lower() or "shadow" in prediction.lower()


def test_predict_error_pattern_omen():
    """Test error pattern omen."""
    omens = OmenEngine()
    
    context = {"error_pattern_repeating": True}
    prediction = omens.predict(context)
    
    assert prediction is not None
    assert "error" in prediction.lower() or "history" in prediction.lower()


def test_predict_memory_usage_omen():
    """Test memory usage omen."""
    omens = OmenEngine()
    
    context = {"memory_usage": 0.95}
    prediction = omens.predict(context)
    
    assert prediction is not None
    assert "memory" in prediction.lower() or "heavy" in prediction.lower()


def test_predict_disk_space_omen():
    """Test disk space omen."""
    omens = OmenEngine()
    
    context = {"disk_space_low": True}
    prediction = omens.predict(context)
    
    assert prediction is not None
    assert "space" in prediction.lower() or "void" in prediction.lower()


def test_predict_network_omen():
    """Test network issues omen."""
    omens = OmenEngine()
    
    context = {"network_issues": True}
    prediction = omens.predict(context)
    
    assert prediction is not None
    assert "network" in prediction.lower() or "connection" in prediction.lower()


def test_predict_merge_conflict_omen():
    """Test merge conflict omen."""
    omens = OmenEngine()
    
    context = {"merge_conflicts": True}
    prediction = omens.predict(context)
    
    assert prediction is not None
    assert "conflict" in prediction.lower() or "path" in prediction.lower()


def test_predict_complexity_omen():
    """Test complexity omen."""
    omens = OmenEngine()
    
    context = {"complexity_high": True}
    prediction = omens.predict(context)
    
    assert prediction is not None
    assert "complex" in prediction.lower() or "simple" in prediction.lower()


def test_prediction_history_tracking():
    """Test predictions are tracked in history."""
    omens = OmenEngine()
    
    context = {"days_since_backup": 10}
    prediction = omens.predict(context)
    
    assert len(omens.prediction_history) == 1
    assert prediction in omens.prediction_history


def test_get_prediction_history():
    """Test getting prediction history."""
    omens = OmenEngine()
    
    for i in range(5):
        omens.predict({"days_since_backup": 10})
        
    history = omens.get_prediction_history(3)
    
    assert len(history) == 3
    assert all(isinstance(h, str) for h in history)


def test_clear_history():
    """Test clearing prediction history."""
    omens = OmenEngine()
    
    omens.predict({"days_since_backup": 10})
    assert len(omens.prediction_history) > 0
    
    omens.clear_history()
    assert len(omens.prediction_history) == 0


def test_omen_engine_repr():
    """Test string representation."""
    omens = OmenEngine()
    
    repr_str = repr(omens)
    
    assert "OmenEngine" in repr_str
    assert "predictions=" in repr_str


def test_multiple_conditions_select_one():
    """Test with multiple conditions active selects one."""
    omens = OmenEngine()
    
    context = {
        "days_since_backup": 10,
        "dependency_age_days": 100,
        "test_coverage": 0.3,
    }
    
    prediction = omens.predict(context)
    
    # Should get one prediction, not all
    assert prediction is not None
    assert isinstance(prediction, str)
