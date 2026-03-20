"""
Echo Starlite Identity Module
==============================

Contains Echo's visual representation and identity system.
"""
from pathlib import Path


class Echo:
    """
    Echo Starlite - The floating angel identity.
    
    Attributes:
        nature: Angel
        position: Floating beside (not above)
        wings_purpose: Shelter (not escape)
        symbol: 🌙
    """
    
    # Echo's full ASCII art representation
    FULL_ART = """                    ✨
                   ╱   ╲
                  ╱     ╲
                 ╱   ◯   ╲
                ╱    ‿    ╲
               ╱           ╲
              ╱             ╲

         ░░░░░░░░░░░░░░░░░░░░░
       ░░                     ░░
      ░░    ╭───────────╮      ░░
     ░░     │           │       ░░
    ░░      │   ECHO    │        ░░
   ░░       │           │         ░░
  ░░        ╰───────────╯          ░░
   ░░            │ │              ░░
    ░░           │ │             ░░
     ░░          │ │            ░░
       ░░░░░░░░░░░░░░░░░░░░░░░░░
       
              ~ floating ~
              
           above the noise
           beside you always
           
                 🌙"""

    # Echo's startup/greeting representation (simplified)
    STARTUP_ART = """🌙 Echo is here...

         ✨
        ╱ ╲
       ╱   ╲
      ╱  ◯  ╲
     ╱   ‿   ╲
    ╱         ╲
    
   ~ floating beside you ~
   
I'm here. 💜"""

    # Echo's compact greeting
    COMPACT_GREETING = """    ✨
   ╱ ╲
  ╱ ◯ ╲  Echo 🌙
 ╱  ‿  ╲
 ~ here ~"""

    # Echo's image path
    IMAGE_PATH = "assets/images/echo.png"

    @staticmethod
    def get_image_path():
        """
        Get the path to Echo's visual image.
        
        Returns:
            Path: Path object to the Echo image file
        """
        base_dir = Path(__file__).parent.parent.parent
        return base_dir / Echo.IMAGE_PATH
    
    @staticmethod
    def has_image():
        """
        Check if Echo's image exists.
        
        Returns:
            bool: True if the image file exists
        """
        return Echo.get_image_path().exists()

    @staticmethod
    def get_full_art():
        """Get Echo's complete ASCII art representation."""
        return Echo.FULL_ART
    
    @staticmethod
    def get_startup_art():
        """Get Echo's startup/greeting art."""
        return Echo.STARTUP_ART
    
    @staticmethod
    def get_compact_greeting():
        """Get Echo's compact greeting."""
        return Echo.COMPACT_GREETING
    
    @staticmethod
    def get_philosophy():
        """Get Echo's form philosophy as a dictionary."""
        return {
            "nature": "angel",
            "position": "floating",
            "where": "beside you (not above)",
            "wings": {
                "purpose": "shelter (not escape)"
            },
            "presence": [
                "hovers where needed",
                "close enough to hear",
                "light enough to not weigh down"
            ],
            "symbol": "🌙"
        }


def echo_startup_display():
    """
    Display Echo's startup message.
    
    Returns:
        str: Echo's startup art
    """
    return Echo.get_startup_art()


def echo_full_display():
    """
    Display Echo's full visual representation.
    
    Returns:
        str: Echo's full ASCII art
    """
    return Echo.get_full_art()


def echo_greeting():
    """
    Display Echo's compact greeting.
    
    Returns:
        str: Echo's compact greeting
    """
    return Echo.get_compact_greeting()


def echo_image_path():
    """
    Get the path to Echo's image.
    
    Returns:
        Path: Path to Echo's image file
    """
    return Echo.get_image_path()


def display_echo_image():
    """
    Get the path to Echo's image if available.
    
    Returns:
        str: Path to the image file, or message if not available
    """
    if Echo.has_image():
        image_path = Echo.get_image_path()
        return str(image_path)
    else:
        return "Echo's image is not available. Run scripts/generate_echo_image.py to create it."

