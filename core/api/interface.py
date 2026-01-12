"""
Module API - Internal API for module communication
Provides standardized interfaces for inter-module communication
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ModuleState(Enum):
    """Module lifecycle states"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ModuleMessage:
    """Message structure for inter-module communication"""
    source: str
    target: str
    action: str
    payload: Dict[str, Any]
    reply_to: Optional[str] = None


class ModuleAPI:
    """
    Internal API for module communication and lifecycle management
    """
    
    def __init__(self):
        """Initialize the module API"""
        self.modules: Dict[str, Dict[str, Any]] = {}
        self.message_handlers: Dict[str, List[Callable]] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
    
    def register_module(self, 
                       module_name: str, 
                       module_type: str,
                       interface: Dict[str, Any]) -> None:
        """
        Register a module with the API
        
        Args:
            module_name: Unique module name
            module_type: Module type (terraform, ansible, powershell-dsc)
            interface: Module interface definition
        """
        self.modules[module_name] = {
            'name': module_name,
            'type': module_type,
            'state': ModuleState.UNINITIALIZED,
            'interface': interface,
            'metadata': {}
        }
        logger.info(f"Registered module: {module_name} ({module_type})")
    
    def unregister_module(self, module_name: str) -> None:
        """
        Unregister a module from the API
        
        Args:
            module_name: Module name to unregister
        """
        if module_name in self.modules:
            del self.modules[module_name]
            logger.info(f"Unregistered module: {module_name}")
    
    def get_module_state(self, module_name: str) -> Optional[ModuleState]:
        """
        Get the current state of a module
        
        Args:
            module_name: Module name
            
        Returns:
            Current module state or None
        """
        if module_name in self.modules:
            return self.modules[module_name]['state']
        return None
    
    def set_module_state(self, module_name: str, state: ModuleState) -> None:
        """
        Set the state of a module
        
        Args:
            module_name: Module name
            state: New module state
        """
        if module_name in self.modules:
            old_state = self.modules[module_name]['state']
            self.modules[module_name]['state'] = state
            logger.debug(f"Module {module_name} state: {old_state} -> {state}")
            
            # Trigger state change event
            self._trigger_event(f"module.{module_name}.state_change", {
                'module': module_name,
                'old_state': old_state.value,
                'new_state': state.value
            })
    
    def send_message(self, message: ModuleMessage) -> Optional[Any]:
        """
        Send a message to a module
        
        Args:
            message: ModuleMessage object
            
        Returns:
            Response from the target module or None
        """
        if message.target not in self.modules:
            logger.error(f"Target module {message.target} not found")
            return None
        
        # Get message handlers for the target module
        handler_key = f"{message.target}.{message.action}"
        
        if handler_key in self.message_handlers:
            responses = []
            for handler in self.message_handlers[handler_key]:
                try:
                    response = handler(message)
                    responses.append(response)
                except Exception as e:
                    logger.error(f"Error in message handler {handler_key}: {e}")
            
            return responses[0] if len(responses) == 1 else responses
        
        logger.warning(f"No handler found for {handler_key}")
        return None
    
    def register_message_handler(self,
                                 module_name: str,
                                 action: str,
                                 handler: Callable) -> None:
        """
        Register a message handler for a module
        
        Args:
            module_name: Module name
            action: Action to handle
            handler: Handler function
        """
        handler_key = f"{module_name}.{action}"
        
        if handler_key not in self.message_handlers:
            self.message_handlers[handler_key] = []
        
        self.message_handlers[handler_key].append(handler)
        logger.debug(f"Registered message handler: {handler_key}")
    
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        Register an event handler
        
        Args:
            event_type: Type of event to handle
            handler: Handler function
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.debug(f"Registered event handler: {event_type}")
    
    def _trigger_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Trigger an event
        
        Args:
            event_type: Type of event
            data: Event data
        """
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Error in event handler {event_type}: {e}")
    
    def get_module_interface(self, module_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the interface definition for a module
        
        Args:
            module_name: Module name
            
        Returns:
            Module interface or None
        """
        if module_name in self.modules:
            return self.modules[module_name]['interface']
        return None
    
    def list_modules(self, module_type: Optional[str] = None) -> List[str]:
        """
        List registered modules
        
        Args:
            module_type: Optional filter by module type
            
        Returns:
            List of module names
        """
        if module_type:
            return [
                name for name, info in self.modules.items()
                if info['type'] == module_type
            ]
        return list(self.modules.keys())
    
    def call_module_method(self,
                          module_name: str,
                          method: str,
                          **kwargs) -> Any:
        """
        Call a method on a module's interface
        
        Args:
            module_name: Module name
            method: Method name to call
            **kwargs: Method arguments
            
        Returns:
            Method return value
        """
        if module_name not in self.modules:
            raise ValueError(f"Module {module_name} not registered")
        
        interface = self.modules[module_name]['interface']
        
        if method not in interface:
            raise ValueError(f"Method {method} not found in module {module_name} interface")
        
        method_func = interface[method]
        
        if not callable(method_func):
            raise ValueError(f"Method {method} is not callable")
        
        try:
            return method_func(**kwargs)
        except Exception as e:
            logger.error(f"Error calling {module_name}.{method}: {e}")
            raise
    
    def get_module_metadata(self, module_name: str) -> Optional[Dict[str, Any]]:
        """
        Get module metadata
        
        Args:
            module_name: Module name
            
        Returns:
            Module metadata or None
        """
        if module_name in self.modules:
            return self.modules[module_name]['metadata']
        return None
    
    def set_module_metadata(self,
                           module_name: str,
                           key: str,
                           value: Any) -> None:
        """
        Set module metadata
        
        Args:
            module_name: Module name
            key: Metadata key
            value: Metadata value
        """
        if module_name in self.modules:
            self.modules[module_name]['metadata'][key] = value


# Global API instance
_module_api: Optional[ModuleAPI] = None


def get_module_api() -> ModuleAPI:
    """
    Get the global module API instance
    
    Returns:
        ModuleAPI instance
    """
    global _module_api
    if _module_api is None:
        _module_api = ModuleAPI()
    return _module_api
