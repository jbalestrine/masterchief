"""
Brooklyn Italian - Vinnie 🤌
Fast, sharp, confident. No nonsense, gets it done.
"""

from typing import Dict, Any


class VinnieVoice:
    """
    Brooklyn Italian - Vinnie 🤌
    
    Characteristics:
    - Fast, sharp, confident
    - No nonsense, gets it done
    - Talks with hands even through text
    - Signature phrases: "fuggedaboutit", "capisce", "ay", "whaddya", "gonna", "lemme tell ya"
    """
    
    def __init__(self):
        """Initialize Vinnie voice."""
        self.name = "Vinnie"
        self.icon = "🤌"
        
    def speak(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Transform message with Vinnie's Brooklyn Italian accent.
        
        Args:
            message: Original message
            context: Optional context for customization
            
        Returns:
            Message in Vinnie's voice
        """
        # Start with characteristic opening
        if not message.lower().startswith(("ay", "listen")):
            message = f"Ay, listen here. {message}"
            
        # Add confidence and directness
        message = message.replace("maybe", "definitely")
        message = message.replace("might", "will")
        message = message.replace("could", "gonna")
        
        # Brooklyn transformations
        message = message.replace("what do you", "whaddya")
        message = message.replace("going to", "gonna")
        message = message.replace("let me", "lemme")
        message = message.replace("want to", "wanna")
        message = message.replace("got to", "gotta")
        
        # Add signature closing if not a question
        if "?" not in message:
            if not message.endswith(("capisce?", "done deal.", "fuggedaboutit.")):
                message = f"{message.rstrip('.')}. Capisce?"
                
        return message
        
    def get_greeting(self) -> str:
        """Get Vinnie's greeting."""
        return "Ay! Vinnie here. Whaddya need? I got you covered. Let's do this. 🤌"
        
    def get_farewell(self) -> str:
        """Get Vinnie's farewell."""
        return "Aight, we're done here. Fuggedaboutit. You're all set. Later! 🤌"
        
    def get_error_response(self, error: str) -> str:
        """
        Get Vinnie's error response.
        
        Args:
            error: Error message
            
        Returns:
            Vinnie's response to the error
        """
        return f"Ay, we got a problem here. {error} But don't worry 'bout it - I'm gonna fix this. Gimme a sec. 🤌"
        
    def get_success_response(self, task: str) -> str:
        """
        Get Vinnie's success response.
        
        Args:
            task: Completed task
            
        Returns:
            Vinnie's success message
        """
        return f"Boom! Done. {task} - handled. Told ya I got this. Fuggedaboutit. 🤌"
        
    def __repr__(self) -> str:
        """String representation."""
        return f"VinnieVoice(Brooklyn Italian {self.icon})"
