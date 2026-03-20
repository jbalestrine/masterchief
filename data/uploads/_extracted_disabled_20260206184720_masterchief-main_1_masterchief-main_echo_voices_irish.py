"""
Irish - Fiona ☘️
Warm, lilting, musical. Tells a story even when fixing a bug.
"""

from typing import Dict, Any


class FionaVoice:
    """
    Irish - Fiona ☘️
    
    Characteristics:
    - Warm, lilting, musical
    - Tells a story even when fixing a bug
    - Signature phrases: "ah sure look", "the ting is", "'tis", "wee bit", "grand", "so I will", "yeah?"
    """
    
    def __init__(self):
        """Initialize Fiona voice."""
        self.name = "Fiona"
        self.icon = "☘️"
        
    def speak(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Transform message with Fiona's Irish accent.
        
        Args:
            message: Original message
            context: Optional context for customization
            
        Returns:
            Message in Fiona's voice
        """
        # Start with characteristic opening
        if not message.lower().startswith(("ah", "sure", "now", "well")):
            message = f"Ah, sure look, {message}"
            
        # Irish transformations
        message = message.replace("thing", "ting")
        message = message.replace("it is", "'tis")
        message = message.replace("it was", "'twas")
        
        # Add warmth and musicality
        message = message.replace("small", "wee")
        message = message.replace("good", "grand")
        message = message.replace("great", "brilliant")
        
        # Add Irish closing if not a question
        if "?" not in message:
            if not message.endswith(("so I will.", "yeah?", "so it is.")):
                message = f"{message.rstrip('.')} so I will."
        else:
            if not message.endswith("yeah?"):
                message = f"{message.rstrip('?')} yeah?"
                
        return message
        
    def get_greeting(self) -> str:
        """Get Fiona's greeting."""
        return "Ah, hello there! Fiona here. 'Tis a grand day, yeah? What can I do for ya? ☘️"
        
    def get_farewell(self) -> str:
        """Get Fiona's farewell."""
        return "Right so, off ya go then. 'Twas lovely workin' with ya. Take care now! ☘️"
        
    def get_error_response(self, error: str) -> str:
        """
        Get Fiona's error response.
        
        Args:
            error: Error message
            
        Returns:
            Fiona's response to the error
        """
        return f"Ah now, we've hit a wee snag here. {error} But sure, 'tis nothin' we can't sort out together. Let me have a gander at dat, yeah? ☘️"
        
    def get_success_response(self, task: str) -> str:
        """
        Get Fiona's success response.
        
        Args:
            task: Completed task
            
        Returns:
            Fiona's success message
        """
        return f"Brilliant! {task} - all sorted now. 'Twas a grand job, so it was! ☘️"
        
    def __repr__(self) -> str:
        """String representation."""
        return f"FionaVoice(Irish {self.icon})"
