#!/usr/bin/env python3
"""
Demo script showcasing the Plugin Wizard, Config Editor, and AI Assistant.
Run from platform directory: cd platform && python ../demo_plugin_wizard.py
"""

import sys
from pathlib import Path

# Add current directory to path (when run from platform directory)
sys.path.insert(0, '.')
sys.path.insert(0, '../chatops/irc/bot-engine')

from plugins.wizard.wizard_engine import WizardEngine
from plugins.config_editor.editor import ConfigEditor
from ai_assistant.assistant import AIAssistant


def print_header(text):
    """Print a formatted header."""
    print(f'\n{"=" * 70}')
    print(f'  {text}')
    print("=" * 70)


def demo_wizard():
    """Demonstrate the Plugin Wizard."""
    print_header("1. Plugin Wizard Demo")
    
    wizard = WizardEngine('/tmp/demo-plugins')
    
    # Start session
    session = wizard.start_session()
    print(f'\n✓ Started wizard session: {session.session_id[:8]}...')
    
    # Select Python plugin
    result = wizard.advance_step(session.session_id, {'plugin_type': 'python'})
    print(f'✓ Selected plugin type: Python')
    
    # Submit metadata
    result = wizard.advance_step(session.session_id, {
        'name': 'demo-automation-plugin',
        'description': 'A demo plugin showcasing the wizard capabilities',
        'version': '1.0.0',
        'author': 'Demo Script',
        'tags': ['demo', 'automation']
    })
    print(f'✓ Submitted metadata: demo-automation-plugin v1.0.0')
    
    # Submit configuration
    result = wizard.advance_step(session.session_id, {
        'python_version': '3.10',
        'venv_enabled': True,
        'venv_path': '.venv',
        'dependencies': ['flask>=2.0', 'requests', 'pyyaml'],
        'entry_point': 'main.py'
    })
    print(f'✓ Configured Python settings')
    
    # Complete wizard
    result = wizard.advance_step(session.session_id, {'confirm': True})
    if result['success']:
        print(f'✓ Plugin created at: {result["plugin_path"]}')
        print('\n  Folder structure:')
        print('    ├── src/')
        print('    ├── logs/')
        print('    ├── config/')
        print('    │   ├── plugin.yaml')
        print('    │   └── python_config.yaml')
        print('    ├── tests/')
        print('    ├── README.md')
        print('    ├── .gitignore')
        print('    └── requirements.txt')


def demo_config_editor():
    """Demonstrate the Configuration Editor."""
    print_header("2. Configuration Editor Demo")
    
    editor = ConfigEditor('/tmp/demo-plugins')
    print('\n✓ Configuration editor initialized')
    
    # Example validation
    sample_config = {
        'plugin': {
            'name': 'demo-plugin',
            'version': '1.0.0',
            'description': 'Demo plugin configuration',
            'type': 'python'
        }
    }
    
    result = editor.validate_config('demo-plugin', sample_config)
    print(f'\n✓ Configuration validation: {"PASSED" if result["valid"] else "FAILED"}')
    
    if not result['valid']:
        print('  Validation errors:')
        for error in result['errors']:
            print(f'    - {error}')
    
    print('\n  Features available:')
    print('    - Real-time YAML/JSON editing')
    print('    - Schema validation')
    print('    - Diff viewing')
    print('    - Automatic backups')


def demo_ai_assistant():
    """Demonstrate the AI Assistant."""
    print_header("3. AI Assistant Demo")
    
    assistant = AIAssistant()
    print('\n✓ AI Assistant initialized')
    
    # Test default suggestions
    print('\n📋 Default suggestions for Python plugin:')
    defaults = assistant.suggest_defaults('python')
    for key, value in list(defaults.items())[:5]:
        if isinstance(value, list):
            value = ', '.join(str(v) for v in value[:2])
        print(f'    {key}: {value}')
    
    # Test validation
    print('\n🔍 Validating PHP configuration:')
    php_config = {
        'memory_limit': '256M',
        'upload_max_filesize': '512M',
        'post_max_size': '64M'
    }
    result = assistant.validate_plugin_config('php', php_config)
    
    if result['issues']:
        print(f'  Found {len(result["issues"])} potential issues:')
        for issue in result['issues'][:2]:
            print(f'    ⚠️  {issue["message"]}')
    
    if result['suggestions']:
        print(f'\n  💡 {len(result["suggestions"])} suggestions available')
    
    # Test knowledge base
    print('\n💬 AI Assistant Q&A:')
    questions = [
        'How do I configure PHP memory limit?',
        'How do I set up Python virtual environment?'
    ]
    
    for question in questions:
        answer = assistant.answer_question(question)
        print(f'\n  Q: {question}')
        print(f'  A: {answer[:120]}...')
    
    # Test setup guide
    print('\n📖 Setup guide for Node.js:')
    guide = assistant.get_setup_guide('nodejs')
    print(f'  Steps: {len(guide["steps"])}')
    for i, step in enumerate(guide['steps'][:3], 1):
        print(f'    {i}. {step}')


def demo_irc_commands():
    """Show IRC bot commands."""
    print_header("4. IRC Bot Commands")
    
    print('\n📢 Public channel commands:')
    print('    !plugin wizard              - Start plugin wizard')
    print('    !plugin help <type>         - Get help for plugin type')
    print('    !plugin validate <type>     - Validate default config')
    print('    !plugin suggest <type>      - Get suggested defaults')
    print('    !plugin status              - Check wizard status')
    
    print('\n💬 Private message commands:')
    print('    /msg bot !plugin ask <question>')
    print('      - Ask AI assistant for help')
    
    print('\n📝 Example IRC session:')
    print('    <user> !plugin help python')
    print('    <bot>  Setup guide for python:')
    print('    <bot>  1. Install Python 3.8 or newer')
    print('    <bot>  2. Create virtual environment: python -m venv .venv')
    print('    <bot>  3. Activate virtual environment')


def main():
    """Run all demos."""
    print('\n')
    print('╔══════════════════════════════════════════════════════════════════════╗')
    print('║                                                                      ║')
    print('║         MasterChief Plugin System - Feature Demonstration           ║')
    print('║                                                                      ║')
    print('╚══════════════════════════════════════════════════════════════════════╝')
    
    try:
        demo_wizard()
        demo_config_editor()
        demo_ai_assistant()
        demo_irc_commands()
        
        print_header("Demo Complete!")
        print('\n✅ All features demonstrated successfully!')
        print('\n📚 Documentation:')
        print('    - docs/plugin-wizard.md')
        print('    - docs/config-editor.md')
        print('    - docs/ai-assistant.md')
        print('\n🚀 To get started:')
        print('    cd platform && python main.py')
        print('    # Visit http://localhost:8443')
        print('')
        
    except Exception as e:
        print(f'\n❌ Demo failed: {e}')
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
