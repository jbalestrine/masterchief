"""
Unit tests for Echo Scenario Bot
"""

import sys
sys.path.insert(0, '/home/runner/work/masterchief/masterchief')

from echo.scenario_bot import (
    EchoScenarioBot,
    ScenarioEngine,
    ScenarioContext,
    ConversationState,
    QuestionType,
    Question
)


def test_scenario_context():
    """Test ScenarioContext"""
    context = ScenarioContext()
    
    # Test initialization
    assert context.goal == ""
    assert context.phase is None
    assert context.task_type is None
    assert len(context.requirements) == 0
    assert len(context.conversation_history) == 0
    
    # Test adding exchanges
    context.add_exchange("Echo: Hello", "User: Hi")
    assert len(context.conversation_history) == 1
    assert context.conversation_history[0] == ("Echo: Hello", "User: Hi")
    
    # Test extracting key info
    context.extract_key_info("app_name", "myapp")
    assert context.requirements["app_name"] == "myapp"
    
    print("✓ test_scenario_context passed")


def test_question_creation():
    """Test Question dataclass"""
    question = Question(
        text="What's your app name?",
        question_type=QuestionType.OPEN_ENDED,
        key="app_name",
        default="myapp"
    )
    
    assert question.text == "What's your app name?"
    assert question.question_type == QuestionType.OPEN_ENDED
    assert question.key == "app_name"
    assert question.default == "myapp"
    
    print("✓ test_question_creation passed")


def test_scenario_engine_initialization():
    """Test ScenarioEngine initialization"""
    engine = ScenarioEngine()
    
    assert engine.state == ConversationState.GREETING
    assert len(engine.questions_asked) == 0
    assert len(engine.pending_questions) == 0
    assert engine.context is not None
    
    print("✓ test_scenario_engine_initialization passed")


def test_scenario_engine_start():
    """Test starting a conversation"""
    engine = ScenarioEngine()
    
    response = engine.start_conversation()
    
    assert "Echo" in response
    assert "scripting companion" in response
    assert engine.state == ConversationState.GREETING
    
    print("✓ test_scenario_engine_start passed")


def test_intent_parsing_deploy():
    """Test intent parsing for deployment"""
    engine = ScenarioEngine()
    
    # Test Kubernetes deployment
    intent = engine._parse_intent("I need to deploy to Kubernetes")
    assert intent['phase'] == 'deploy'
    assert intent['task_type'] == 'kubernetes'
    
    # Test Docker deployment
    intent = engine._parse_intent("deploy my Docker container")
    assert intent['phase'] == 'deploy'
    assert intent['task_type'] == 'docker'
    
    print("✓ test_intent_parsing_deploy passed")


def test_intent_parsing_build():
    """Test intent parsing for build"""
    engine = ScenarioEngine()
    
    # Test Docker build
    intent = engine._parse_intent("build a Docker image")
    assert intent['phase'] == 'build'
    assert intent['task_type'] == 'docker_build'
    
    # Test Python build
    intent = engine._parse_intent("build my Python package")
    assert intent['phase'] == 'build'
    assert intent['task_type'] == 'python_build'
    
    # Test Node build
    intent = engine._parse_intent("build Node.js app")
    assert intent['phase'] == 'build'
    assert intent['task_type'] == 'node_build'
    
    print("✓ test_intent_parsing_build passed")


def test_intent_parsing_test():
    """Test intent parsing for testing"""
    engine = ScenarioEngine()
    
    # Test unit tests
    intent = engine._parse_intent("run unit tests")
    assert intent['phase'] == 'test'
    assert intent['task_type'] == 'unit_tests'
    
    # Test integration tests
    intent = engine._parse_intent("run integration tests")
    assert intent['phase'] == 'test'
    assert intent['task_type'] == 'integration_tests'
    
    print("✓ test_intent_parsing_test passed")


def test_intent_parsing_monitor():
    """Test intent parsing for monitoring"""
    engine = ScenarioEngine()
    
    # Test Prometheus metrics
    intent = engine._parse_intent("set up Prometheus metrics")
    assert intent['phase'] == 'monitor'
    assert intent['task_type'] == 'metrics'
    
    # Test alerting
    intent = engine._parse_intent("configure alerts")
    assert intent['phase'] == 'monitor'
    assert intent['task_type'] == 'alerting'
    
    print("✓ test_intent_parsing_monitor passed")


def test_intent_parsing_security():
    """Test intent parsing for security"""
    engine = ScenarioEngine()
    
    # Test vulnerability scan
    intent = engine._parse_intent("scan for vulnerabilities")
    assert intent['phase'] == 'secure'
    assert intent['task_type'] == 'vulnerability_scan'
    
    print("✓ test_intent_parsing_security passed")


def test_question_generation_kubernetes():
    """Test question generation for Kubernetes deployment"""
    engine = ScenarioEngine()
    engine.context.phase = 'deploy'
    engine.context.task_type = 'kubernetes'
    
    questions = engine._generate_questions()
    
    assert len(questions) > 0
    
    # Check for expected questions
    question_keys = [q.key for q in questions]
    assert 'app_name' in question_keys
    assert 'namespace' in question_keys
    assert 'has_manifest' in question_keys
    
    print("✓ test_question_generation_kubernetes passed")


def test_question_generation_docker_build():
    """Test question generation for Docker build"""
    engine = ScenarioEngine()
    engine.context.phase = 'build'
    engine.context.task_type = 'docker_build'
    
    questions = engine._generate_questions()
    
    assert len(questions) > 0
    
    question_keys = [q.key for q in questions]
    assert 'image_name' in question_keys
    assert 'tag' in question_keys
    
    print("✓ test_question_generation_docker_build passed")


def test_echo_scenario_bot_initialization():
    """Test EchoScenarioBot initialization"""
    bot = EchoScenarioBot()
    
    assert bot.engine is not None
    assert bot.session_start is not None
    assert not bot.is_complete()
    
    print("✓ test_echo_scenario_bot_initialization passed")


def test_echo_scenario_bot_start():
    """Test EchoScenarioBot start method"""
    bot = EchoScenarioBot()
    
    response = bot.start()
    
    assert "Echo" in response
    assert len(response) > 0
    assert not bot.is_complete()
    
    print("✓ test_echo_scenario_bot_start passed")


def test_echo_scenario_bot_conversation_flow():
    """Test full conversation flow"""
    bot = EchoScenarioBot()
    
    # Start
    response = bot.start("I need to deploy to Kubernetes")
    assert "kubernetes" in response.lower()
    
    # Answer questions
    response = bot.chat("myapp")
    assert len(response) > 0
    
    response = bot.chat("production")
    assert len(response) > 0
    
    response = bot.chat("yes")
    assert len(response) > 0
    
    response = bot.chat("no")
    assert len(response) > 0
    
    # Confirm
    response = bot.chat("yes")
    assert "script" in response.lower() or "generating" in response.lower()
    
    # Should be complete now
    assert bot.is_complete()
    
    # Should be able to get script
    script = bot.get_script()
    assert script is not None
    assert len(script) > 0
    
    print("✓ test_echo_scenario_bot_conversation_flow passed")


def test_echo_scenario_bot_reset():
    """Test bot reset functionality"""
    bot = EchoScenarioBot()
    
    # Have a conversation
    bot.start("I need to build Docker image")
    bot.chat("myapp")
    
    # Reset
    bot.reset()
    
    # Should be back to initial state
    assert bot.engine.state == ConversationState.GREETING
    assert len(bot.engine.questions_asked) == 0
    assert not bot.is_complete()
    
    print("✓ test_echo_scenario_bot_reset passed")


def test_script_creation():
    """Test script creation from context"""
    engine = ScenarioEngine()
    engine.context.goal = "Deploy to Kubernetes"
    engine.context.phase = "deploy"
    engine.context.task_type = "kubernetes"
    engine.context.requirements = {
        "app_name": "myapp",
        "namespace": "production"
    }
    
    script = engine._create_script_from_context()
    
    assert script is not None
    assert "#!/usr/bin/env bash" in script
    assert "myapp" in script
    assert "production" in script
    assert "Generated by Echo" in script
    
    print("✓ test_script_creation passed")


def test_conversation_states():
    """Test conversation state transitions"""
    engine = ScenarioEngine()
    
    # Initial state
    assert engine.state == ConversationState.GREETING
    
    # Process intent
    engine._process_initial_intent("deploy to Kubernetes")
    assert engine.state == ConversationState.GATHERING_REQUIREMENTS
    
    print("✓ test_conversation_states passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("Running Echo Scenario Bot Tests")
    print("="*70 + "\n")
    
    tests = [
        test_scenario_context,
        test_question_creation,
        test_scenario_engine_initialization,
        test_scenario_engine_start,
        test_intent_parsing_deploy,
        test_intent_parsing_build,
        test_intent_parsing_test,
        test_intent_parsing_monitor,
        test_intent_parsing_security,
        test_question_generation_kubernetes,
        test_question_generation_docker_build,
        test_echo_scenario_bot_initialization,
        test_echo_scenario_bot_start,
        test_echo_scenario_bot_conversation_flow,
        test_echo_scenario_bot_reset,
        test_script_creation,
        test_conversation_states,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} error: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
