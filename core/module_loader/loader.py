"""Module loader for dynamic module management.

This module provides functionality for loading and managing modules dynamically.
"""

from typing import Any, Dict, List


class Module:
    """Represents a loadable module."""
    
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.loaded = False
    
    def load(self) -> bool:
        """Load the module."""
        self.loaded = True
        return True
    
    def unload(self) -> bool:
        """Unload the module."""
        self.loaded = False
        return True


class ModuleLoader:
    """Loads and manages modules dynamically."""
    
    def __init__(self):
        self.modules: Dict[str, Module] = {}
    
    def load_module(self, name: str, path: str) -> bool:
        """Load a module by name and path.
        
        Args:
            name: The module name
            path: The path to the module
            
        Returns:
            True if the module was loaded successfully
        """
        if name in self.modules:
            return False
        
        module = Module(name, path)
        if module.load():
            self.modules[name] = module
            return True
        return False
    
    def get_module(self, name: str) -> Module:
        """Get a loaded module by name.
        
        Args:
            name: The module name
            
        Returns:
            The module if found, None otherwise
        """
        # Line 65 - Type error: incompatible type assignment
        module: Module = None  # Wrong - should be Optional[Module]
        
        if name in self.modules:
            module = self.modules[name]
        
        return module
    
    def unload_module(self, name: str) -> bool:
        """Unload a module by name.
        
        Args:
            name: The module name
            
        Returns:
            True if the module was unloaded successfully
        """
        if name not in self.modules:
            return False
        
        module = self.modules[name]
        if module.unload():
            del self.modules[name]
            return True
        return False
    
    def list_modules(self) -> List[str]:
        """List all loaded modules.
        
        Returns:
            A list of loaded module names
        """
        return list(self.modules.keys())
