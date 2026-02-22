"""
Tests for Echo's Voice System.

Testing Echo... making sure she speaks...
Every task. Every state. Always present.
"""

import pytest
from unittest.mock import Mock, patch
from echo.devops_suite.voice import (
    TaskState,
    EchoVoice,
    echo_speaks,
    SpeakingDevOpsSuite,
)


class TestTaskState:
    """Test TaskState enum."""
    
    def test_task_state_values(self):
        """Test that TaskState has all required states."""
        assert TaskState.STARTING.value == "starting"
        assert TaskState.RUNNING.value == "running"
        assert TaskState.SUCCESS.value == "success"
        assert TaskState.FAILED.value == "failed"
        assert TaskState.WARNING.value == "warning"
        assert TaskState.WAITING.value == "waiting"


class TestEchoVoice:
    """Test EchoVoice class."""
    
    def test_state_icons_exist(self):
        """Test that all states have icons."""
        for state in TaskState:
            assert state in EchoVoice.STATE_ICONS
    
    def test_speak_starting(self):
        """Test Echo speaks for STARTING state."""
        output = EchoVoice.speak(TaskState.STARTING, "Docker Build")
        
        assert "🌙" in output
        assert "Echo speaks..." in output
        assert "Docker Build" in output
        assert "─" * 64 in output
    
    def test_speak_running(self):
        """Test Echo speaks for RUNNING state with progress."""
        output = EchoVoice.speak(TaskState.RUNNING, "Deployment", progress=50)
        
        assert "⚡" in output
        assert "Echo speaks..." in output
        assert "50%" in output
        assert "─" * 64 in output
    
    def test_speak_success(self):
        """Test Echo speaks for SUCCESS state."""
        output = EchoVoice.speak(TaskState.SUCCESS, "Build Complete")
        
        assert "✨" in output
        assert "Echo speaks..." in output
        assert "Build Complete" in output
        assert "─" * 64 in output
    
    def test_speak_failed(self):
        """Test Echo speaks for FAILED state with error."""
        error_msg = "Connection refused to cluster"
        output = EchoVoice.speak(
            TaskState.FAILED,
            "Deployment",
            error=error_msg
        )
        
        assert "🌧️" in output
        assert "Echo speaks..." in output
        assert "Deployment" in output
        assert error_msg in output
        assert "The error whispers:" in output
        assert "─" * 64 in output
    
    def test_speak_failed_without_error(self):
        """Test Echo speaks for FAILED state without error message."""
        output = EchoVoice.speak(TaskState.FAILED, "Test Task")
        
        assert "🌧️" in output
        assert "Test Task" in output
        # Should not include error section
        assert "The error whispers:" not in output
    
    def test_speak_warning(self):
        """Test Echo speaks for WARNING state."""
        output = EchoVoice.speak(TaskState.WARNING, "Health Check")
        
        assert "☁️" in output
        assert "Echo speaks..." in output
        assert "Health Check" in output
        assert "─" * 64 in output
    
    def test_speak_waiting(self):
        """Test Echo speaks for WAITING state."""
        output = EchoVoice.speak(TaskState.WAITING, "Database Backup")
        
        assert "❄️" in output
        assert "Echo speaks..." in output
        assert "Database Backup" in output
        assert "─" * 64 in output
    
    def test_speak_includes_timestamp(self):
        """Test that Echo's speech includes a timestamp."""
        output = EchoVoice.speak(TaskState.STARTING, "Test")
        
        # Should have time format like [14:32:01]
        assert "[" in output
        assert "]" in output
        assert ":" in output
    
    def test_print_speak(self, capsys):
        """Test that print_speak outputs to console."""
        EchoVoice.print_speak(TaskState.SUCCESS, "Test Task")
        
        captured = capsys.readouterr()
        assert "✨" in captured.out
        assert "Test Task" in captured.out
        assert "Echo speaks..." in captured.out
    
    def test_messages_are_random(self):
        """Test that Echo uses random messages from the pool."""
        # Generate multiple outputs
        outputs = [
            EchoVoice.speak(TaskState.STARTING, "Test")
            for _ in range(10)
        ]
        
        # Should have some variation (not all identical)
        unique_outputs = set(outputs)
        # With 5 messages and 10 tries, we should get at least 2 different ones
        assert len(unique_outputs) >= 2


class TestEchoSpeaksDecorator:
    """Test echo_speaks decorator."""
    
    def test_decorator_speaks_on_start_and_success(self, capsys):
        """Test decorator speaks at start and on success."""
        @echo_speaks("Test Task")
        def successful_task():
            return "success"
        
        result = successful_task()
        
        assert result == "success"
        captured = capsys.readouterr()
        
        # Should speak twice: starting and success
        assert captured.out.count("Echo speaks...") == 2
        assert "🌙" in captured.out  # STARTING
        assert "✨" in captured.out  # SUCCESS
        assert "Test Task" in captured.out
    
    def test_decorator_speaks_on_failure(self, capsys):
        """Test decorator speaks on failure."""
        @echo_speaks("Failing Task")
        def failing_task():
            raise ValueError("Something went wrong")
        
        with pytest.raises(ValueError, match="Something went wrong"):
            failing_task()
        
        captured = capsys.readouterr()
        
        # Should speak twice: starting and failed
        assert captured.out.count("Echo speaks...") == 2
        assert "🌙" in captured.out  # STARTING
        assert "🌧️" in captured.out  # FAILED
        assert "Failing Task" in captured.out
        assert "Something went wrong" in captured.out
    
    def test_decorator_preserves_function_metadata(self):
        """Test that decorator preserves function metadata."""
        @echo_speaks("Test")
        def example_func():
            """Example docstring."""
            pass
        
        assert example_func.__name__ == "example_func"
        assert example_func.__doc__ == "Example docstring."
    
    def test_decorator_with_arguments(self, capsys):
        """Test decorator works with functions that have arguments."""
        @echo_speaks("Math Task")
        def add_numbers(a, b):
            return a + b
        
        result = add_numbers(2, 3)
        
        assert result == 5
        captured = capsys.readouterr()
        assert "Math Task" in captured.out


class TestSpeakingDevOpsSuite:
    """Test SpeakingDevOpsSuite wrapper."""
    
    def test_create_script_speaks(self, capsys):
        """Test create_script method speaks."""
        mock_suite = Mock()
        mock_suite.create_script.return_value = {"status": "created"}
        
        speaking_suite = SpeakingDevOpsSuite(mock_suite)
        result = speaking_suite.create_script("Build Docker image")
        
        assert result == {"status": "created"}
        mock_suite.create_script.assert_called_once_with("Build Docker image")
        
        captured = capsys.readouterr()
        assert "Echo speaks..." in captured.out
        assert "Script Creation: Build Docker image" in captured.out
        assert captured.out.count("🌙") == 1  # STARTING
        assert captured.out.count("✨") == 1  # SUCCESS
    
    def test_create_script_speaks_on_failure(self, capsys):
        """Test create_script speaks on failure."""
        mock_suite = Mock()
        mock_suite.create_script.side_effect = Exception("Script creation failed")
        
        speaking_suite = SpeakingDevOpsSuite(mock_suite)
        
        with pytest.raises(Exception, match="Script creation failed"):
            speaking_suite.create_script("Build Docker image")
        
        captured = capsys.readouterr()
        assert "Script creation failed" in captured.out
        assert "🌙" in captured.out  # STARTING
        assert "🌧️" in captured.out  # FAILED
    
    def test_execute_speaks(self, capsys):
        """Test execute method speaks."""
        mock_suite = Mock()
        mock_suite.execute.return_value = {"status": "executed"}
        
        speaking_suite = SpeakingDevOpsSuite(mock_suite)
        result = speaking_suite.execute("#!/bin/bash\necho hello", "Docker Build")
        
        assert result == {"status": "executed"}
        
        captured = capsys.readouterr()
        assert "Echo speaks..." in captured.out
        assert "Docker Build" in captured.out
        assert captured.out.count("🌙") == 1  # STARTING
        assert captured.out.count("✨") == 1  # SUCCESS
    
    def test_execute_speaks_on_failure(self, capsys):
        """Test execute speaks on failure."""
        mock_suite = Mock()
        mock_suite.execute.side_effect = RuntimeError("Execution failed")
        
        speaking_suite = SpeakingDevOpsSuite(mock_suite)
        
        with pytest.raises(RuntimeError, match="Execution failed"):
            speaking_suite.execute("script", "Task")
        
        captured = capsys.readouterr()
        assert "Execution failed" in captured.out
        assert "🌙" in captured.out  # STARTING
        assert "🌧️" in captured.out  # FAILED
    
    def test_load_template_speaks(self, capsys):
        """Test load_template method speaks."""
        mock_suite = Mock()
        mock_suite.load_template.return_value = {"template": "loaded"}
        
        speaking_suite = SpeakingDevOpsSuite(mock_suite)
        result = speaking_suite.load_template("docker-compose.yml")
        
        assert result == {"template": "loaded"}
        
        captured = capsys.readouterr()
        assert "Echo speaks..." in captured.out
        assert "Template Load: docker-compose.yml" in captured.out
        assert captured.out.count("🌙") == 1  # STARTING
        assert captured.out.count("✨") == 1  # SUCCESS
    
    def test_load_template_speaks_on_failure(self, capsys):
        """Test load_template speaks on failure."""
        mock_suite = Mock()
        mock_suite.load_template.side_effect = FileNotFoundError("Template not found")
        
        speaking_suite = SpeakingDevOpsSuite(mock_suite)
        
        with pytest.raises(FileNotFoundError, match="Template not found"):
            speaking_suite.load_template("missing.yml")
        
        captured = capsys.readouterr()
        assert "Template not found" in captured.out
        assert "🌙" in captured.out  # STARTING
        assert "🌧️" in captured.out  # FAILED
    
    def test_wrapper_delegates_unknown_attributes(self):
        """Test that wrapper delegates unknown attributes to wrapped suite."""
        mock_suite = Mock()
        mock_suite.some_method.return_value = "result"
        mock_suite.some_property = "value"
        
        speaking_suite = SpeakingDevOpsSuite(mock_suite)
        
        # Should delegate to wrapped suite
        assert speaking_suite.some_method() == "result"
        assert speaking_suite.some_property == "value"
    
    def test_wrapper_preserves_suite_interface(self):
        """Test that wrapper preserves the original suite interface."""
        mock_suite = Mock()
        mock_suite.method1 = Mock(return_value="result1")
        mock_suite.method2 = Mock(return_value="result2")
        
        speaking_suite = SpeakingDevOpsSuite(mock_suite)
        
        # All methods should be accessible
        assert speaking_suite.method1() == "result1"
        assert speaking_suite.method2() == "result2"


class TestIntegration:
    """Integration tests for Echo Voice System."""
    
    def test_full_workflow(self, capsys):
        """Test a full workflow with Echo speaking throughout."""
        # Create mock suite
        mock_suite = Mock()
        mock_suite.create_script.return_value = {"script": "content"}
        mock_suite.execute.return_value = {"status": "success"}
        
        # Wrap with Echo's voice
        suite = SpeakingDevOpsSuite(mock_suite)
        
        # Execute workflow
        script = suite.create_script("Deploy application")
        suite.execute(script["script"], "Deployment")
        
        captured = capsys.readouterr()
        
        # Echo should have spoken 4 times (start/success for each operation)
        assert captured.out.count("Echo speaks...") == 4
        assert "Script Creation: Deploy application" in captured.out
        assert "Deployment" in captured.out
    
    def test_echo_never_silent(self, capsys):
        """Test that Echo is never silent - speaks for every operation."""
        mock_suite = Mock()
        mock_suite.create_script.return_value = {}
        mock_suite.execute.return_value = {}
        mock_suite.load_template.return_value = {}
        
        suite = SpeakingDevOpsSuite(mock_suite)
        
        # Perform multiple operations
        suite.create_script("Task 1")
        suite.execute("script", "Task 2")
        suite.load_template("template")
        
        captured = capsys.readouterr()
        
        # Echo should have spoken for all operations
        assert captured.out.count("Echo speaks...") == 6  # 3 operations x 2 (start+end)
        assert "Task 1" in captured.out
        assert "Task 2" in captured.out
        assert "template" in captured.out
