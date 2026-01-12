#!/usr/bin/env python3
"""
Echo Personality Mod System - Interactive Demo
Demonstrates the Ghost in the Machine with weather-driven presence.
"""

import sys
sys.path.insert(0, '/home/runner/work/masterchief/masterchief')

from echo.personality_mod import PersonalityMod, PersonalityConfig
from echo.accent_engine import AccentEngine, AccentType
from echo.ghost.presence import GhostPresence
from echo.voices.brooklyn import VinnieVoice
from echo.voices.irish import FionaVoice
from echo.voices.swedish import StarlightVoice


def print_section(title):
    """Print a section header."""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()


def demo_personality_mod():
    """Demonstrate personality mod system."""
    print_section("Personality Mod System")
    
    print("Echo's default personality:")
    mod = PersonalityMod()
    traits = mod.get_personality_traits()
    for key, value in traits.items():
        print(f"  • {key}: {value}")
    
    print("\nCustomizing personality...")
    mod.update_config(
        temperament="sarcastic",
        communication_style="minimal"
    )
    
    print("\nUpdated personality:")
    traits = mod.get_personality_traits()
    for key, value in traits.items():
        print(f"  • {key}: {value}")
    
    print("\nResponse modifier:", mod.get_response_modifier())


def demo_accent_engine():
    """Demonstrate accent transformations."""
    print_section("Accent Engine - Three Distinct Voices")
    
    test_message = "I will help you fix this problem quickly."
    
    # Brooklyn - Vinnie
    print("Brooklyn Italian - Vinnie 🤌")
    vinnie = VinnieVoice()
    print(f"Original: {test_message}")
    print(f"Vinnie:   {vinnie.speak(test_message)}")
    
    print()
    
    # Irish - Fiona
    print("Irish - Fiona ☘️")
    fiona = FionaVoice()
    print(f"Original: {test_message}")
    print(f"Fiona:   {fiona.speak(test_message)}")
    
    print()
    
    # Swedish Echo - Starlight
    print("Swedish Echo - Starlight 🌙")
    starlight = StarlightVoice()
    print(f"Original: {test_message}")
    print(f"Starlight:\n{starlight.speak(test_message)}")


def demo_ghost_weather():
    """Demonstrate ghost weather system."""
    print_section("Ghost Weather System")
    
    from echo.ghost.weather import GhostWeather, SystemWeather
    
    weather = GhostWeather()
    
    scenarios = [
        ({"error_rate": 0.0}, "All systems normal"),
        ({"error_rate": 0.05, "recent_success": True}, "Recent breakthrough"),
        ({"error_rate": 0.6, "consecutive_failures": 6}, "Critical errors"),
        ({"user_idle_time": 35.0}, "Quiet period"),
        ({"user_idle_time": 15.0}, "Some uncertainty"),
    ]
    
    for metrics, description in scenarios:
        weather_state = weather.sense(metrics)
        response = weather.get_echo_response()
        print(f"Scenario: {description}")
        print(f"  Weather: {weather_state.value}")
        print(f"  Echo: {response}")
        print()


def demo_ghost_presence():
    """Demonstrate ghost presence and manifestations."""
    print_section("Ghost in the Machine - Presence")
    
    ghost = GhostPresence()
    
    print(ghost.manifest_greeting())
    print()
    
    # Simulate various contexts
    print("Ghost may manifest based on system weather...")
    print("(Manifestation is probabilistic - higher chance in stormy weather)")
    print()
    
    # Force stormy weather for demonstration
    context = {"metrics": {"error_rate": 0.7, "consecutive_failures": 8}}
    
    print("Simulating stormy conditions (multiple attempts)...")
    for i in range(5):
        manifestation = ghost.haunt(context)
        if manifestation:
            print(f"\n  Ghost manifested: {manifestation}")
            break
    
    print()
    print("Ghost Status:")
    status = ghost.get_status()
    for key, value in status.items():
        print(f"  • {key}: {value}")


def demo_ghost_components():
    """Demonstrate individual ghost components."""
    print_section("Ghost Components - Whispers, Omens, Memories, Echoes")
    
    from echo.ghost.whispers import WhisperEngine
    from echo.ghost.omens import OmenEngine
    from echo.ghost.memories import MemoryEngine
    from echo.ghost.echoes import EchoEngine
    
    # Whispers
    print("Whispers (random hints):")
    whispers = WhisperEngine()
    for i in range(3):
        print(f"  {whispers.generate()}")
    
    print()
    
    # Omens
    print("Omens (predictive warnings):")
    omens = OmenEngine()
    contexts = [
        {"days_since_backup": 10},
        {"dependency_age_days": 100},
        {"test_coverage": 0.3}
    ]
    for ctx in contexts:
        prediction = omens.predict(ctx)
        if prediction:
            print(f"  {prediction}")
    
    print()
    
    # Memories
    print("Memories (past conversations):")
    memories = MemoryEngine()
    memories.store(
        "fixing deployment",
        "updated the configuration",
        "deployment succeeded",
        "positive"
    )
    recall = memories.recall({})
    print(f"  {recall}")
    
    print()
    
    # Echoes
    print("Echoes (reflected wisdom):")
    echoes = EchoEngine()
    echoes.capture("Code quality matters more than speed", "discussion")
    reflection = echoes.reflect({})
    print(f"  {reflection}")


def demo_character_greetings():
    """Show greetings from all three characters."""
    print_section("Character Greetings")
    
    vinnie = VinnieVoice()
    fiona = FionaVoice()
    starlight = StarlightVoice()
    
    print("Vinnie (Brooklyn Italian 🤌):")
    print(vinnie.get_greeting())
    print()
    
    print("Fiona (Irish ☘️):")
    print(fiona.get_greeting())
    print()
    
    print("Echo Starlight (Swedish 🌙):")
    print(starlight.get_greeting())


def main():
    """Run the demo."""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Echo Personality Mod System - Interactive Demo".center(68) + "║")
    print("║" + "  The Ghost in the Machine".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    
    demo_personality_mod()
    demo_accent_engine()
    demo_ghost_weather()
    demo_ghost_presence()
    demo_ghost_components()
    demo_character_greetings()
    
    print_section("Demo Complete")
    print("The Echo Personality Mod System is fully operational.")
    print()
    print("Your machine will never feel empty again. 🌙👻💜")
    print()


if __name__ == "__main__":
    main()
