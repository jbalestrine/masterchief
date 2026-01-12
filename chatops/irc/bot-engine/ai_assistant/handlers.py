"""
IRC command handlers for plugin management.
"""

import logging
from typing import Any

from .assistant import AIAssistant

logger = logging.getLogger(__name__)


class PluginCommandHandlers:
    """IRC command handlers for plugin operations."""
    
    def __init__(self):
        """Initialize command handlers."""
        self.assistant = AIAssistant()
        logger.info("Plugin command handlers initialized")
    
    def wizard_start_handler(self, connection: Any, event: Any, args: list):
        """
        Handle !plugin wizard command.
        
        Args:
            connection: IRC connection
            event: IRC event
            args: Command arguments
        """
        channel = event.target
        nick = event.source.nick
        
        message = (
            f"{nick}: Plugin Wizard starting! "
            "Visit the web UI at http://masterchief-host:8443/plugins/wizard "
            "or use the API: POST /api/wizard/start"
        )
        
        connection.privmsg(channel, message)
        logger.info(f"Plugin wizard started by {nick}")
    
    def plugin_help_handler(self, connection: Any, event: Any, args: list):
        """
        Handle !plugin help command.
        
        Args:
            connection: IRC connection
            event: IRC event
            args: Command arguments
        """
        channel = event.target
        nick = event.source.nick
        
        if args and len(args) > 0:
            plugin_type = args[0].lower()
            guide = self.assistant.get_setup_guide(plugin_type)
            
            if guide['steps']:
                connection.privmsg(channel, f"{nick}: Setup guide for {plugin_type}:")
                for i, step in enumerate(guide['steps'][:3], 1):
                    connection.privmsg(channel, f"{i}. {step}")
                
                if len(guide['steps']) > 3:
                    connection.privmsg(
                        channel,
                        f"({len(guide['steps']) - 3} more steps... use !plugin ask for details)"
                    )
            else:
                connection.privmsg(
                    channel,
                    f"{nick}: Unknown plugin type. Try: php, python, powershell, nodejs, shell"
                )
        else:
            help_text = (
                f"{nick}: Plugin commands: "
                "!plugin wizard (start wizard), "
                "!plugin help <type> (get help), "
                "!plugin validate <type> (validate config), "
                "!plugin suggest <type> (get defaults), "
                "!plugin status (check status)"
            )
            connection.privmsg(channel, help_text)
    
    def validate_config_handler(self, connection: Any, event: Any, args: list):
        """
        Handle !plugin validate command.
        
        Args:
            connection: IRC connection
            event: IRC event
            args: Command arguments
        """
        channel = event.target
        nick = event.source.nick
        
        if not args or len(args) < 1:
            connection.privmsg(
                channel,
                f"{nick}: Usage: !plugin validate <type>. Example: !plugin validate php"
            )
            return
        
        plugin_type = args[0].lower()
        
        # Get defaults and validate them
        defaults = self.assistant.suggest_defaults(plugin_type)
        
        if defaults:
            result = self.assistant.validate_plugin_config(plugin_type, defaults)
            
            if result['valid']:
                connection.privmsg(
                    channel,
                    f"{nick}: {plugin_type.upper()} default configuration is valid! ✓"
                )
            else:
                connection.privmsg(
                    channel,
                    f"{nick}: Found {len(result['issues'])} potential issues with {plugin_type} config"
                )
                
                for issue in result['issues'][:2]:
                    connection.privmsg(channel, f"  - {issue.get('message', 'Unknown issue')}")
                
                if len(result['suggestions']) > 0:
                    connection.privmsg(
                        channel,
                        f"  💡 {len(result['suggestions'])} suggestions available"
                    )
        else:
            connection.privmsg(
                channel,
                f"{nick}: Unknown plugin type. Try: php, python, powershell, nodejs, shell"
            )
    
    def suggest_defaults_handler(self, connection: Any, event: Any, args: list):
        """
        Handle !plugin suggest command.
        
        Args:
            connection: IRC connection
            event: IRC event
            args: Command arguments
        """
        channel = event.target
        nick = event.source.nick
        
        if not args or len(args) < 1:
            connection.privmsg(
                channel,
                f"{nick}: Usage: !plugin suggest <type>. Example: !plugin suggest python"
            )
            return
        
        plugin_type = args[0].lower()
        defaults = self.assistant.suggest_defaults(plugin_type)
        
        if defaults:
            connection.privmsg(channel, f"{nick}: Suggested defaults for {plugin_type}:")
            
            # Show top 3 most important settings
            important_keys = {
                'php': ['php_version', 'memory_limit', 'extensions'],
                'python': ['python_version', 'venv_enabled', 'dependencies'],
                'powershell': ['ps_version', 'execution_policy', 'modules'],
                'nodejs': ['node_version', 'package_manager', 'dependencies'],
                'shell': ['shell_type', 'entry_point']
            }
            
            keys_to_show = important_keys.get(plugin_type, list(defaults.keys())[:3])
            
            for key in keys_to_show:
                if key in defaults:
                    value = defaults[key]
                    if isinstance(value, list):
                        value = ', '.join(str(v) for v in value[:3])
                        if len(defaults[key]) > 3:
                            value += '...'
                    connection.privmsg(channel, f"  {key}: {value}")
            
            connection.privmsg(
                channel,
                f"Use the web UI or API for full configuration options"
            )
        else:
            connection.privmsg(
                channel,
                f"{nick}: Unknown plugin type. Try: php, python, powershell, nodejs, shell"
            )
    
    def plugin_status_handler(self, connection: Any, event: Any, args: list):
        """
        Handle !plugin status command.
        
        Args:
            connection: IRC connection
            event: IRC event
            args: Command arguments
        """
        channel = event.target
        nick = event.source.nick
        
        # Show available plugin types
        status_msg = (
            f"{nick}: Plugin Wizard Status - "
            "Supported types: PHP, Python, PowerShell, Node.js, Shell/Bash. "
            "API endpoint: /api/wizard/start"
        )
        connection.privmsg(channel, status_msg)
    
    def ai_ask_handler(self, connection: Any, event: Any, args: list):
        """
        Handle !plugin ask command (private message).
        
        Args:
            connection: IRC connection
            event: IRC event
            args: Command arguments
        """
        nick = event.source.nick
        
        if not args or len(args) < 1:
            connection.privmsg(
                nick,
                "Usage: !plugin ask <question>. Example: !plugin ask how do I fix PHP memory issues?"
            )
            return
        
        question = ' '.join(args)
        answer = self.assistant.answer_question(question)
        
        # Send answer as private message
        connection.privmsg(nick, f"AI Assistant: {answer}")
        logger.info(f"Answered question from {nick}: {question}")


def register_handlers(bot: Any):
    """
    Register plugin-related IRC command handlers.
    
    Args:
        bot: IRC bot instance
    """
    handlers = PluginCommandHandlers()
    
    # Register public channel commands
    bot.bind("pub", "-|-", "!plugin wizard", handlers.wizard_start_handler)
    bot.bind("pub", "-|-", "!plugin help", handlers.plugin_help_handler)
    bot.bind("pub", "-|-", "!plugin validate", handlers.validate_config_handler)
    bot.bind("pub", "-|-", "!plugin suggest", handlers.suggest_defaults_handler)
    bot.bind("pub", "-|-", "!plugin status", handlers.plugin_status_handler)
    
    # Register private message command for AI queries
    bot.bind("msg", "-|-", "!plugin ask", handlers.ai_ask_handler)
    
    logger.info("Plugin command handlers registered successfully")
