"""
Plugin configuration knowledge base.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class PluginKnowledgeBase:
    """Knowledge base for plugin configuration and troubleshooting."""
    
    def __init__(self):
        """Initialize knowledge base."""
        self.logger = logging.getLogger(__name__)
        self.knowledge = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict[str, Any]:
        """Load knowledge base data."""
        return {
            'php': {
                'setup_steps': [
                    'Install PHP with required extensions',
                    'Configure php.ini settings',
                    'Set proper file permissions (755 for directories, 644 for files)',
                    'Test configuration with php -v and php -m',
                    'Verify web server integration if applicable'
                ],
                'best_practices': [
                    'Use latest stable PHP version (8.2+)',
                    'Enable OPcache for better performance',
                    'Set reasonable memory and execution time limits',
                    'Use Composer for dependency management',
                    'Enable error logging in production'
                ],
                'common_issues': [
                    {
                        'issue': 'Memory exhausted errors',
                        'solution': 'Increase memory_limit in php.ini or plugin config'
                    },
                    {
                        'issue': 'Upload failures',
                        'solution': 'Check upload_max_filesize and post_max_size settings'
                    },
                    {
                        'issue': 'Extension not found',
                        'solution': 'Install required PHP extension and restart web server'
                    }
                ]
            },
            'python': {
                'setup_steps': [
                    'Install Python 3.8 or newer',
                    'Create virtual environment: python -m venv .venv',
                    'Activate virtual environment',
                    'Install dependencies: pip install -r requirements.txt',
                    'Test import of main module'
                ],
                'best_practices': [
                    'Always use virtual environments',
                    'Pin dependency versions in requirements.txt',
                    'Use type hints for better code quality',
                    'Follow PEP 8 style guide',
                    'Write unit tests with pytest'
                ],
                'common_issues': [
                    {
                        'issue': 'Module not found',
                        'solution': 'Ensure virtual environment is activated and dependencies are installed'
                    },
                    {
                        'issue': 'Permission denied',
                        'solution': 'Check file permissions and virtual environment ownership'
                    },
                    {
                        'issue': 'Version conflicts',
                        'solution': 'Use pip freeze to audit dependencies and resolve conflicts'
                    }
                ]
            },
            'powershell': {
                'setup_steps': [
                    'Install PowerShell 7+ (recommended)',
                    'Set execution policy: Set-ExecutionPolicy RemoteSigned',
                    'Install required modules: Install-Module <ModuleName>',
                    'Test script execution',
                    'Configure logging and error handling'
                ],
                'best_practices': [
                    'Use approved verbs for function names',
                    'Implement proper error handling with try/catch',
                    'Use parameter validation',
                    'Write comment-based help',
                    'Test on both Windows PowerShell and PowerShell 7+'
                ],
                'common_issues': [
                    {
                        'issue': 'Execution policy error',
                        'solution': 'Set execution policy to RemoteSigned or Bypass'
                    },
                    {
                        'issue': 'Module not found',
                        'solution': 'Install module with Install-Module or update $env:PSModulePath'
                    },
                    {
                        'issue': 'Access denied',
                        'solution': 'Run PowerShell as Administrator or check file permissions'
                    }
                ]
            },
            'nodejs': {
                'setup_steps': [
                    'Install Node.js LTS version',
                    'Initialize project: npm init',
                    'Install dependencies: npm install',
                    'Set up entry point (index.js or main file)',
                    'Test with: node index.js'
                ],
                'best_practices': [
                    'Use LTS versions of Node.js',
                    'Lock dependency versions with package-lock.json',
                    'Use async/await for async operations',
                    'Implement proper error handling',
                    'Use ESLint for code quality'
                ],
                'common_issues': [
                    {
                        'issue': 'Module not found',
                        'solution': 'Run npm install to install dependencies'
                    },
                    {
                        'issue': 'EACCES permission error',
                        'solution': 'Fix npm permissions or use nvm'
                    },
                    {
                        'issue': 'Version mismatch',
                        'solution': 'Use nvm to switch Node.js versions'
                    }
                ]
            },
            'shell': {
                'setup_steps': [
                    'Ensure shell is available (bash, zsh, etc.)',
                    'Make script executable: chmod +x script.sh',
                    'Add shebang line: #!/bin/bash',
                    'Test script execution',
                    'Set up environment variables if needed'
                ],
                'best_practices': [
                    'Always include shebang line',
                    'Use set -e to exit on errors',
                    'Quote variables to prevent word splitting',
                    'Use shellcheck for static analysis',
                    'Add error handling and logging'
                ],
                'common_issues': [
                    {
                        'issue': 'Permission denied',
                        'solution': 'Make script executable with chmod +x'
                    },
                    {
                        'issue': 'Command not found',
                        'solution': 'Check PATH or use absolute paths'
                    },
                    {
                        'issue': 'Syntax errors',
                        'solution': 'Use shellcheck to validate syntax'
                    }
                ]
            }
        }
    
    def query(self, question: str) -> str:
        """
        Answer a plugin configuration question.
        
        Args:
            question: User question
            
        Returns:
            Answer or guidance
        """
        question_lower = question.lower()
        
        # Simple keyword matching
        if 'php' in question_lower:
            if 'memory' in question_lower:
                return "For PHP memory issues, increase 'memory_limit' in your config. Typical values are 256M for small apps, 512M for medium, and 1G+ for large applications."
            elif 'upload' in question_lower:
                return "To fix upload issues, check 'upload_max_filesize' and 'post_max_size'. Post max size should be equal to or larger than upload max filesize."
        
        elif 'python' in question_lower:
            if 'virtual' in question_lower or 'venv' in question_lower:
                return "Create a virtual environment with: python -m venv .venv, then activate it with: source .venv/bin/activate (Linux/Mac) or .venv\\Scripts\\activate (Windows)."
            elif 'dependency' in question_lower or 'package' in question_lower:
                return "Install dependencies with: pip install -r requirements.txt. Always use a virtual environment to avoid conflicts."
        
        elif 'powershell' in question_lower:
            if 'execution' in question_lower or 'policy' in question_lower:
                return "Set execution policy with: Set-ExecutionPolicy RemoteSigned. This allows running local scripts while still protecting against unsigned remote scripts."
            elif 'module' in question_lower:
                return "Install PowerShell modules with: Install-Module <ModuleName> -Scope CurrentUser. Use Get-Module -ListAvailable to see installed modules."
        
        elif 'nodejs' in question_lower or 'node' in question_lower:
            if 'install' in question_lower or 'npm' in question_lower:
                return "Install Node.js dependencies with: npm install. Use npm ci for clean installs in CI/CD environments."
            elif 'version' in question_lower:
                return "Use nvm (Node Version Manager) to manage multiple Node.js versions. Install with: nvm install <version>, use with: nvm use <version>."
        
        elif 'shell' in question_lower or 'bash' in question_lower:
            if 'permission' in question_lower:
                return "Make shell scripts executable with: chmod +x script.sh. Scripts should also have a shebang line like #!/bin/bash at the top."
            elif 'error' in question_lower:
                return "Use 'set -e' at the start of your script to exit on errors. Add 'set -x' for debugging to see each command as it executes."
        
        return "I'm here to help with plugin configuration! Ask me about PHP, Python, PowerShell, Node.js, or Shell plugins. For example: 'How do I fix PHP memory issues?' or 'How do I set up Python virtual environment?'"
    
    def get_setup_steps(self, plugin_type: str) -> List[str]:
        """Get setup steps for a plugin type."""
        return self.knowledge.get(plugin_type, {}).get('setup_steps', [])
    
    def get_best_practices(self, plugin_type: str) -> List[str]:
        """Get best practices for a plugin type."""
        return self.knowledge.get(plugin_type, {}).get('best_practices', [])
    
    def get_common_issues(self, plugin_type: str) -> List[Dict[str, str]]:
        """Get common issues for a plugin type."""
        return self.knowledge.get(plugin_type, {}).get('common_issues', [])
    
    def get_troubleshooting_steps(
        self,
        plugin_type: str,
        issue_description: str
    ) -> List[str]:
        """
        Get troubleshooting steps for a specific issue.
        
        Args:
            plugin_type: Type of plugin
            issue_description: Description of the issue
            
        Returns:
            List of troubleshooting steps
        """
        issue_lower = issue_description.lower()
        
        common_issues = self.get_common_issues(plugin_type)
        
        # Find matching issue
        for issue_info in common_issues:
            if any(keyword in issue_lower for keyword in issue_info['issue'].lower().split()):
                return [
                    f"Issue: {issue_info['issue']}",
                    f"Solution: {issue_info['solution']}",
                    "If this doesn't help, check logs for more details",
                    "Verify all dependencies are installed",
                    "Check file permissions and ownership"
                ]
        
        # Generic troubleshooting steps
        return [
            "Check plugin logs in logs/ directory",
            "Verify configuration in config/plugin.yaml",
            "Check file and directory permissions",
            "Ensure all dependencies are installed",
            f"Review {plugin_type} best practices for your setup"
        ]
