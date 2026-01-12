"""
Script Validator
Validate and lint scripts before execution for safety
"""

import logging
import re
import subprocess
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LintIssue:
    """Represents a linting issue."""
    line: int
    column: int
    severity: str  # error, warning, info
    message: str
    code: Optional[str] = None


@dataclass
class SecurityIssue:
    """Represents a security issue."""
    line: int
    pattern: str
    description: str
    severity: str  # critical, high, medium, low


@dataclass
class ValidationResult:
    """Complete validation result."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    security_issues: List[SecurityIssue]
    lint_issues: List[LintIssue]


class ScriptValidator:
    """Validate and lint scripts before execution."""
    
    # Dangerous patterns that should be blocked
    DANGEROUS_PATTERNS = [
        (r'rm\s+-rf\s+/', 'Dangerous: Recursive delete from root', 'critical'),
        (r'rm\s+-rf\s+/\*', 'Dangerous: Delete all files from root', 'critical'),
        (r'mkfs\.', 'Dangerous: Filesystem formatting', 'critical'),
        (r'dd\s+if=.+of=/dev/[sh]d[a-z]', 'Dangerous: Direct disk write', 'critical'),
        (r'chmod\s+-R\s+777', 'Security risk: Overly permissive permissions', 'high'),
        (r':\(\)\{\s*:\|:&\s*\};:', 'Dangerous: Fork bomb', 'critical'),
        (r'>\s*/dev/[sh]d[a-z]', 'Dangerous: Write to disk device', 'critical'),
        (r'curl.+\|\s*bash', 'Security risk: Pipe to bash from remote source', 'high'),
        (r'wget.+\|\s*sh', 'Security risk: Pipe to shell from remote source', 'high'),
        (r'eval\s+\$\(.*curl', 'Security risk: Eval remote content', 'high'),
        (r'killall\s+-9', 'Potentially dangerous: Force kill all processes', 'medium'),
        (r'chown\s+-R.*/', 'Potentially dangerous: Recursive ownership change', 'medium'),
    ]
    
    def __init__(self, block_dangerous: bool = True, require_validation: bool = False):
        """
        Initialize script validator.
        
        Args:
            block_dangerous: Whether to block scripts with dangerous patterns
            require_validation: Whether validation is required before execution
        """
        self.block_dangerous = block_dangerous
        self.require_validation = require_validation
    
    def validate(self, script_path: str) -> ValidationResult:
        """
        Full validation of a script.
        
        Args:
            script_path: Path to the script file
            
        Returns:
            ValidationResult with all validation findings
        """
        path = Path(script_path)
        errors = []
        warnings = []
        security_issues = []
        lint_issues = []
        
        # Check if file exists
        if not path.exists():
            errors.append(f"Script file not found: {script_path}")
            return ValidationResult(False, errors, warnings, security_issues, lint_issues)
        
        # Read script content
        try:
            with open(path, 'r') as f:
                content = f.read()
        except Exception as e:
            errors.append(f"Failed to read script: {e}")
            return ValidationResult(False, errors, warnings, security_issues, lint_issues)
        
        # Check for dangerous patterns
        security_issues = self.check_security(content)
        
        # Determine script type and lint accordingly
        if path.suffix in ['.sh', '.bash'] or content.startswith('#!/bin/bash') or content.startswith('#!/bin/sh'):
            lint_issues = self.lint_bash(script_path)
        elif path.suffix == '.py' or content.startswith('#!/usr/bin/env python') or content.startswith('#!/usr/bin/python'):
            lint_issues = self.lint_python(script_path)
        
        # Aggregate errors and warnings
        for issue in lint_issues:
            if issue.severity == 'error':
                errors.append(f"Line {issue.line}: {issue.message}")
            elif issue.severity == 'warning':
                warnings.append(f"Line {issue.line}: {issue.message}")
        
        for issue in security_issues:
            if issue.severity in ['critical', 'high']:
                errors.append(f"Security ({issue.severity}): Line {issue.line}: {issue.description}")
            else:
                warnings.append(f"Security ({issue.severity}): Line {issue.line}: {issue.description}")
        
        # Determine if valid
        valid = len(errors) == 0
        if self.block_dangerous and any(issue.severity == 'critical' for issue in security_issues):
            valid = False
        
        return ValidationResult(valid, errors, warnings, security_issues, lint_issues)
    
    def lint_bash(self, script_path: str) -> List[LintIssue]:
        """
        Lint bash script using shellcheck.
        
        Args:
            script_path: Path to bash script
            
        Returns:
            List of lint issues
        """
        issues = []
        
        try:
            # Check if shellcheck is available
            result = subprocess.run(
                ['shellcheck', '--version'],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                logger.warning("shellcheck not available, skipping bash linting")
                return issues
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("shellcheck not available, skipping bash linting")
            return issues
        
        try:
            # Run shellcheck
            result = subprocess.run(
                ['shellcheck', '--format=json', script_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse JSON output
            if result.stdout:
                import json
                findings = json.loads(result.stdout)
                
                for finding in findings:
                    issues.append(LintIssue(
                        line=finding.get('line', 0),
                        column=finding.get('column', 0),
                        severity=finding.get('level', 'info'),
                        message=finding.get('message', ''),
                        code=finding.get('code')
                    ))
        
        except Exception as e:
            logger.error(f"Bash linting failed: {e}")
        
        return issues
    
    def lint_python(self, script_path: str) -> List[LintIssue]:
        """
        Lint Python script using ruff.
        
        Args:
            script_path: Path to Python script
            
        Returns:
            List of lint issues
        """
        issues = []
        
        try:
            # Check if ruff is available
            result = subprocess.run(
                ['ruff', '--version'],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                logger.warning("ruff not available, skipping Python linting")
                return issues
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("ruff not available, skipping Python linting")
            return issues
        
        try:
            # Run ruff
            result = subprocess.run(
                ['ruff', 'check', '--output-format=json', script_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse JSON output
            if result.stdout:
                import json
                findings = json.loads(result.stdout)
                
                for finding in findings:
                    location = finding.get('location', {})
                    issues.append(LintIssue(
                        line=location.get('row', 0),
                        column=location.get('column', 0),
                        severity='error' if finding.get('code', '').startswith('E') else 'warning',
                        message=finding.get('message', ''),
                        code=finding.get('code')
                    ))
        
        except Exception as e:
            logger.error(f"Python linting failed: {e}")
        
        return issues
    
    def check_security(self, script: str) -> List[SecurityIssue]:
        """
        Check for dangerous commands in script.
        
        Args:
            script: Script content to check
            
        Returns:
            List of security issues
        """
        issues = []
        lines = script.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue
            
            # Check each dangerous pattern
            for pattern, description, severity in self.DANGEROUS_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(SecurityIssue(
                        line=line_num,
                        pattern=pattern,
                        description=description,
                        severity=severity
                    ))
        
        return issues
    
    def dry_run(self, script_path: str) -> Dict[str, Any]:
        """
        Simulate script execution without side effects (bash -n).
        
        Args:
            script_path: Path to script
            
        Returns:
            Dict with dry run results
        """
        path = Path(script_path)
        
        try:
            # For bash scripts, use bash -n to check syntax
            if path.suffix in ['.sh', '.bash']:
                result = subprocess.run(
                    ['bash', '-n', script_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                return {
                    'success': result.returncode == 0,
                    'output': result.stderr if result.stderr else 'Syntax check passed',
                    'errors': result.stderr if result.returncode != 0 else None
                }
            
            # For Python scripts, compile to check syntax
            elif path.suffix == '.py':
                with open(path, 'r') as f:
                    content = f.read()
                
                try:
                    compile(content, script_path, 'exec')
                    return {
                        'success': True,
                        'output': 'Python syntax check passed',
                        'errors': None
                    }
                except SyntaxError as e:
                    return {
                        'success': False,
                        'output': '',
                        'errors': str(e)
                    }
            
            else:
                return {
                    'success': False,
                    'output': '',
                    'errors': 'Unsupported script type for dry run'
                }
        
        except Exception as e:
            logger.error(f"Dry run failed: {e}")
            return {
                'success': False,
                'output': '',
                'errors': str(e)
            }
