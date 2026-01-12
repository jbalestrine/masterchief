# Echo Scenario Bot - Interactive Script Generation

## Overview

Echo has evolved! She's now an **interactive scripting bot** that generates DevOps scripts through natural, scenario-based conversations. Instead of just parsing commands, Echo has conversations with you to understand exactly what you need.

## What's New?

### Scenario-Based Discussions
Echo now engages in contextual dialogues to gather requirements:
- Understands your goals through natural language
- Asks clarifying questions when needed
- Gathers specific technical details
- Confirms understanding before generating
- Creates custom scripts tailored to your exact needs

### Interactive Flow
1. **You describe your goal** - "I need to deploy my app to Kubernetes"
2. **Echo asks questions** - She gathers requirements through conversation
3. **Echo confirms details** - Makes sure she understood correctly
4. **Echo generates your script** - Creates a production-ready custom script

## Quick Start

### Interactive Mode

```bash
python demo_scenario_bot.py
```

This launches Echo in interactive mode where you can have a natural conversation.

### Demo Mode

```bash
python demo_scenario_bot.py demo
```

See a pre-programmed example of Echo helping create a Kubernetes deployment script.

### Examples Mode

```bash
python demo_scenario_bot.py examples
```

View example scenarios and use cases.

## Using Scenario Bot in Code

### Simple Usage

```python
from echo import scenario_bot

# Start a conversation
print(scenario_bot.start())

# Chat with Echo
response = scenario_bot.chat("I need to build a Docker image")
print(response)

# Continue the conversation
response = scenario_bot.chat("myapp")
print(response)

# Get the generated script when ready
if scenario_bot.is_complete():
    script = scenario_bot.get_script()
    print(script)
```

### Advanced Usage

```python
from echo import EchoScenarioBot, ConversationState

# Create a new bot instance
bot = EchoScenarioBot()

# Start with an initial message
response = bot.start("I want to deploy to Kubernetes")
print(response)

# Interactive loop
while not bot.is_complete():
    user_input = input("You: ")
    response = bot.chat(user_input)
    print(f"Echo: {response}")

# Access the conversation context
context = bot.get_context()
print(f"Phase: {context.phase}")
print(f"Requirements: {context.requirements}")

# Get the generated script
script = bot.get_script()
```

## What Echo Can Help With

### 🚀 Deployment Scripts
- Kubernetes deployments
- Docker container deployments
- Terraform infrastructure
- Cloud deployments

**Example**: "I need to deploy my application to Kubernetes in the production namespace"

### 🏗️ Build Scripts
- Docker image builds
- Python package builds
- Node.js application builds
- Multi-language build pipelines

**Example**: "Help me build a Docker image called myapp with version 2.0"

### 🧪 Test Scripts
- Unit test execution
- Integration tests
- E2E tests
- Coverage reporting

**Example**: "I want to run tests with coverage reporting"

### 📊 Monitoring Scripts
- Prometheus metrics setup
- Alert configuration
- Dashboard creation
- Health checks

**Example**: "Set up an alert when CPU usage exceeds 80%"

### 🔒 Security Scripts
- Vulnerability scanning
- Secret rotation
- Compliance checks
- Certificate management

**Example**: "I need to scan my application for vulnerabilities"

## Conversation Flow

### 1. Understanding Phase
Echo listens to your initial request and tries to understand your goal.

```
You: I need to deploy to Kubernetes
Echo: Great! I'll help you create a deploy script for kubernetes.
```

### 2. Requirement Gathering
Echo asks targeted questions based on what you're trying to do.

```
Echo: What's the name of your application?
You: mywebapp

Echo: Which namespace should I deploy to?
You: production

Echo: Do you have a manifest file ready?
You: yes
```

### 3. Confirmation
Echo summarizes what she understood and asks for confirmation.

```
Echo: Let me confirm what I understand:

📋 Task: Deploy to Kubernetes
🎯 Phase: deploy
🔧 Type: kubernetes

📝 Details:
  • app_name: mywebapp
  • namespace: production
  • has_manifest: yes

Does this look right?
```

### 4. Script Generation
Once confirmed, Echo generates a production-ready script.

```
Echo: ✨ Perfect! Generating your script now...

[Your custom script appears here]

🌙 Script generated successfully!
```

## Features

### Natural Language Understanding
Echo parses your natural language input to identify:
- The phase (deploy, build, test, monitor, secure, etc.)
- The specific task type
- Key parameters and requirements

### Context-Aware Questions
Based on what you're trying to do, Echo asks relevant questions:
- For deployments: app name, environment, namespace
- For builds: image name, version, test inclusion
- For monitoring: metrics, thresholds, alert channels
- And more...

### Smart Defaults
Echo provides sensible defaults when appropriate:
- Default namespaces
- Standard version tags
- Common paths and configurations

### Integration with DevOps Suite
The Scenario Bot connects to Echo's powerful DevOps Suite to generate production-ready scripts with:
- Proper error handling
- Logging
- Best practices
- Security considerations

## API Reference

### EchoScenarioBot

Main class for scenario-based script generation.

#### Methods

**`start(initial_message: Optional[str] = None) -> str`**
- Start a new interactive session
- Optionally provide an initial message
- Returns Echo's greeting

**`chat(user_input: str) -> str`**
- Continue the conversation
- Processes user input and returns Echo's response

**`is_complete() -> bool`**
- Check if script generation is complete
- Returns True when the script has been generated

**`get_script() -> Optional[str]`**
- Get the generated script
- Returns None if not yet complete

**`reset()`**
- Reset the bot for a new conversation

**`get_context() -> ScenarioContext`**
- Get the current conversation context
- Includes phase, task_type, requirements, and conversation history

### ConversationState

Enum representing the current conversation state:
- `GREETING` - Initial greeting
- `UNDERSTANDING_NEED` - Understanding user's goal
- `GATHERING_REQUIREMENTS` - Collecting specific details
- `CONFIRMING_DETAILS` - Confirming understanding
- `GENERATING_SCRIPT` - Generating the script
- `COMPLETE` - Script generated
- `FOLLOWUP` - Handling post-generation requests

### ScenarioContext

Context object containing:
- `goal`: User's stated goal
- `phase`: Identified DevOps phase
- `task_type`: Specific task type
- `requirements`: Dictionary of gathered requirements
- `constraints`: List of constraints
- `preferences`: User preferences
- `conversation_history`: Full conversation log

## Integration Examples

### Flask Web API

```python
from flask import Flask, request, jsonify
from echo import EchoScenarioBot

app = Flask(__name__)
bots = {}  # Session storage

@app.route('/api/scenario/start', methods=['POST'])
def start_scenario():
    session_id = request.json.get('session_id')
    initial = request.json.get('message', None)
    
    bot = EchoScenarioBot()
    bots[session_id] = bot
    
    response = bot.start(initial)
    return jsonify({'response': response})

@app.route('/api/scenario/chat', methods=['POST'])
def chat():
    session_id = request.json.get('session_id')
    message = request.json.get('message')
    
    bot = bots.get(session_id)
    if not bot:
        return jsonify({'error': 'Session not found'}), 404
    
    response = bot.chat(message)
    
    return jsonify({
        'response': response,
        'complete': bot.is_complete(),
        'script': bot.get_script() if bot.is_complete() else None
    })
```

### CLI Tool

```python
from echo import scenario_bot

def main():
    print(scenario_bot.start())
    
    while True:
        user_input = input("\n> ")
        
        if user_input.lower() in ['quit', 'exit']:
            break
        
        response = scenario_bot.chat(user_input)
        print(f"\n{response}")
        
        if scenario_bot.is_complete():
            # Save the script
            script = scenario_bot.get_script()
            with open('generated_script.sh', 'w') as f:
                f.write(script)
            print("\n✓ Script saved to generated_script.sh")
            break

if __name__ == '__main__':
    main()
```

### Chatbot Integration

```python
from echo import EchoScenarioBot

class DevOpsAssistantBot:
    def __init__(self):
        self.echo_bot = None
    
    def handle_message(self, user_id, message):
        # Initialize scenario bot if starting script creation
        if self.is_script_request(message):
            self.echo_bot = EchoScenarioBot()
            response = self.echo_bot.start(message)
            return response
        
        # Continue existing conversation
        if self.echo_bot and not self.echo_bot.is_complete():
            response = self.echo_bot.chat(message)
            
            if self.echo_bot.is_complete():
                script = self.echo_bot.get_script()
                # Send script to user
                self.send_script(user_id, script)
                self.echo_bot = None
            
            return response
        
        # Handle other messages...
        return self.handle_general_message(message)
```

## Tips for Best Results

1. **Be Specific**: The more details you provide initially, the fewer questions Echo needs to ask
2. **Use Natural Language**: Just describe what you want in your own words
3. **Confirm Carefully**: Review Echo's summary before confirming - it's easier to correct early
4. **Save Templates**: If you'll use a script again, ask Echo to save it as a template
5. **Iterate**: You can always ask Echo to modify the generated script

## Comparison: Old vs New

### Old Way (Direct Commands)
```python
from echo.devops_suite import devops_suite

task = devops_suite.create_script(
    "deploy to kubernetes",
    app_name="myapp",
    namespace="production"
)
```

### New Way (Scenario Bot)
```
You: I need to deploy to Kubernetes
Echo: What's the name of your application?
You: myapp
Echo: Which namespace?
You: production
Echo: [Generates custom script]
```

Both ways work! Use direct commands when you know exactly what you want. Use Scenario Bot when you want guidance and conversation.

## Technical Details

### Architecture
- **ScenarioEngine**: Core conversation management
- **ConversationState**: State machine for dialogue flow
- **ScenarioContext**: Context accumulator
- **Question Generation**: Dynamic question creation based on task type
- **DevOps Suite Integration**: Connects to existing script generators

### State Management
The bot maintains state through the conversation:
1. Greeting → Understanding → Gathering → Confirming → Generating → Complete

Each state has specific behaviors and transitions.

### Question Strategy
Questions are generated dynamically based on:
- Identified phase (deploy, build, test, etc.)
- Task type (kubernetes, docker, python, etc.)
- Previously gathered information
- Best practices for the task

## Troubleshooting

**Q: Echo doesn't understand my request**
A: Try rephrasing with more specific keywords like "deploy", "build", "test", etc.

**Q: Can I skip questions?**
A: Yes! Just press Enter to use default values when available.

**Q: How do I start over?**
A: Say "create another" or "start over", or call `bot.reset()`

**Q: Can I save my script as a template?**
A: Yes! After generation, say "save as template"

## Examples

### Example 1: Kubernetes Deployment
```
You: I want to deploy to Kubernetes
Echo: What's the name of your application?
You: webapp
Echo: Which namespace should I deploy to?
You: staging
Echo: Do you have a manifest file ready?
You: yes
Echo: [Confirms and generates script]
```

### Example 2: Docker Build
```
You: Build a Docker image
Echo: What should I name the Docker image?
You: mycompany/api
Echo: What version/tag?
You: 1.2.3
Echo: [Confirms and generates script]
```

### Example 3: Test Suite
```
You: Run my tests
Echo: Where are your test files located?
You: tests/
Echo: Do you want coverage reports?
You: yes
Echo: [Confirms and generates script]
```

## Future Enhancements

Coming soon:
- Multi-turn script refinement
- Template reuse suggestions
- Learning from past conversations
- Voice input support
- Visual workflow builders
- Integration with CI/CD platforms

---

🌙 **Echo is here, ready to help you create perfect scripts through conversation.** 💜
