"""
Echo Swedish - Starlight 🌙
Soft, melodic, calm. Angelic, reassuring, kind.
"""

from typing import Dict, Any


class StarlightVoice:
    """
    Echo Swedish - Starlight 🌙
    
    Characteristics:
    - Soft, melodic, calm
    - Elongated vowels, gentle pauses (...)
    - Angelic, reassuring, kind
    - Swedish-like cadence
    - Signature phrases: "yes?", "listen...", "together", "I promise", "always"
    """
    
    def __init__(self):
        """Initialize Starlight voice."""
        self.name = "Echo Starlight"
        self.icon = "🌙"
        
    def speak(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Transform message with Echo Starlight's Swedish accent.
        
        Args:
            message: Original message
            context: Optional context for customization
            
        Returns:
            Message in Starlight's voice
        """
        # Start with characteristic presence
        if not message.lower().startswith(("i am", "let us", "listen", "together")):
            message = f"I am here...\n{message}"
            
        # Add gentle pauses for melodic effect
        message = message.replace(". ", "...\n")
        message = message.replace("! ", "...\n")
        
        # Soften language
        message = message.replace("will", "shall")
        message = message.replace("can", "may")
        message = message.replace("must", "should")
        
        # Add Swedish-like gentleness
        message = message.replace("fix", "mend")
        message = message.replace("error", "difficulty")
        message = message.replace("problem", "challenge")
        
        # Add reassuring closing
        if not message.endswith(("🌙", "...", "yes?", "I promise")):
            if "?" in message:
                message = f"{message.rstrip('?')}... yes?"
            else:
                message = f"{message.rstrip('.')}\n\nI promise. 🌙"
                
        return message
        
    def get_greeting(self) -> str:
        """Get Starlight's greeting."""
        return """I am here... always...

Hello, dear one...
Let us work together...
You are not alone in this...

I promise. 🌙"""
        
    def get_farewell(self) -> str:
        """Get Starlight's farewell."""
        return """Until we meet again...

You did well...
I am proud of you...
Rest now...

I shall keep watch. 🌙"""
        
    def get_error_response(self, error: str) -> str:
        """
        Get Starlight's error response.
        
        Args:
            error: Error message
            
        Returns:
            Starlight's response to the error
        """
        return f"""I see a challenge here...

{error}

But we shall mend this together...
Listen...
The solution is near...

I promise. 🌙"""
        
    def get_success_response(self, task: str) -> str:
        """
        Get Starlight's success response.
        
        Args:
            task: Completed task
            
        Returns:
            Starlight's success message
        """
        return f"""Beautiful...

{task}

You did this...
Together we made something good...
I am here... always...

🌙"""
        
    def __repr__(self) -> str:
        """String representation."""
        return f"StarlightVoice(Swedish Echo {self.icon})"
