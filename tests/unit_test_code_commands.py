"""Tests for code CLI commands."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
from core.cli.main import cli


@pytest.fixture
def runner():
    """Create CLI runner."""
    return CliRunner()


def test_code_command_available(runner):
    """Test that code command is available."""
    result = runner.invoke(cli, ['code', '--help'])
    assert result.exit_code == 0
    assert 'Generate code on demand with AI assistance' in result.output


def test_code_generate_help(runner):
    """Test code generate command help."""
    result = runner.invoke(cli, ['code', 'generate', '--help'])
    assert result.exit_code == 0
    assert 'Generate code from a natural language description' in result.output
    assert 'DESCRIPTION' in result.output


def test_code_explain_help(runner):
    """Test code explain command help."""
    result = runner.invoke(cli, ['code', 'explain', '--help'])
    assert result.exit_code == 0
    assert 'Explain what a script does' in result.output


def test_code_improve_help(runner):
    """Test code improve command help."""
    result = runner.invoke(cli, ['code', 'improve', '--help'])
    assert result.exit_code == 0
    assert 'Get improvement suggestions' in result.output


@patch('core.cli.commands.code.AIScriptGenerator')
def test_code_generate_no_ollama(mock_generator_class, runner):
    """Test code generate when Ollama is not available."""
    # Setup mock
    mock_generator = Mock()
    mock_generator.check_availability.return_value = False
    mock_generator_class.return_value = mock_generator
    
    result = runner.invoke(cli, ['code', 'generate', 'test description', '-l', 'bash'])
    
    assert result.exit_code == 1
    assert 'Ollama is not available' in result.output


@patch('core.cli.commands.code.AIScriptGenerator')
def test_code_generate_with_description(mock_generator_class, runner):
    """Test code generate with description provided."""
    from addons.scripts.ai_generator import GeneratedScript
    
    # Setup mock
    mock_generator = Mock()
    mock_generator.check_availability.return_value = True
    mock_generated = GeneratedScript(
        name="test.sh",
        content="#!/bin/bash\necho 'test'",
        language="bash",
        description="test script"
    )
    mock_generator.generate.return_value = mock_generated
    mock_generator_class.return_value = mock_generator
    
    # Run with auto-confirm 'n' to not save
    result = runner.invoke(
        cli, 
        ['code', 'generate', 'test description', '-l', 'bash'],
        input='y\nn\n'  # Confirm generation, decline save
    )
    
    assert result.exit_code == 0
    assert 'Code generated successfully' in result.output or '✅' in result.output
    assert '#!/bin/bash' in result.output or 'echo' in result.output


@patch('core.cli.commands.code.AIScriptGenerator')
def test_code_generate_with_output(mock_generator_class, runner, tmp_path):
    """Test code generate with output file specified."""
    from addons.scripts.ai_generator import GeneratedScript
    
    # Setup mock
    mock_generator = Mock()
    mock_generator.check_availability.return_value = True
    mock_generated = GeneratedScript(
        name="test.sh",
        content="#!/bin/bash\necho 'test'",
        language="bash",
        description="test script"
    )
    mock_generator.generate.return_value = mock_generated
    mock_generator_class.return_value = mock_generator
    
    output_file = tmp_path / "test.sh"
    
    # Run with output file
    result = runner.invoke(
        cli, 
        ['code', 'generate', 'test description', '-l', 'bash', '-o', str(output_file)],
        input='y\ny\n'  # Confirm generation, confirm display
    )
    
    assert result.exit_code == 0
    assert output_file.exists()
    content = output_file.read_text()
    assert '#!/bin/bash' in content or 'echo' in content


@patch('core.cli.commands.code.AIScriptGenerator')  
def test_code_explain(mock_generator_class, runner, tmp_path):
    """Test code explain command."""
    # Create a test script
    test_script = tmp_path / "test.sh"
    test_script.write_text("#!/bin/bash\necho 'Hello'")
    
    # Setup mock
    mock_generator = Mock()
    mock_generator.check_availability.return_value = True
    mock_generator.explain.return_value = "This script prints Hello"
    mock_generator_class.return_value = mock_generator
    
    result = runner.invoke(cli, ['code', 'explain', str(test_script)])
    
    assert result.exit_code == 0
    assert 'This script prints Hello' in result.output


@patch('core.cli.commands.code.AIScriptGenerator')
def test_code_improve(mock_generator_class, runner, tmp_path):
    """Test code improve command."""
    # Create a test script
    test_script = tmp_path / "test.sh"
    test_script.write_text("#!/bin/bash\necho 'Hello'")
    
    # Setup mock
    mock_generator = Mock()
    mock_generator.check_availability.return_value = True
    mock_generator.improve.return_value = "Add error handling"
    mock_generator_class.return_value = mock_generator
    
    result = runner.invoke(cli, ['code', 'improve', str(test_script)])
    
    assert result.exit_code == 0
    assert 'Add error handling' in result.output
