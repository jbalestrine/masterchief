"""Tests for AI script generator."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from addons.scripts.ai_generator import AIScriptGenerator, GeneratedScript


@pytest.fixture
def mock_ollama_response():
    """Mock Ollama API response."""
    return {
        "message": {
            "content": """#!/bin/bash
# Backup script
tar -czf backup.tar.gz /data
"""
        }
    }


@pytest.fixture
def generator():
    """Create AI script generator instance."""
    return AIScriptGenerator(model="codellama", ollama_url="http://localhost:11434")


def test_generator_initialization():
    """Test generator can be initialized."""
    gen = AIScriptGenerator()
    assert gen is not None
    assert gen.model == "codellama"
    assert gen.ollama_url == "http://localhost:11434"


def test_generator_custom_config():
    """Test generator with custom configuration."""
    gen = AIScriptGenerator(model="llama2", ollama_url="http://custom:8080")
    assert gen.model == "llama2"
    assert gen.ollama_url == "http://custom:8080"


@patch('addons.scripts.ai_generator.httpx.Client')
def test_generate_script(mock_client_class, mock_ollama_response):
    """Test generating a script from description."""
    # Setup mock
    mock_client = Mock()
    mock_response = Mock()
    mock_response.json.return_value = mock_ollama_response
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    gen = AIScriptGenerator()
    
    script = gen.generate(
        description="Create a backup script",
        language="bash"
    )
    
    assert isinstance(script, GeneratedScript)
    assert script.language == "bash"
    assert script.description == "Create a backup script"
    assert "#!/bin/bash" in script.content or "backup" in script.content.lower()


@patch('addons.scripts.ai_generator.httpx.Client')
def test_explain_script(mock_client_class):
    """Test explaining a script."""
    # Setup mock
    mock_client = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "message": {
            "content": "This script creates a backup of the /data directory using tar."
        }
    }
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    gen = AIScriptGenerator()
    
    explanation = gen.explain("tar -czf backup.tar.gz /data")
    
    assert isinstance(explanation, str)
    assert len(explanation) > 0


@patch('addons.scripts.ai_generator.httpx.Client')
def test_improve_script(mock_client_class):
    """Test getting improvement suggestions."""
    # Setup mock
    mock_client = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "message": {
            "content": "Add error handling and check if directory exists."
        }
    }
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    gen = AIScriptGenerator()
    
    suggestions = gen.improve("tar -czf backup.tar.gz /data")
    
    assert isinstance(suggestions, str)
    assert len(suggestions) > 0


@patch('addons.scripts.ai_generator.httpx.Client')
def test_convert_script(mock_client_class):
    """Test converting script between languages."""
    # Setup mock
    mock_client = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "message": {
            "content": """import subprocess
subprocess.run(['tar', '-czf', 'backup.tar.gz', '/data'])
"""
        }
    }
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    gen = AIScriptGenerator()
    
    converted = gen.convert(
        script="tar -czf backup.tar.gz /data",
        from_lang="bash",
        to_lang="python"
    )
    
    assert isinstance(converted, str)
    assert len(converted) > 0


def test_generate_filename():
    """Test filename generation from description."""
    gen = AIScriptGenerator()
    
    # Test bash script
    filename = gen._generate_filename("backup all databases", "bash")
    assert filename.endswith(".sh")
    assert "backup" in filename.lower()
    
    # Test python script
    filename = gen._generate_filename("deploy application", "python")
    assert filename.endswith(".py")
    
    # Test with special characters
    filename = gen._generate_filename("test@script#with$special%chars", "bash")
    assert filename.endswith(".sh")
    # Should only have alphanumeric and underscores
    assert all(c.isalnum() or c in ['_', '.'] for c in filename)


@patch('addons.scripts.ai_generator.httpx.Client')
def test_check_availability(mock_client_class):
    """Test checking if Ollama is available."""
    # Setup mock
    mock_client = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "models": [
            {"name": "codellama:latest"},
            {"name": "llama2:latest"}
        ]
    }
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    gen = AIScriptGenerator(model="codellama")
    
    available = gen.check_availability()
    assert available is True


@patch('addons.scripts.ai_generator.httpx.Client')
def test_check_availability_model_not_found(mock_client_class):
    """Test check availability when model is not found."""
    # Setup mock
    mock_client = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "models": [
            {"name": "llama2:latest"}
        ]
    }
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    gen = AIScriptGenerator(model="codellama")
    
    available = gen.check_availability()
    assert available is False


@patch('addons.scripts.ai_generator.httpx.Client')
def test_generate_with_markdown_cleanup(mock_client_class):
    """Test that markdown code blocks are cleaned from generated scripts."""
    # Setup mock with markdown code blocks
    mock_client = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "message": {
            "content": """```bash
#!/bin/bash
echo "Hello"
```"""
        }
    }
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    gen = AIScriptGenerator()
    
    script = gen.generate("simple script", language="bash")
    
    # Markdown code fences should be removed
    assert "```" not in script.content
    assert "#!/bin/bash" in script.content or "echo" in script.content
