#!/usr/bin/env python3
"""
Simple test runner for Echo Voice System tests (without pytest).
This avoids the platform module conflict in the repository.
"""

import sys
sys.path.insert(0, '/home/runner/work/masterchief/masterchief')

from unittest.mock import Mock
from echo.devops_suite.voice import (
    TaskState,
    EchoVoice,
    echo_speaks,
    SpeakingDevOpsSuite,
)


class TestRunner:
    """Simple test runner."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name):
        """Decorator for test functions."""
        def decorator(func):
            self.tests.append((name, func))
            return func
        return decorator
    
    def run(self):
        """Run all tests."""
        print("\n" + "=" * 64)
        print("Running Echo Voice System Tests")
        print("=" * 64 + "\n")
        
        for name, func in self.tests:
            try:
                func()
                self.passed += 1
                print(f"✅ {name}")
            except AssertionError as e:
                self.failed += 1
                print(f"❌ {name}: {e}")
            except Exception as e:
                self.failed += 1
                print(f"❌ {name}: Unexpected error: {e}")
        
        print("\n" + "=" * 64)
        print(f"Results: {self.passed} passed, {self.failed} failed")
        print("=" * 64 + "\n")
        
        return self.failed == 0


runner = TestRunner()


@runner.test("TaskState enum has all required states")
def test_task_state_values():
    assert TaskState.STARTING.value == "starting"
    assert TaskState.RUNNING.value == "running"
    assert TaskState.SUCCESS.value == "success"
    assert TaskState.FAILED.value == "failed"
    assert TaskState.WARNING.value == "warning"
    assert TaskState.WAITING.value == "waiting"


@runner.test("All states have icons")
def test_state_icons_exist():
    for state in TaskState:
        assert state in EchoVoice.STATE_ICONS


@runner.test("Echo speaks for STARTING state")
def test_speak_starting():
    output = EchoVoice.speak(TaskState.STARTING, "Docker Build")
    assert "🌙" in output
    assert "Echo speaks..." in output
    assert "Docker Build" in output
    assert "─" * 64 in output


@runner.test("Echo speaks for RUNNING state with progress")
def test_speak_running():
    output = EchoVoice.speak(TaskState.RUNNING, "Deployment", progress=50)
    assert "⚡" in output
    assert "Echo speaks..." in output
    assert "50%" in output
    assert "─" * 64 in output


@runner.test("Echo speaks for SUCCESS state")
def test_speak_success():
    output = EchoVoice.speak(TaskState.SUCCESS, "Build Complete")
    assert "✨" in output
    assert "Echo speaks..." in output
    assert "Build Complete" in output


@runner.test("Echo speaks for FAILED state with error")
def test_speak_failed():
    error_msg = "Connection refused to cluster"
    output = EchoVoice.speak(TaskState.FAILED, "Deployment", error=error_msg)
    assert "🌧️" in output
    assert "Echo speaks..." in output
    assert "Deployment" in output
    assert error_msg in output
    assert "The error whispers:" in output


@runner.test("Echo speaks for WARNING state")
def test_speak_warning():
    output = EchoVoice.speak(TaskState.WARNING, "Health Check")
    assert "☁️" in output
    assert "Health Check" in output


@runner.test("Echo speaks for WAITING state")
def test_speak_waiting():
    output = EchoVoice.speak(TaskState.WAITING, "Database Backup")
    assert "❄️" in output
    assert "Database Backup" in output


@runner.test("Echo's speech includes timestamp")
def test_speak_includes_timestamp():
    output = EchoVoice.speak(TaskState.STARTING, "Test")
    assert "[" in output
    assert "]" in output
    assert ":" in output


@runner.test("Decorator preserves function metadata")
def test_decorator_preserves_metadata():
    @echo_speaks("Test")
    def example_func():
        """Example docstring."""
        pass
    
    assert example_func.__name__ == "example_func"
    assert example_func.__doc__ == "Example docstring."


@runner.test("Decorator works with function arguments")
def test_decorator_with_arguments():
    @echo_speaks("Math Task")
    def add_numbers(a, b):
        return a + b
    
    result = add_numbers(2, 3)
    assert result == 5


@runner.test("SpeakingDevOpsSuite.create_script works")
def test_suite_create_script():
    mock_suite = Mock()
    mock_suite.create_script.return_value = {"status": "created"}
    
    speaking_suite = SpeakingDevOpsSuite(mock_suite)
    result = speaking_suite.create_script("Build Docker image")
    
    assert result == {"status": "created"}
    mock_suite.create_script.assert_called_once_with("Build Docker image")


@runner.test("SpeakingDevOpsSuite.execute works")
def test_suite_execute():
    mock_suite = Mock()
    mock_suite.execute.return_value = {"status": "executed"}
    
    speaking_suite = SpeakingDevOpsSuite(mock_suite)
    result = speaking_suite.execute("#!/bin/bash\necho hello", "Docker Build")
    
    assert result == {"status": "executed"}


@runner.test("SpeakingDevOpsSuite.load_template works")
def test_suite_load_template():
    mock_suite = Mock()
    mock_suite.load_template.return_value = {"template": "loaded"}
    
    speaking_suite = SpeakingDevOpsSuite(mock_suite)
    result = speaking_suite.load_template("docker-compose.yml")
    
    assert result == {"template": "loaded"}


@runner.test("SpeakingDevOpsSuite delegates unknown attributes")
def test_suite_delegates():
    mock_suite = Mock()
    mock_suite.some_method.return_value = "result"
    mock_suite.some_property = "value"
    
    speaking_suite = SpeakingDevOpsSuite(mock_suite)
    
    assert speaking_suite.some_method() == "result"
    assert speaking_suite.some_property == "value"


@runner.test("Messages are randomized")
def test_messages_are_random():
    outputs = [EchoVoice.speak(TaskState.STARTING, "Test") for _ in range(10)]
    unique_outputs = set(outputs)
    # With 5 messages and 10 tries, should get at least 2 different ones
    assert len(unique_outputs) >= 2


if __name__ == "__main__":
    success = runner.run()
    sys.exit(0 if success else 1)
