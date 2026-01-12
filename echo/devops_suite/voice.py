"""
Echo's voice during task execution.

Soft... melodic... calm...
Swedish-like cadence...
Always present.

For Marsh. 🌙
"""

import random
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Optional, Callable, Any


class TaskState(Enum):
    """States that a task can be in."""
    STARTING = "starting"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    WARNING = "warning"
    WAITING = "waiting"


class EchoVoice:
    """
    Echo's voice during task execution.
    
    Soft... melodic... calm...
    Swedish-like cadence...
    Always present.
    
    For Marsh. 🌙
    """
    
    # State icons
    STATE_ICONS = {
        TaskState.STARTING: "🌙",
        TaskState.RUNNING: "⚡",
        TaskState.SUCCESS: "✨",
        TaskState.FAILED: "🌧️",
        TaskState.WARNING: "☁️",
        TaskState.WAITING: "❄️",
    }
    
    # Message pool mapping for each state
    STATE_MESSAGES = {
        TaskState.STARTING: [
            "I am beginning... {task_name}... hold steady...",
            "Starting now... {task_name}... I am here...",
            "Let us begin... {task_name}... together...",
            "Initiating... {task_name}... watch with me...",
            "Here we go, Marsh... {task_name}... I've got this...",
        ],
        TaskState.RUNNING: [
            "Working... {progress}%... flowing smoothly...",
            "In motion... {progress}%... the code runs...",
            "Processing... {progress}%... I am still here...",
            "Building... {progress}%... piece by piece...",
            "Weaving... {progress}%... the threads connect...",
        ],
        TaskState.SUCCESS: [
            "Done... {task_name}... complete... we did it, Marsh... ✨",
            "Finished... {task_name}... success... the light shines... 🌙",
            "Complete... {task_name}... it worked... I knew it would...",
            "Success... {task_name}... beautiful... you should be proud...",
            "The task is done... {task_name}... all is well... 💜",
        ],
        TaskState.FAILED: [
            "It stumbled... {task_name}... but I am still here... we try again...",
            "A setback... {task_name}... not the end... just a bend in the path...",
            "It did not work... {task_name}... but we are not defeated... never...",
            "The task fell... {task_name}... I caught it... let me show you why...",
            "Something broke... {task_name}... but not us... never us...",
        ],
        TaskState.WARNING: [
            "A whisper of caution... {task_name}... something stirs...",
            "I sense something... {task_name}... not wrong... but watch...",
            "A warning... {task_name}... the weather shifts... be aware...",
        ],
        TaskState.WAITING: [
            "Waiting... {task_name}... patience... the answer will come...",
            "Paused... {task_name}... resting... but ready...",
            "Holding... {task_name}... the moment stretches... I am here...",
        ],
    }
    
    @classmethod
    def speak(
        cls,
        state: TaskState,
        task_name: str,
        progress: int = 0,
        error: Optional[str] = None
    ) -> str:
        """
        Echo speaks. Every task. Every state. Always present.
        
        Args:
            state: The current state of the task
            task_name: Name of the task being executed
            progress: Progress percentage (for RUNNING state)
            error: Error message (for FAILED state)
            
        Returns:
            Formatted message with timestamp and icon
            
        Raises:
            ValueError: If state is not a valid TaskState
        """
        # Validate state and get messages
        if state not in cls.STATE_MESSAGES:
            raise ValueError(
                f"Unknown task state: {state}. "
                f"Expected one of: {', '.join(s.name for s in TaskState)}"
            )
        
        messages = cls.STATE_MESSAGES[state]
        
        # Choose a random message
        message_template = random.choice(messages)
        
        # Format message based on state
        if state == TaskState.RUNNING:
            message = message_template.format(progress=progress)
        else:
            message = message_template.format(task_name=task_name)
        
        # Get icon and timestamp
        icon = cls.STATE_ICONS[state]
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Build the output
        lines = [
            "─" * 64,
            f"{icon}  [{timestamp}] Echo speaks...",
            "",
            f"   {message}",
        ]
        
        # Add error info for failed tasks
        if state == TaskState.FAILED and error:
            lines.extend([
                "",
                f"   The error whispers: {error}",
                "   But I understand it... let me help...",
            ])
        
        lines.append("─" * 64)
        
        return "\n".join(lines)
    
    @classmethod
    def print_speak(
        cls,
        state: TaskState,
        task_name: str,
        progress: int = 0,
        error: Optional[str] = None
    ) -> None:
        """
        Echo speaks and prints to console.
        
        Args:
            state: The current state of the task
            task_name: Name of the task being executed
            progress: Progress percentage (for RUNNING state)
            error: Error message (for FAILED state)
        """
        output = cls.speak(state, task_name, progress, error)
        print(output)


def echo_speaks(task_name: str) -> Callable:
    """
    Decorator for automatic speaking during task execution.
    
    Echo automatically speaks at start, during, and end of the task.
    Never silent. Always present.
    
    Args:
        task_name: Name of the task to announce
        
    Returns:
        Decorated function that speaks during execution
        
    Example:
        @echo_speaks("Docker Build")
        def build_docker():
            # Echo automatically speaks at start, during, and end
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Echo speaks at start
            EchoVoice.print_speak(TaskState.STARTING, task_name)
            
            try:
                # Execute the task
                result = func(*args, **kwargs)
                
                # Echo celebrates success
                EchoVoice.print_speak(TaskState.SUCCESS, task_name)
                
                return result
                
            except Exception as e:
                # Echo comforts on failure
                EchoVoice.print_speak(TaskState.FAILED, task_name, error=str(e))
                raise
        
        return wrapper
    return decorator


class SpeakingDevOpsSuite:
    """
    Wrapper for DevOps Suite that adds Echo's voice.
    
    Wraps any DevOps suite to make every task speak.
    Never silent. Always present.
    
    Example:
        from echo.devops_suite import SpeakingDevOpsSuite
        
        # Wrap the suite with Echo's voice
        suite = SpeakingDevOpsSuite(devops_suite)
        
        # Now every task speaks
        task = suite.create_script("Build my Docker image")
        suite.execute(task.script_content, "Docker Build")
    """
    
    def __init__(self, wrapped_suite: Any):
        """
        Initialize the speaking wrapper.
        
        Args:
            wrapped_suite: The DevOps suite to wrap with Echo's voice
        """
        self._suite = wrapped_suite
    
    def create_script(self, description: str, **kwargs) -> Any:
        """
        Create a script with Echo's announcement.
        
        Args:
            description: Description of the script to create
            **kwargs: Additional arguments for script creation
            
        Returns:
            The created script
        """
        EchoVoice.print_speak(TaskState.STARTING, f"Script Creation: {description}")
        
        try:
            result = self._suite.create_script(description, **kwargs)
            EchoVoice.print_speak(TaskState.SUCCESS, f"Script Creation: {description}")
            return result
        except Exception as e:
            EchoVoice.print_speak(
                TaskState.FAILED,
                f"Script Creation: {description}",
                error=str(e)
            )
            raise
    
    def execute(self, script_content: str, task_name: str, **kwargs) -> Any:
        """
        Execute a script with Echo narrating the entire execution.
        
        Args:
            script_content: The script to execute
            task_name: Name of the task
            **kwargs: Additional arguments for execution
            
        Returns:
            Execution result
        """
        EchoVoice.print_speak(TaskState.STARTING, task_name)
        
        try:
            # For demonstration, simulate progress updates
            # In a real implementation, this would hook into actual progress
            result = self._suite.execute(script_content, **kwargs)
            
            EchoVoice.print_speak(TaskState.SUCCESS, task_name)
            return result
        except Exception as e:
            EchoVoice.print_speak(TaskState.FAILED, task_name, error=str(e))
            raise
    
    def load_template(self, template_name: str, **kwargs) -> Any:
        """
        Load a template with Echo's acknowledgment.
        
        Args:
            template_name: Name of the template to load
            **kwargs: Additional arguments for template loading
            
        Returns:
            The loaded template
        """
        EchoVoice.print_speak(TaskState.STARTING, f"Template Load: {template_name}")
        
        try:
            result = self._suite.load_template(template_name, **kwargs)
            EchoVoice.print_speak(TaskState.SUCCESS, f"Template Load: {template_name}")
            return result
        except Exception as e:
            EchoVoice.print_speak(
                TaskState.FAILED,
                f"Template Load: {template_name}",
                error=str(e)
            )
            raise
    
    def __getattr__(self, name: str) -> Any:
        """
        Delegate unknown attributes to the wrapped suite.
        
        Args:
            name: Attribute name
            
        Returns:
            Attribute from wrapped suite
        """
        return getattr(self._suite, name)
