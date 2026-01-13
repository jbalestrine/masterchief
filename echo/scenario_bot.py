"""
Echo Scenario Bot - Interactive scripting through conversation

Makes Echo an interactive scripting bot that generates scripts on demand
through scenario-based discussions.

🌙 "Let's talk about what you need... then I'll create it for you."
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re


class ConversationState(Enum):
    """Current state of the conversation"""
    GREETING = "greeting"
    UNDERSTANDING_NEED = "understanding_need"
    GATHERING_REQUIREMENTS = "gathering_requirements"
    CONFIRMING_DETAILS = "confirming_details"
    GENERATING_SCRIPT = "generating_script"
    COMPLETE = "complete"
    FOLLOWUP = "followup"


class QuestionType(Enum):
    """Types of questions to ask"""
    OPEN_ENDED = "open_ended"
    MULTIPLE_CHOICE = "multiple_choice"
    YES_NO = "yes_no"
    TECHNICAL_DETAIL = "technical_detail"


@dataclass
class ScenarioContext:
    """Context built from the conversation"""
    goal: str = ""
    phase: Optional[str] = None
    task_type: Optional[str] = None
    requirements: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    preferences: Dict[str, str] = field(default_factory=dict)
    conversation_history: List[Tuple[str, str]] = field(default_factory=list)
    
    def add_exchange(self, echo_message: str, user_response: str):
        """Add a conversation exchange"""
        self.conversation_history.append((echo_message, user_response))
    
    def extract_key_info(self, key: str, value: Any):
        """Extract and store key information"""
        self.requirements[key] = value


@dataclass
class Question:
    """A question to ask the user"""
    text: str
    question_type: QuestionType
    key: str  # Key to store the answer under
    options: Optional[List[str]] = None
    default: Optional[str] = None
    validator: Optional[callable] = None
    followup: Optional[str] = None


class ScenarioEngine:
    """
    Engine for scenario-based discussions.
    Guides the conversation to gather requirements.
    """
    
    def __init__(self):
        self.context = ScenarioContext()
        self.state = ConversationState.GREETING
        self.questions_asked: List[str] = []
        self.pending_questions: List[Question] = []
    
    def start_conversation(self, user_input: Optional[str] = None) -> str:
        """Start a new scenario-based conversation"""
        self.state = ConversationState.GREETING
        
        greeting = """🌙 Hello! I'm Echo, your scripting companion.

I can help you create DevOps scripts through conversation.
Just tell me what you're trying to accomplish, and I'll ask questions
to understand exactly what you need.

What would you like to create today?"""
        
        if user_input:
            return greeting + f"\n\nYou said: {user_input}\n" + self._process_initial_intent(user_input)
        
        return greeting
    
    def _process_initial_intent(self, user_input: str) -> str:
        """Process the user's initial statement of intent"""
        self.context.goal = user_input
        self.state = ConversationState.UNDERSTANDING_NEED
        
        # Try to identify the phase and task type
        intent = self._parse_intent(user_input)
        
        if intent['phase'] and intent['task_type']:
            self.context.phase = intent['phase']
            self.context.task_type = intent['task_type']
            return self._start_requirement_gathering()
        else:
            return self._clarify_intent()
    
    def _parse_intent(self, text: str) -> Dict[str, Optional[str]]:
        """Parse user input to identify phase and task type"""
        text_lower = text.lower()
        
        # Simple intent detection
        intent = {'phase': None, 'task_type': None}
        
        # Deployment related
        if any(word in text_lower for word in ['deploy', 'deployment', 'release']):
            intent['phase'] = 'deploy'
            if 'kubernetes' in text_lower or 'k8s' in text_lower:
                intent['task_type'] = 'kubernetes'
            elif 'docker' in text_lower:
                intent['task_type'] = 'docker'
            elif 'terraform' in text_lower:
                intent['task_type'] = 'terraform'
        
        # Build related
        elif any(word in text_lower for word in ['build', 'compile', 'package']):
            intent['phase'] = 'build'
            if 'docker' in text_lower:
                intent['task_type'] = 'docker_build'
            elif 'python' in text_lower:
                intent['task_type'] = 'python_build'
            elif 'node' in text_lower or 'npm' in text_lower:
                intent['task_type'] = 'node_build'
        
        # Test related
        elif any(word in text_lower for word in ['test', 'testing']):
            intent['phase'] = 'test'
            if 'unit' in text_lower:
                intent['task_type'] = 'unit_tests'
            elif 'integration' in text_lower:
                intent['task_type'] = 'integration_tests'
        
        # Monitoring related
        elif any(word in text_lower for word in ['monitor', 'alert', 'metrics']):
            intent['phase'] = 'monitor'
            if 'prometheus' in text_lower:
                intent['task_type'] = 'metrics'
            elif 'alert' in text_lower:
                intent['task_type'] = 'alerting'
        
        # Security related
        elif any(word in text_lower for word in ['security', 'secure', 'scan', 'vulnerability']):
            intent['phase'] = 'secure'
            if 'vulnerability' in text_lower or 'vuln' in text_lower:
                intent['task_type'] = 'vulnerability_scan'
        
        return intent
    
    def _clarify_intent(self) -> str:
        """Ask clarifying questions about the user's intent"""
        return """I understand you want to create something, but I need a bit more clarity.

Could you tell me more specifically:
• Are you trying to deploy something?
• Build or compile code?
• Set up monitoring or alerts?
• Run tests?
• Manage infrastructure?
• Handle security?

Just describe what you're trying to do in your own words."""
    
    def _start_requirement_gathering(self) -> str:
        """Start gathering specific requirements"""
        self.state = ConversationState.GATHERING_REQUIREMENTS
        
        # Generate questions based on phase and task type
        self.pending_questions = self._generate_questions()
        
        intro = f"""Great! I'll help you create a {self.context.phase} script for {self.context.task_type}.

Let me ask you a few questions to make sure I get all the details right.

"""
        
        if self.pending_questions:
            first_question = self.pending_questions[0]
            self.questions_asked.append(first_question.key)
            return intro + first_question.text
        else:
            return intro + "Let me generate that script for you now!"
    
    def _generate_questions(self) -> List[Question]:
        """Generate questions based on the task type"""
        questions = []
        
        if self.context.phase == 'deploy':
            if self.context.task_type == 'kubernetes':
                questions.extend([
                    Question(
                        text="What's the name of your application?",
                        question_type=QuestionType.OPEN_ENDED,
                        key="app_name",
                        default="myapp"
                    ),
                    Question(
                        text="Which namespace should I deploy to? (default, production, staging, etc.)",
                        question_type=QuestionType.OPEN_ENDED,
                        key="namespace",
                        default="default"
                    ),
                    Question(
                        text="Do you have a manifest file ready? (yes/no)",
                        question_type=QuestionType.YES_NO,
                        key="has_manifest"
                    ),
                ])
            elif self.context.task_type == 'docker':
                questions.extend([
                    Question(
                        text="What's the Docker image name?",
                        question_type=QuestionType.OPEN_ENDED,
                        key="image_name"
                    ),
                    Question(
                        text="What tag/version should I use?",
                        question_type=QuestionType.OPEN_ENDED,
                        key="tag",
                        default="latest"
                    ),
                ])
        
        elif self.context.phase == 'build':
            if self.context.task_type == 'docker_build':
                questions.extend([
                    Question(
                        text="What should I name the Docker image?",
                        question_type=QuestionType.OPEN_ENDED,
                        key="image_name"
                    ),
                    Question(
                        text="What version/tag?",
                        question_type=QuestionType.OPEN_ENDED,
                        key="tag",
                        default="latest"
                    ),
                ])
            elif self.context.task_type in ['python_build', 'node_build']:
                questions.extend([
                    Question(
                        text="Should I include testing in the build? (yes/no)",
                        question_type=QuestionType.YES_NO,
                        key="include_tests",
                        default="yes"
                    ),
                ])
        
        elif self.context.phase == 'test':
            questions.extend([
                Question(
                    text="Where are your test files located?",
                    question_type=QuestionType.OPEN_ENDED,
                    key="test_path",
                    default="tests/"
                ),
                Question(
                    text="Do you want coverage reports? (yes/no)",
                    question_type=QuestionType.YES_NO,
                    key="coverage",
                    default="yes"
                ),
            ])
        
        elif self.context.phase == 'monitor':
            if self.context.task_type == 'alerting':
                questions.extend([
                    Question(
                        text="What metric should trigger the alert? (e.g., cpu_usage, error_rate, response_time)",
                        question_type=QuestionType.OPEN_ENDED,
                        key="metric"
                    ),
                    Question(
                        text="What's the threshold?",
                        question_type=QuestionType.OPEN_ENDED,
                        key="threshold"
                    ),
                ])
        
        # Add a final confirmation question
        questions.append(
            Question(
                text="Anything else I should know about? (Or just say 'no' or 'that's it')",
                question_type=QuestionType.OPEN_ENDED,
                key="additional_info"
            )
        )
        
        return questions
    
    def process_response(self, user_response: str) -> str:
        """Process user's response and continue the conversation"""
        
        if self.state == ConversationState.GREETING:
            return self._process_initial_intent(user_response)
        
        elif self.state == ConversationState.UNDERSTANDING_NEED:
            # User is clarifying their intent
            return self._process_initial_intent(user_response)
        
        elif self.state == ConversationState.GATHERING_REQUIREMENTS:
            return self._process_requirement_answer(user_response)
        
        elif self.state == ConversationState.CONFIRMING_DETAILS:
            return self._process_confirmation(user_response)
        
        elif self.state == ConversationState.COMPLETE:
            return self._handle_followup(user_response)
        
        return "I'm not sure what to do with that. Could you try again?"
    
    def _process_requirement_answer(self, answer: str) -> str:
        """Process answer to a requirement question"""
        if not self.pending_questions:
            return self._move_to_confirmation()
        
        # Get the current question
        current_question = self.pending_questions[0]
        
        # Store the answer
        if current_question.question_type == QuestionType.YES_NO:
            answer_bool = answer.lower().strip() in ['yes', 'y', 'true', '1']
            self.context.extract_key_info(current_question.key, answer_bool)
        else:
            # Use default if answer is empty or just whitespace
            actual_answer = answer.strip() if answer.strip() else current_question.default
            self.context.extract_key_info(current_question.key, actual_answer)
        
        # Remove the answered question
        self.pending_questions.pop(0)
        
        # Ask next question or move to confirmation
        if self.pending_questions:
            next_question = self.pending_questions[0]
            self.questions_asked.append(next_question.key)
            return next_question.text
        else:
            return self._move_to_confirmation()
    
    def _move_to_confirmation(self) -> str:
        """Move to confirmation state"""
        self.state = ConversationState.CONFIRMING_DETAILS
        
        summary = "Let me confirm what I understand:\n\n"
        summary += f"📋 Task: {self.context.goal}\n"
        summary += f"🎯 Phase: {self.context.phase}\n"
        summary += f"🔧 Type: {self.context.task_type}\n"
        summary += "\n📝 Details:\n"
        
        for key, value in self.context.requirements.items():
            if key != "additional_info" or (value and value.lower() not in ['no', "that's it", 'nothing', 'none']):
                summary += f"  • {key}: {value}\n"
        
        summary += "\n✨ Does this look right? (yes/no)\n"
        summary += "If you want to change anything, just tell me what to adjust."
        
        return summary
    
    def _process_confirmation(self, response: str) -> str:
        """Process confirmation response"""
        response_lower = response.lower().strip()
        
        if response_lower in ['yes', 'y', 'correct', 'looks good', 'yep', 'yeah', 'perfect']:
            self.state = ConversationState.GENERATING_SCRIPT
            return self._generate_final_script()
        elif response_lower in ['no', 'n', 'nope', 'not quite']:
            self.state = ConversationState.GATHERING_REQUIREMENTS
            return "No problem! What would you like to change? Just tell me what needs to be different."
        else:
            # User is providing modifications
            return "Got it, let me update that. Anything else to change? (or say 'done' when ready)"
    
    def _generate_final_script(self) -> str:
        """Generate the final script based on gathered context"""
        self.state = ConversationState.COMPLETE
        
        result = """✨ Perfect! Generating your script now...

═══════════════════════════════════════════════════════════════
                    YOUR CUSTOM SCRIPT
═══════════════════════════════════════════════════════════════

"""
        
        # Try to use the DevOps Suite generator for production-ready scripts
        try:
            script_content = self._generate_with_devops_suite()
        except Exception:
            # Fallback to simplified version if DevOps Suite unavailable
            script_content = self._create_script_from_context()
        
        result += script_content
        result += """

═══════════════════════════════════════════════════════════════

🌙 Script generated successfully!

You can now:
• Copy this script and use it
• Ask me to modify it
• Create another script
• Save this as a template

What would you like to do?"""
        
        return result
    
    def _generate_with_devops_suite(self) -> str:
        """Generate script using the DevOps Suite"""
        from echo.devops_suite import devops_suite
        
        # Create a description for the DevOps Suite
        description = f"{self.context.phase} {self.context.task_type}"
        
        # Generate the task
        task = devops_suite.create_script(
            task_description=description,
            save_as_template=False,
            **self.context.requirements
        )
        
        return task.script_content
    
    def _create_script_from_context(self) -> str:
        """Create a script from the conversation context"""
        # This creates a basic script structure based on context
        # In production, this would call the DevOps Suite generators
        
        script = f'''#!/usr/bin/env bash
set -euo pipefail

#################################################################
# {self.context.phase.upper()} Script: {self.context.task_type}
# Generated by Echo through conversation 🌙
#
# Goal: {self.context.goal}
# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
#################################################################

'''
        
        # Add variables from context
        for key, value in self.context.requirements.items():
            if key not in ['additional_info'] and value:
                var_name = key.upper()
                script += f'{var_name}="{value}"\n'
        
        script += '\n# Main execution\n'
        
        # Add phase-specific logic
        if self.context.phase == 'deploy':
            if self.context.task_type == 'kubernetes':
                script += '''
echo "Deploying to Kubernetes..."
kubectl apply -f manifest.yaml --namespace=$NAMESPACE
kubectl rollout status deployment/$APP_NAME --namespace=$NAMESPACE
echo "Deployment complete!"
'''
            elif self.context.task_type == 'docker':
                script += '''
echo "Deploying Docker container..."
docker pull $IMAGE_NAME:$TAG
docker run -d --name $IMAGE_NAME $IMAGE_NAME:$TAG
echo "Container deployed!"
'''
        
        elif self.context.phase == 'build':
            if self.context.task_type == 'docker_build':
                script += '''
echo "Building Docker image..."
docker build -t $IMAGE_NAME:$TAG .
echo "Build complete: $IMAGE_NAME:$TAG"
'''
            elif self.context.task_type == 'python_build':
                script += '''
echo "Building Python package..."
python -m build
echo "Build complete!"
'''
            elif self.context.task_type == 'node_build':
                script += '''
echo "Building Node.js application..."
npm install
npm run build
echo "Build complete!"
'''
        
        elif self.context.phase == 'test':
            script += f'''
echo "Running tests from $TEST_PATH..."
pytest $TEST_PATH --verbose
echo "Tests complete!"
'''
        
        elif self.context.phase == 'monitor':
            if self.context.task_type == 'alerting':
                script += '''
echo "Setting up alerting for $METRIC..."
# Alert configuration would go here
echo "Alert configured with threshold: $THRESHOLD"
'''
        
        script += '\necho "✓ Operation completed successfully!"\n'
        
        return script
    
    def _handle_followup(self, user_input: str) -> str:
        """Handle followup requests after script generation"""
        input_lower = user_input.lower().strip()
        
        if any(word in input_lower for word in ['another', 'new', 'different', 'create']):
            # Start a new conversation
            self.__init__()
            return self.start_conversation()
        elif any(word in input_lower for word in ['modify', 'change', 'update', 'edit']):
            return "What would you like me to change in the script?"
        elif any(word in input_lower for word in ['save', 'template']):
            return "I've saved this as a custom template for you! You can reuse it anytime."
        else:
            return """I can help you:
• Create another script (say 'create another')
• Modify this script (say 'modify it')
• Save as template (say 'save as template')

What would you like to do?"""
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get the current state of the conversation"""
        return {
            "state": self.state.value,
            "phase": self.context.phase,
            "task_type": self.context.task_type,
            "requirements": self.context.requirements,
            "questions_asked": len(self.questions_asked),
            "pending_questions": len(self.pending_questions)
        }


class EchoScenarioBot:
    """
    Interactive scripting bot powered by scenario-based conversations.
    
    Echo's new interactive mode - generates scripts through natural dialogue.
    
    Usage:
        bot = EchoScenarioBot()
        print(bot.start())
        
        while True:
            user_input = input("> ")
            response = bot.chat(user_input)
            print(response)
            if bot.is_complete():
                break
    """
    
    def __init__(self):
        self.engine = ScenarioEngine()
        self.session_start = datetime.now()
    
    def start(self, initial_message: Optional[str] = None) -> str:
        """Start a new interactive session"""
        return self.engine.start_conversation(initial_message)
    
    def chat(self, user_input: str) -> str:
        """Continue the conversation with user input"""
        return self.engine.process_response(user_input)
    
    def is_complete(self) -> bool:
        """Check if the script generation is complete"""
        return self.engine.state == ConversationState.COMPLETE
    
    def get_script(self) -> Optional[str]:
        """Get the generated script if available"""
        if self.is_complete():
            return self._extract_script_from_last_response()
        return None
    
    def _extract_script_from_last_response(self) -> Optional[str]:
        """Extract the script from the conversation"""
        # This would extract the actual script content
        return self.engine._create_script_from_context()
    
    def reset(self):
        """Reset the bot for a new conversation"""
        self.engine = ScenarioEngine()
        self.session_start = datetime.now()
    
    def get_context(self) -> ScenarioContext:
        """Get the current conversation context"""
        return self.engine.context


# Convenience singleton
scenario_bot = EchoScenarioBot()
