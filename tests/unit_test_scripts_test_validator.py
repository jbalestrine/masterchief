"""Tests for script validator."""
import pytest
from pathlib import Path
import tempfile
from addons.scripts.validator import ScriptValidator, ValidationResult, SecurityIssue


def test_validator_initialization():
    """Test validator can be initialized."""
    validator = ScriptValidator()
    assert validator is not None
    assert validator.block_dangerous is True


def test_check_security_dangerous_rm():
    """Test detection of dangerous rm -rf / command."""
    validator = ScriptValidator()
    
    dangerous_script = """#!/bin/bash
rm -rf /
"""
    
    issues = validator.check_security(dangerous_script)
    assert len(issues) > 0
    assert any(issue.severity == 'critical' for issue in issues)


def test_check_security_fork_bomb():
    """Test detection of fork bomb."""
    validator = ScriptValidator()
    
    fork_bomb = """#!/bin/bash
:(){ :|:& };:
"""
    
    issues = validator.check_security(fork_bomb)
    assert len(issues) > 0
    assert any('fork bomb' in issue.description.lower() for issue in issues)


def test_check_security_chmod_777():
    """Test detection of overly permissive chmod."""
    validator = ScriptValidator()
    
    script = """#!/bin/bash
chmod -R 777 /
"""
    
    issues = validator.check_security(script)
    assert len(issues) > 0
    assert any('permission' in issue.description.lower() for issue in issues)


def test_check_security_safe_script():
    """Test that safe scripts pass security check."""
    validator = ScriptValidator()
    
    safe_script = """#!/bin/bash
echo "Hello, world!"
ls -la
"""
    
    issues = validator.check_security(safe_script)
    assert len(issues) == 0


def test_check_security_pipe_to_bash():
    """Test detection of curl | bash pattern."""
    validator = ScriptValidator()
    
    script = """#!/bin/bash
curl https://example.com/script.sh | bash
"""
    
    issues = validator.check_security(script)
    assert len(issues) > 0
    assert any('pipe to bash' in issue.description.lower() for issue in issues)


def test_validate_nonexistent_script():
    """Test validation of non-existent script."""
    validator = ScriptValidator()
    
    result = validator.validate("/nonexistent/script.sh")
    assert result.valid is False
    assert len(result.errors) > 0


def test_validate_safe_bash_script(tmp_path):
    """Test validation of a safe bash script."""
    validator = ScriptValidator(block_dangerous=True)
    
    script_path = tmp_path / "safe_script.sh"
    script_path.write_text("""#!/bin/bash
echo "Hello, world!"
exit 0
""")
    
    result = validator.validate(str(script_path))
    
    # Should be valid (no critical security issues)
    assert isinstance(result, ValidationResult)
    # May have warnings but no critical errors
    assert all(issue.severity != 'critical' for issue in result.security_issues)


def test_validate_dangerous_bash_script(tmp_path):
    """Test validation of a dangerous bash script."""
    validator = ScriptValidator(block_dangerous=True)
    
    script_path = tmp_path / "dangerous_script.sh"
    script_path.write_text("""#!/bin/bash
rm -rf /
""")
    
    result = validator.validate(str(script_path))
    
    # Should be invalid due to dangerous command
    assert result.valid is False
    assert len(result.security_issues) > 0


def test_dry_run_bash_syntax_error(tmp_path):
    """Test dry run with bash syntax error."""
    validator = ScriptValidator()
    
    script_path = tmp_path / "syntax_error.sh"
    script_path.write_text("""#!/bin/bash
if [ "$x" == "y"
    echo "missing fi"
""")
    
    result = validator.dry_run(str(script_path))
    
    assert result is not None
    assert result['success'] is False
    assert result['errors'] is not None


def test_dry_run_valid_bash(tmp_path):
    """Test dry run with valid bash script."""
    validator = ScriptValidator()
    
    script_path = tmp_path / "valid.sh"
    script_path.write_text("""#!/bin/bash
echo "Hello"
exit 0
""")
    
    result = validator.dry_run(str(script_path))
    
    assert result is not None
    assert result['success'] is True


def test_dry_run_python_syntax_error(tmp_path):
    """Test dry run with Python syntax error."""
    validator = ScriptValidator()
    
    script_path = tmp_path / "syntax_error.py"
    script_path.write_text("""#!/usr/bin/env python
def broken(
    print("missing closing paren")
""")
    
    result = validator.dry_run(str(script_path))
    
    assert result is not None
    assert result['success'] is False


def test_dry_run_valid_python(tmp_path):
    """Test dry run with valid Python script."""
    validator = ScriptValidator()
    
    script_path = tmp_path / "valid.py"
    script_path.write_text("""#!/usr/bin/env python
print("Hello, world!")
""")
    
    result = validator.dry_run(str(script_path))
    
    assert result is not None
    assert result['success'] is True


def test_security_issue_line_numbers():
    """Test that security issues report correct line numbers."""
    validator = ScriptValidator()
    
    script = """#!/bin/bash
# Line 2
echo "safe"
rm -rf /
echo "after dangerous"
"""
    
    issues = validator.check_security(script)
    
    # The dangerous command is on line 4
    dangerous_issues = [i for i in issues if 'recursive delete' in i.description.lower()]
    assert len(dangerous_issues) > 0
    assert dangerous_issues[0].line == 4


def test_validator_skip_comments():
    """Test that validator skips commented dangerous commands."""
    validator = ScriptValidator()
    
    script = """#!/bin/bash
# This is just a comment: rm -rf /
echo "Safe command"
"""
    
    issues = validator.check_security(script)
    
    # Should not flag the commented dangerous command
    assert len(issues) == 0
