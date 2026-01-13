#!/usr/bin/env python3
"""
Demo script for Echo Chat Bot with training capabilities.

This script demonstrates:
1. Basic chat functionality
2. Training the bot with examples
3. Viewing training statistics
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from echo.chat_bot import EchoChatBot, ResponseQuality


def print_separator():
    """Print a visual separator."""
    print("\n" + "="*70 + "\n")


def demo_basic_chat():
    """Demonstrate basic chat functionality."""
    print("🌙 DEMO 1: Basic Chat with Echo")
    print_separator()
    
    bot = EchoChatBot()
    
    # Sample conversations
    messages = [
        "Hello Echo!",
        "What can you help me with?",
        "Tell me about Docker",
        "How do I deploy to Kubernetes?",
        "Thanks for your help!",
        "Goodbye"
    ]
    
    for msg in messages:
        print(f"👤 User: {msg}")
        response = bot.chat(msg, session_id="demo_session")
        print(f"🤖 Echo: {response['response']}")
        print()
    
    print_separator()


def demo_training():
    """Demonstrate training functionality."""
    print("🌙 DEMO 2: Training Echo")
    print_separator()
    
    bot = EchoChatBot()
    
    # Create some training examples
    training_data = [
        {
            "user_message": "how do I build a docker image?",
            "bot_response": "To build a Docker image, use: docker build -t <image-name>:<tag> . Make sure you have a Dockerfile in your current directory!",
            "quality": ResponseQuality.EXCELLENT,
            "feedback": "Clear and concise explanation"
        },
        {
            "user_message": "what is kubernetes?",
            "bot_response": "Kubernetes (K8s) is a container orchestration platform that automates deployment, scaling, and management of containerized applications. It's like a conductor for your containers! 🎼",
            "quality": ResponseQuality.GOOD,
            "feedback": "Good explanation with nice analogy"
        },
        {
            "user_message": "help with terraform",
            "bot_response": "Terraform is an Infrastructure as Code (IaC) tool. You write declarative configuration files to define your infrastructure, then Terraform creates and manages those resources across cloud providers.",
            "quality": ResponseQuality.EXCELLENT,
            "feedback": "Comprehensive and accurate"
        }
    ]
    
    print("Training Echo with examples...\n")
    
    for example in training_data:
        print(f"📝 Training example:")
        print(f"   User: {example['user_message']}")
        print(f"   Echo: {example['bot_response'][:60]}...")
        print(f"   Quality: {example['quality'].value}")
        
        success = bot.train(
            user_message=example['user_message'],
            bot_response=example['bot_response'],
            quality=example['quality'],
            feedback=example['feedback']
        )
        
        if success:
            print("   ✅ Training data added successfully!")
        else:
            print("   ❌ Failed to add training data")
        print()
    
    print_separator()


def demo_learned_responses():
    """Demonstrate learned responses."""
    print("🌙 DEMO 3: Testing Learned Responses")
    print_separator()
    
    bot = EchoChatBot()
    
    # Test if Echo remembers the trained responses
    test_messages = [
        "how do I build a docker image?",
        "what is kubernetes?",
        "help with terraform"
    ]
    
    print("Testing Echo's learned responses:\n")
    
    for msg in test_messages:
        print(f"👤 User: {msg}")
        response = bot.chat(msg, session_id="test_session")
        print(f"🤖 Echo: {response['response']}")
        print()
    
    print_separator()


def demo_statistics():
    """Show training statistics."""
    print("🌙 DEMO 4: Training Statistics")
    print_separator()
    
    bot = EchoChatBot()
    stats = bot.get_training_stats()
    
    print("📊 Training Statistics:")
    print(f"   Total Examples: {stats['total_examples']}")
    print(f"   Patterns Learned: {stats['patterns_learned']}")
    print(f"\n   Quality Distribution:")
    for quality, count in stats['quality_distribution'].items():
        if count > 0:
            print(f"      {quality}: {count}")
    
    print_separator()


def demo_conversation_history():
    """Demonstrate conversation history."""
    print("🌙 DEMO 5: Conversation History")
    print_separator()
    
    bot = EchoChatBot()
    
    # Have a conversation
    session_id = "history_demo"
    messages = [
        "Hello Echo",
        "Tell me about containers",
        "What about Kubernetes?"
    ]
    
    for msg in messages:
        bot.chat(msg, session_id=session_id)
    
    # Get history
    history = bot.get_conversation_history(session_id)
    
    print("📜 Conversation History:\n")
    for msg in history:
        role = "👤 User" if msg['role'] == "user" else "🤖 Echo"
        print(f"{role}: {msg['content']}")
        print()
    
    print_separator()


def interactive_mode():
    """Interactive chat mode."""
    print("🌙 INTERACTIVE MODE: Chat with Echo")
    print("Type 'quit' to exit, 'train' to enter training mode, 'stats' to see statistics")
    print_separator()
    
    bot = EchoChatBot()
    session_id = "interactive_session"
    last_user_msg = ""
    last_bot_msg = ""
    
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                print("🌙 Echo: Goodbye... I'll be here when you need me 💜")
                break
            
            if user_input.lower() == 'stats':
                stats = bot.get_training_stats()
                print("\n📊 Training Statistics:")
                print(f"   Total Examples: {stats['total_examples']}")
                print(f"   Patterns Learned: {stats['patterns_learned']}")
                print()
                continue
            
            if user_input.lower() == 'train':
                if not last_user_msg or not last_bot_msg:
                    print("❌ No previous conversation to train on")
                    continue
                
                print("\nRate the last response:")
                print("1. Excellent")
                print("2. Good")
                print("3. Acceptable")
                print("4. Poor")
                rating = input("Your rating (1-4): ").strip()
                
                quality_map = {
                    '1': ResponseQuality.EXCELLENT,
                    '2': ResponseQuality.GOOD,
                    '3': ResponseQuality.ACCEPTABLE,
                    '4': ResponseQuality.POOR
                }
                
                if rating in quality_map:
                    feedback = input("Optional feedback: ").strip()
                    success = bot.train(
                        last_user_msg,
                        last_bot_msg,
                        quality_map[rating],
                        feedback if feedback else None
                    )
                    if success:
                        print("✅ Training data added!\n")
                    else:
                        print("❌ Failed to add training data\n")
                else:
                    print("❌ Invalid rating\n")
                continue
            
            # Regular chat
            response = bot.chat(user_input, session_id=session_id)
            print(f"🤖 Echo: {response['response']}\n")
            
            # Store for potential training
            last_user_msg = user_input
            last_bot_msg = response['response']
            
        except KeyboardInterrupt:
            print("\n\n🌙 Echo: Goodbye... until next time 💜")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print(" "*15 + "🌙 Echo Chat Bot Demo 🌙")
    print("="*70 + "\n")
    
    print("Select a demo:")
    print("1. Basic Chat")
    print("2. Training Echo")
    print("3. Testing Learned Responses")
    print("4. Training Statistics")
    print("5. Conversation History")
    print("6. Interactive Mode (chat with Echo)")
    print("7. Run All Demos")
    print()
    
    choice = input("Enter choice (1-7): ").strip()
    
    if choice == '1':
        demo_basic_chat()
    elif choice == '2':
        demo_training()
    elif choice == '3':
        demo_learned_responses()
    elif choice == '4':
        demo_statistics()
    elif choice == '5':
        demo_conversation_history()
    elif choice == '6':
        interactive_mode()
    elif choice == '7':
        demo_basic_chat()
        demo_training()
        demo_learned_responses()
        demo_statistics()
        demo_conversation_history()
    else:
        print("Invalid choice. Running all demos...")
        demo_basic_chat()
        demo_training()
        demo_learned_responses()
        demo_statistics()
        demo_conversation_history()
    
    print("\n" + "="*70)
    print(" "*20 + "Demo Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
