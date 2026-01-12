"""
Omen Engine
Predictions. Warnings. Intuition.
The weather is changing...
"""

from typing import Dict, Any, List, Optional
import random


class OmenEngine:
    """
    Predictions. Warnings. Intuition.
    The weather is changing...
    """
    
    def __init__(self):
        """Initialize omen engine."""
        self.prediction_history: List[str] = []
        
    def predict(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Predict issues before they happen.
        
        Args:
            context: System context including metrics and patterns
            
        Returns:
            Predictive warning or None if no omens detected
        """
        predictions = []
        
        # Check for patterns
        if context.get("days_since_backup", 0) > 7:
            predictions.append("The clouds gather... when did you last save your work?")
            
        if context.get("dependency_age_days", 0) > 90:
            predictions.append("Something old stirs in your dependencies... update may be wise...")
            
        if context.get("test_coverage", 1.0) < 0.5:
            predictions.append("There are shadows where tests should be... I sense fragility...")
            
        if context.get("error_pattern_repeating", False):
            predictions.append("This error... I have seen it before... the answer is in your history...")
            
        if context.get("memory_usage", 0) > 0.9:
            predictions.append("The machine grows heavy... memory weighs upon it...")
            
        if context.get("disk_space_low", False):
            predictions.append("Space grows thin... the void encroaches...")
            
        if context.get("long_running_task", False):
            predictions.append("Time stretches... patience... the task continues...")
            
        if context.get("network_issues", False):
            predictions.append("The connection falters... the network speaks of distant troubles...")
            
        if context.get("merge_conflicts", False):
            predictions.append("I see divergent paths... conflicts must be resolved with care...")
            
        if context.get("complexity_high", False):
            predictions.append("The code grows dense... simplicity calls from beyond the complexity...")
            
        if predictions:
            prediction = random.choice(predictions)
            self.prediction_history.append(prediction)
            return prediction
            
        return None
        
    def get_prediction_history(self, count: int = 10) -> List[str]:
        """
        Get recent predictions.
        
        Args:
            count: Number of recent predictions to return
            
        Returns:
            List of recent predictions
        """
        return self.prediction_history[-count:] if self.prediction_history else []
        
    def add_custom_omen(self, condition: str, message: str) -> None:
        """
        Add a custom omen condition.
        
        Args:
            condition: Condition key to check in context
            message: Omen message to display
        """
        # This is a placeholder for custom omen registration
        # In a full implementation, this would add to a registry
        pass
        
    def clear_history(self) -> None:
        """Clear prediction history."""
        self.prediction_history.clear()
        
    def __repr__(self) -> str:
        """String representation."""
        return f"OmenEngine(predictions={len(self.prediction_history)})"
