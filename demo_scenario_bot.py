#!/usr/bin/env python3
"""
Echo Scenario Bot - Interactive Demo
Demonstrates Echo's new scenario-based scripting capabilities

Run this to have an interactive conversation with Echo where she
gathers requirements and generates custom scripts for you.
"""

import sys
sys.path.insert(0, '/home/runner/work/masterchief/masterchief')

from echo.scenario_bot import EchoScenarioBot


def print_banner():
    """Print the Echo banner"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                  🌙 ECHO SCENARIO BOT 🌙                          ║
║                                                                  ║
║           Interactive Script Generation Through Dialogue          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

Echo has evolved! She's now an interactive scripting companion who
generates scripts through natural conversation.

Just tell her what you want to create, answer a few questions, and
watch as she generates exactly the script you need.

Type 'quit' or 'exit' to end the conversation.

""")


def run_interactive_mode():
    """Run Echo in interactive mode"""
    print_banner()
    
    bot = EchoScenarioBot()
    
    # Start the conversation
    print(bot.start())
    print()
    
    # Main conversation loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                print("\n🌙 Echo: Goodbye! Come back anytime you need a script. 💜\n")
                break
            
            # Process the input
            print()
            response = bot.chat(user_input)
            print(f"Echo: {response}")
            print()
            
        except KeyboardInterrupt:
            print("\n\n🌙 Echo: Interrupted. Goodbye! 💜\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            continue


def run_demo_scenario():
    """Run a pre-programmed demo scenario"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                      DEMO SCENARIO MODE                           ║
╚══════════════════════════════════════════════════════════════════╝

This demo shows a complete conversation flow where Echo helps create
a Kubernetes deployment script.

""")
    
    bot = EchoScenarioBot()
    
    # Demo conversation
    conversation = [
        ("Echo", bot.start()),
        ("User", "I need to deploy my application to Kubernetes"),
        ("User", "mywebapp"),
        ("User", "production"),
        ("User", "yes"),
        ("User", "no, that's it"),
        ("User", "yes"),
    ]
    
    for i, (speaker, message) in enumerate(conversation):
        if speaker == "Echo":
            print(f"\n🌙 Echo:\n{message}\n")
            print("-" * 70)
        else:
            print(f"\n👤 User: {message}\n")
            if i < len(conversation) - 1:
                # Process response and get Echo's reply
                response = bot.chat(message)
                conversation.insert(i + 1, ("Echo", response))
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                         DEMO COMPLETE                             ║
╚══════════════════════════════════════════════════════════════════╝

As you can see, Echo:
1. ✓ Understood the user's goal (Kubernetes deployment)
2. ✓ Asked relevant questions to gather requirements
3. ✓ Confirmed understanding before generating
4. ✓ Generated a complete, ready-to-use script

This is scenario-based script generation in action!

Run 'python demo_scenario_bot.py' for interactive mode.
""")


def show_examples():
    """Show example use cases"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                     EXAMPLE SCENARIOS                             ║
╚══════════════════════════════════════════════════════════════════╝

Here are some things you can ask Echo to create:

🚀 DEPLOYMENT
   "I need to deploy my app to Kubernetes"
   "Help me deploy a Docker container"
   "I want to deploy infrastructure with Terraform"

🏗️  BUILD
   "I need to build a Docker image"
   "Help me build my Python package"
   "I want to build a Node.js application"

🧪 TESTING
   "I need to run unit tests"
   "Help me set up integration tests"
   "I want to run tests with coverage"

📊 MONITORING
   "I need to set up Prometheus alerts"
   "Help me create a dashboard"
   "I want to monitor my application"

🔒 SECURITY
   "I need to scan for vulnerabilities"
   "Help me rotate secrets"
   "I want to check compliance"

Just describe what you want in natural language, and Echo will:
1. Ask clarifying questions
2. Gather all necessary details
3. Confirm her understanding
4. Generate a custom script for you

""")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == 'demo':
            run_demo_scenario()
        elif mode == 'examples':
            show_examples()
        else:
            print("Usage: python demo_scenario_bot.py [mode]")
            print("Modes:")
            print("  (none)   - Interactive conversation with Echo")
            print("  demo     - Run a pre-programmed demo scenario")
            print("  examples - Show example use cases")
    else:
        run_interactive_mode()


if __name__ == "__main__":
    main()
