# AI Assistant Documentation

## Overview

The AI Assistant provides intelligent guidance for plugin configuration, troubleshooting, and best practices through IRC bot commands. It integrates with the existing MasterChief IRC bot to provide real-time assistance.

## Features

- **Input Validation** - Detect conflicting settings and misconfigurations
- **Conflict Resolution** - Suggest fixes for common issues
- **Default Suggestions** - Recommend sensible defaults based on plugin type
- **Permission Checking** - Warn about potential security and permission issues
- **Setup Guidance** - Step-by-step help for plugin configuration
- **Knowledge Base** - Answer questions about plugin configuration
- **Troubleshooting** - Provide solutions for common problems

## Architecture

### Components

1. **AIAssistant** (`assistant.py`)
   - Main AI logic coordinator
   - Integrates validators, suggestions, and knowledge base
   - Provides high-level assistance methods

2. **AssistantValidators** (`validators.py`)
   - Detects configuration conflicts
   - Identifies misconfigurations
   - Checks file permissions
   - Validates security settings

3. **DefaultSuggestions** (`suggestions.py`)
   - Provides sensible defaults for each plugin type
   - Suggests fixes for detected issues
   - Recommends optimal configurations

4. **PluginKnowledgeBase** (`knowledge_base.py`)
   - Stores setup guides and best practices
   - Provides troubleshooting information
   - Answers common questions

5. **PluginCommandHandlers** (`handlers.py`)
   - IRC command handlers for plugin operations
   - Formats responses for IRC display
   - Manages command execution

## IRC Commands

### Public Channel Commands

#### !plugin wizard
Start the plugin wizard.

```
<user> !plugin wizard
<bot> user: Plugin Wizard starting! Visit the web UI at http://masterchief-host:8443/plugins/wizard or use the API: POST /api/wizard/start
```

#### !plugin help [type]
Get help for a specific plugin type.

```
<user> !plugin help python
<bot> user: Setup guide for python:
<bot> 1. Install Python 3.8 or newer
<bot> 2. Create virtual environment: python -m venv .venv
<bot> 3. Activate virtual environment
<bot> (2 more steps... use !plugin ask for details)
```

#### !plugin validate <type>
Validate default configuration for a plugin type.

```
<user> !plugin validate php
<bot> user: PHP default configuration is valid! ✓
```

Or with issues:

```
<user> !plugin validate php
<bot> user: Found 2 potential issues with php config
<bot>   - Upload size (512M) is too close to memory limit (256M)
<bot>   - post_max_size (64M) must be >= upload_max_filesize (512M)
<bot>   💡 2 suggestions available
```

#### !plugin suggest <type>
Get suggested defaults for a plugin type.

```
<user> !plugin suggest python
<bot> user: Suggested defaults for python:
<bot>   python_version: 3.10
<bot>   venv_enabled: True
<bot>   dependencies: flask, requests, pyyaml
<bot> Use the web UI or API for full configuration options
```

#### !plugin status
Check plugin wizard status.

```
<user> !plugin status
<bot> user: Plugin Wizard Status - Supported types: PHP, Python, PowerShell, Node.js, Shell/Bash. API endpoint: /api/wizard/start
```

### Private Message Commands

#### !plugin ask <question>
Ask the AI assistant a question (private message).

```
/msg bot !plugin ask how do I fix PHP memory issues?
<bot> AI Assistant: For PHP memory issues, increase 'memory_limit' in your config. Typical values are 256M for small apps, 512M for medium, and 1G+ for large applications.
```

```
/msg bot !plugin ask how do I set up Python virtual environment?
<bot> AI Assistant: Create a virtual environment with: python -m venv .venv, then activate it with: source .venv/bin/activate (Linux/Mac) or .venv\Scripts\activate (Windows).
```

## Knowledge Base

### PHP

**Setup Steps:**
1. Install PHP with required extensions
2. Configure php.ini settings
3. Set proper file permissions
4. Test configuration
5. Verify web server integration

**Best Practices:**
- Use latest stable PHP version (8.2+)
- Enable OPcache for performance
- Set reasonable memory limits
- Use Composer for dependencies
- Enable error logging

**Common Issues:**
- Memory exhausted → Increase memory_limit
- Upload failures → Check upload_max_filesize and post_max_size
- Extension not found → Install PHP extension

### Python

**Setup Steps:**
1. Install Python 3.8 or newer
2. Create virtual environment
3. Activate virtual environment
4. Install dependencies
5. Test import of main module

**Best Practices:**
- Always use virtual environments
- Pin dependency versions
- Use type hints
- Follow PEP 8 style guide
- Write unit tests with pytest

**Common Issues:**
- Module not found → Check venv activation and install dependencies
- Permission denied → Check file permissions
- Version conflicts → Use pip freeze to audit

### PowerShell

**Setup Steps:**
1. Install PowerShell 7+ (recommended)
2. Set execution policy
3. Install required modules
4. Test script execution
5. Configure logging

**Best Practices:**
- Use approved verbs for functions
- Implement error handling
- Use parameter validation
- Write comment-based help
- Test on multiple PowerShell versions

**Common Issues:**
- Execution policy error → Set to RemoteSigned or Bypass
- Module not found → Install module or update PSModulePath
- Access denied → Run as Administrator

### Node.js

**Setup Steps:**
1. Install Node.js LTS version
2. Initialize project
3. Install dependencies
4. Set up entry point
5. Test execution

**Best Practices:**
- Use LTS versions
- Lock dependencies with package-lock.json
- Use async/await
- Implement error handling
- Use ESLint for code quality

**Common Issues:**
- Module not found → Run npm install
- EACCES error → Fix npm permissions or use nvm
- Version mismatch → Use nvm to switch versions

### Shell/Bash

**Setup Steps:**
1. Ensure shell is available
2. Make script executable
3. Add shebang line
4. Test script execution
5. Set up environment variables

**Best Practices:**
- Always include shebang
- Use set -e for error handling
- Quote variables
- Use shellcheck
- Add logging

**Common Issues:**
- Permission denied → chmod +x script
- Command not found → Check PATH
- Syntax errors → Use shellcheck

## Conflict Detection

### PHP Conflicts

**Memory vs Upload Size**
```
Issue: Upload size (512M) too close to memory limit (256M)
Suggestion: Increase memory_limit to 512M or decrease upload_max_filesize
```

**Post Size vs Upload Size**
```
Issue: post_max_size (64M) must be >= upload_max_filesize (128M)
Suggestion: Increase post_max_size to 128M or higher
```

### PowerShell Conflicts

**Execution Policy vs Script Signing**
```
Issue: Execution policy is RemoteSigned but script signing is disabled
Suggestion: Enable script signing or change policy to Bypass for testing
```

### Security Warnings

**Unrestricted Execution Policy**
```
Issue: Execution policy "Unrestricted" is a security risk
Suggestion: Use "RemoteSigned" for better security
```

**Deprecated Versions**
```
Issue: Python 3.7 is end-of-life
Suggestion: Upgrade to Python 3.10 or newer
```

## Usage Examples

### IRC Usage

```irc
# Start plugin wizard
<user> !plugin wizard

# Get Python help
<user> !plugin help python

# Validate PHP config
<user> !plugin validate php

# Get Node.js defaults
<user> !plugin suggest nodejs

# Ask a question (private message)
<user> /msg bot !plugin ask how do I configure PHP memory limit?

# Check status
<user> !plugin status
```

### Python API Usage

```python
from chatops.irc.bot_engine.ai_assistant import AIAssistant

assistant = AIAssistant()

# Validate configuration
result = assistant.validate_plugin_config('php', {
    'memory_limit': '256M',
    'upload_max_filesize': '512M'
})

if not result['valid']:
    for issue in result['issues']:
        print(f"Issue: {issue['message']}")
    
    for suggestion in result['suggestions']:
        print(f"Suggestion: {suggestion}")

# Get defaults
defaults = assistant.suggest_defaults('python')
print(defaults)

# Answer question
answer = assistant.answer_question('How do I set up Python venv?')
print(answer)

# Get setup guide
guide = assistant.get_setup_guide('nodejs')
print("Steps:", guide['steps'])
print("Best practices:", guide['best_practices'])
```

## Integration with IRC Bot

The AI Assistant is automatically registered with the IRC bot when enabled:

```python
from chatops.irc.bot_engine.bot import create_bot

# Create bot with AI assistant enabled (default)
bot = create_bot(
    server='irc.example.com',
    port=6667,
    nickname='masterchief-bot',
    channels=['#devops', '#automation'],
    enable_ai_assistant=True
)

# Start bot
bot.start()
```

## Best Practices

1. **Use Private Messages for Detailed Questions** - Keep channels clean
2. **Start with !plugin help** - Get oriented with available commands
3. **Validate Before Deploying** - Use !plugin validate
4. **Follow Suggestions** - AI recommendations are based on best practices
5. **Check Documentation** - Use !plugin ask for specific questions

## Troubleshooting

### Bot Not Responding

**Solution:** Check that AI assistant is enabled and handlers are registered.

### Command Not Recognized

**Solution:** Ensure you're using the correct command syntax with !plugin prefix.

### No Suggestions Provided

**Solution:** The configuration may be valid. Use !plugin suggest for defaults.

## Future Enhancements

- Machine learning-based suggestions from existing configurations
- Integration with monitoring for proactive issue detection
- Automated remediation for common issues
- Custom knowledge base entries
- Multi-language support for responses
