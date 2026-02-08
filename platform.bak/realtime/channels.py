"""WebSocket channel definitions."""
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class Channel(Enum):
    """WebSocket channel names."""
    DEPLOYMENTS = "deployments"
    LOGS = "logs"
    METRICS = "metrics"
    PLUGINS = "plugins"
    ALERTS = "alerts"
    WIZARD = "wizard"
    CHAT = "chat"
    SYSTEM = "system"


@dataclass
class ChannelConfig:
    """Channel configuration."""
    name: str
    description: str
    requires_auth: bool = False
    max_subscribers: Optional[int] = None


# Channel configurations
CHANNELS = {
    Channel.DEPLOYMENTS.value: ChannelConfig(
        name=Channel.DEPLOYMENTS.value,
        description="Real-time deployment updates",
        requires_auth=True
    ),
    Channel.LOGS.value: ChannelConfig(
        name=Channel.LOGS.value,
        description="Live log streaming",
        requires_auth=True
    ),
    Channel.METRICS.value: ChannelConfig(
        name=Channel.METRICS.value,
        description="System metrics stream",
        requires_auth=True
    ),
    Channel.PLUGINS.value: ChannelConfig(
        name=Channel.PLUGINS.value,
        description="Plugin status updates",
        requires_auth=True
    ),
    Channel.ALERTS.value: ChannelConfig(
        name=Channel.ALERTS.value,
        description="System alerts",
        requires_auth=True
    ),
    Channel.WIZARD.value: ChannelConfig(
        name=Channel.WIZARD.value,
        description="Wizard progress updates",
        requires_auth=True
    ),
    Channel.CHAT.value: ChannelConfig(
        name=Channel.CHAT.value,
        description="IRC bot messages relay",
        requires_auth=False
    ),
    Channel.SYSTEM.value: ChannelConfig(
        name=Channel.SYSTEM.value,
        description="System events",
        requires_auth=True
    ),
}


def is_valid_channel(channel_name: str) -> bool:
    """Check if channel name is valid."""
    return channel_name in CHANNELS


def get_channel_config(channel_name: str) -> Optional[ChannelConfig]:
    """Get configuration for a channel."""
    return CHANNELS.get(channel_name)
