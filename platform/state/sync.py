"""Cross-component state synchronization."""
import logging
import asyncio
from typing import Callable, Dict, Any, List
from platform.event_bus import Event, get_event_bus

logger = logging.getLogger(__name__)


class StateSynchronizer:
    """Synchronizes state changes across components via event bus."""
    
    def __init__(self, state_store, event_bus=None):
        self.state_store = state_store
        self.event_bus = event_bus or get_event_bus()
        self.change_handlers: Dict[str, List[Callable]] = {}
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Set up event handlers for state changes."""
        self.event_bus.subscribe("config.changed", self._on_config_changed)
        self.event_bus.subscribe("deployment.progress", self._on_deployment_progress)
        self.event_bus.subscribe("plugin.configured", self._on_plugin_configured)
    
    async def _on_config_changed(self, event: Event):
        """Handle configuration change events."""
        config_key = event.data.get("config_key")
        config_value = event.data.get("config_value")
        
        if config_key:
            await self.state_store.set(f"config:{config_key}", config_value)
            await self._notify_handlers(f"config:{config_key}", config_value)
    
    async def _on_deployment_progress(self, event: Event):
        """Handle deployment progress events."""
        deployment_id = event.data.get("deployment_id")
        progress = event.data.get("progress")
        
        if deployment_id:
            state_key = f"deployment:{deployment_id}"
            current_state = await self.state_store.get(state_key, {})
            current_state["progress"] = progress
            current_state["message"] = event.data.get("message", "")
            await self.state_store.set(state_key, current_state)
    
    async def _on_plugin_configured(self, event: Event):
        """Handle plugin configuration events."""
        plugin_id = event.data.get("plugin_id")
        config = event.data.get("configuration")
        
        if plugin_id:
            state_key = f"plugin:{plugin_id}"
            current_state = await self.state_store.get(state_key, {})
            current_state["configuration"] = config
            await self.state_store.set(state_key, current_state)
    
    def register_change_handler(self, key_pattern: str, handler: Callable):
        """Register a handler for state changes matching a pattern."""
        if key_pattern not in self.change_handlers:
            self.change_handlers[key_pattern] = []
        self.change_handlers[key_pattern].append(handler)
        logger.info(f"Registered change handler for pattern: {key_pattern}")
    
    async def _notify_handlers(self, key: str, value: Any):
        """Notify registered handlers of state changes."""
        for pattern, handlers in self.change_handlers.items():
            if self._matches_pattern(key, pattern):
                for handler in handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(key, value)
                        else:
                            handler(key, value)
                    except Exception as e:
                        logger.error(f"Error in change handler: {e}")
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches pattern (simple wildcard support)."""
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            return key.startswith(pattern[:-1])
        return key == pattern
    
    async def sync_state(self, key: str, value: Any):
        """
        Manually sync state and notify listeners.
        
        Args:
            key: State key
            value: New value
        """
        await self.state_store.set(key, value)
        await self._notify_handlers(key, value)
        
        # Publish change event
        event = Event(
            type="state.changed",
            source="synchronizer",
            data={"key": key, "value": value}
        )
        await self.event_bus.publish(event)
