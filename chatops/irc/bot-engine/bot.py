"""Eggdrop-style IRC bot engine with TCL-inspired Python bindings."""
import asyncio
import logging
import re
from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

import irc.client
import irc.bot

logger = logging.getLogger(__name__)


class BindType(Enum):
    """IRC binding types."""
    PUB = "pub"  # Public channel command
    MSG = "msg"  # Private message command
    JOIN = "join"  # User join event
    PART = "part"  # User part event
    TIME = "time"  # Scheduled/cron event
    RAW = "raw"  # Raw IRC events
    DCC = "dcc"  # DCC commands
    PUBM = "pubm"  # Public channel pattern match


@dataclass
class Binding:
    """Binding configuration."""
    bind_type: BindType
    flags: str  # Permission flags (e.g., "-|-", "o|-")
    pattern: str  # Command or pattern
    handler: Callable
    cooldown: Optional[int] = None
    last_triggered: Optional[float] = None


class IRCBot(irc.bot.SingleServerIRCBot):
    """Enhanced IRC bot with binding system."""

    def __init__(self, server, port, nickname, channels, realname="MasterChief Bot"):
        super().__init__([(server, port)], nickname, realname)
        self.channels_to_join = channels
        self.bindings: List[Binding] = []
        self.user_levels: Dict[str, str] = {}  # nickname -> level
        self.command_stats: Dict[str, int] = {}

    def on_welcome(self, connection, event):
        """Handle connection to server."""
        logger.info(f"Connected to {event.source}")
        for channel in self.channels_to_join:
            connection.join(channel)
            logger.info(f"Joined channel: {channel}")

    def on_pubmsg(self, connection, event):
        """Handle public channel messages."""
        message = event.arguments[0]
        nick = event.source.nick
        channel = event.target

        # Check for command bindings
        for binding in self.bindings:
            if binding.bind_type == BindType.PUB:
                if message.startswith(binding.pattern):
                    if self._check_permissions(nick, binding.flags):
                        if self._check_cooldown(binding):
                            args = message[len(binding.pattern):].strip().split()
                            self._execute_handler(binding, connection, event, args)

            elif binding.bind_type == BindType.PUBM:
                if re.search(binding.pattern, message):
                    if self._check_permissions(nick, binding.flags):
                        self._execute_handler(binding, connection, event, [message])

    def on_privmsg(self, connection, event):
        """Handle private messages."""
        message = event.arguments[0]
        nick = event.source.nick

        for binding in self.bindings:
            if binding.bind_type == BindType.MSG:
                if message.startswith(binding.pattern):
                    if self._check_permissions(nick, binding.flags):
                        args = message[len(binding.pattern):].strip().split()
                        self._execute_handler(binding, connection, event, args)

    def on_join(self, connection, event):
        """Handle user join events."""
        nick = event.source.nick
        channel = event.target

        for binding in self.bindings:
            if binding.bind_type == BindType.JOIN:
                if binding.pattern == "*" or binding.pattern == channel:
                    self._execute_handler(binding, connection, event, [nick, channel])

    def on_part(self, connection, event):
        """Handle user part events."""
        nick = event.source.nick
        channel = event.target

        for binding in self.bindings:
            if binding.bind_type == BindType.PART:
                if binding.pattern == "*" or binding.pattern == channel:
                    self._execute_handler(binding, connection, event, [nick, channel])

    def bind(self, bind_type: str, flags: str, pattern: str, handler: Callable, cooldown: Optional[int] = None):
        """
        Register a binding (TCL-inspired interface).
        
        Examples:
            bind("pub", "-|-", "!deploy", deploy_handler)
            bind("msg", "-|-", "!status", status_handler)
            bind("join", "-|-", "*", welcome_handler)
            bind("pubm", "-|-", "*terraform*", tf_mention)
        """
        try:
            bind_type_enum = BindType(bind_type)
        except ValueError:
            logger.error(f"Invalid bind type: {bind_type}")
            return

        binding = Binding(
            bind_type=bind_type_enum,
            flags=flags,
            pattern=pattern,
            handler=handler,
            cooldown=cooldown
        )
        self.bindings.append(binding)
        logger.info(f"Registered binding: {bind_type} {pattern}")

    def unbind(self, bind_type: str, pattern: str):
        """Remove a binding."""
        try:
            bind_type_enum = BindType(bind_type)
            self.bindings = [
                b for b in self.bindings
                if not (b.bind_type == bind_type_enum and b.pattern == pattern)
            ]
            logger.info(f"Removed binding: {bind_type} {pattern}")
        except ValueError:
            logger.error(f"Invalid bind type: {bind_type}")

    def _check_permissions(self, nick: str, flags: str) -> bool:
        """Check user permissions against flags."""
        # Simplified permission check
        # Format: "channel_flags|global_flags"
        # -|- means any user
        if flags == "-|-":
            return True

        user_level = self.user_levels.get(nick, "user")
        # Add more sophisticated permission logic here
        return True

    def _check_cooldown(self, binding: Binding) -> bool:
        """Check if cooldown has expired."""
        if binding.cooldown is None:
            return True

        import time
        now = time.time()
        if binding.last_triggered is None:
            binding.last_triggered = now
            return True

        if now - binding.last_triggered >= binding.cooldown:
            binding.last_triggered = now
            return True

        return False

    def _execute_handler(self, binding: Binding, connection, event, args):
        """Execute a binding handler."""
        try:
            binding.handler(connection, event, args)
            
            # Update stats
            key = f"{binding.bind_type.value}:{binding.pattern}"
            self.command_stats[key] = self.command_stats.get(key, 0) + 1
            
        except Exception as e:
            logger.error(f"Error executing handler for {binding.pattern}: {e}")

    def set_user_level(self, nick: str, level: str):
        """Set user permission level."""
        self.user_levels[nick] = level
        logger.info(f"Set user level: {nick} -> {level}")

    def get_stats(self) -> Dict[str, Any]:
        """Get bot statistics."""
        return {
            "bindings_count": len(self.bindings),
            "command_stats": self.command_stats,
            "users_tracked": len(self.user_levels),
        }


def create_bot(server: str, port: int, nickname: str, channels: List[str]) -> IRCBot:
    """Factory function to create an IRC bot."""
    return IRCBot(server, port, nickname, channels)
