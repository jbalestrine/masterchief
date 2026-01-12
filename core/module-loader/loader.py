"""
Module Loader - Dynamic module discovery and loading system
Handles registration, discovery, and lifecycle management of platform modules
"""

import os
import yaml
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ModuleManifest:
    """Module manifest data structure"""
    name: str
    version: str
    type: str  # terraform, ansible, powershell-dsc
    description: str
    author: str
    dependencies: List[str]
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    metadata: Dict[str, Any]
    path: Path


class ModuleLoader:
    """
    Dynamic module loader that discovers and manages platform modules
    """
    
    def __init__(self, modules_dir: str = "modules"):
        """
        Initialize the module loader
        
        Args:
            modules_dir: Directory containing modules
        """
        self.modules_dir = Path(modules_dir)
        self.modules: Dict[str, ModuleManifest] = {}
        self.loaded_modules: Dict[str, Any] = {}
        
    def discover_modules(self) -> List[ModuleManifest]:
        """
        Discover all modules in the modules directory
        
        Returns:
            List of discovered module manifests
        """
        discovered = []
        
        if not self.modules_dir.exists():
            logger.warning(f"Modules directory {self.modules_dir} does not exist")
            return discovered
            
        # Walk through modules directory
        for module_type_dir in self.modules_dir.iterdir():
            if not module_type_dir.is_dir() or module_type_dir.name == 'templates':
                continue
                
            # Look for modules in each type directory
            for module_dir in module_type_dir.iterdir():
                if not module_dir.is_dir():
                    continue
                    
                # Look for manifest file (module.yaml or module.json)
                manifest_path = self._find_manifest(module_dir)
                if manifest_path:
                    try:
                        manifest = self._load_manifest(manifest_path, module_dir)
                        discovered.append(manifest)
                        self.modules[manifest.name] = manifest
                        logger.info(f"Discovered module: {manifest.name} (v{manifest.version})")
                    except Exception as e:
                        logger.error(f"Error loading manifest from {manifest_path}: {e}")
                        
        return discovered
    
    def _find_manifest(self, module_dir: Path) -> Optional[Path]:
        """Find manifest file in module directory"""
        for filename in ['module.yaml', 'module.yml', 'module.json']:
            manifest_path = module_dir / filename
            if manifest_path.exists():
                return manifest_path
        return None
    
    def _load_manifest(self, manifest_path: Path, module_dir: Path) -> ModuleManifest:
        """
        Load and parse module manifest
        
        Args:
            manifest_path: Path to manifest file
            module_dir: Module directory path
            
        Returns:
            Parsed ModuleManifest object
        """
        with open(manifest_path, 'r') as f:
            if manifest_path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        
        return ModuleManifest(
            name=data['name'],
            version=data['version'],
            type=data['type'],
            description=data.get('description', ''),
            author=data.get('author', ''),
            dependencies=data.get('dependencies', []),
            inputs=data.get('inputs', {}),
            outputs=data.get('outputs', {}),
            metadata=data.get('metadata', {}),
            path=module_dir
        )
    
    def load_module(self, module_name: str) -> Any:
        """
        Load a specific module by name
        
        Args:
            module_name: Name of the module to load
            
        Returns:
            Loaded module object
        """
        if module_name in self.loaded_modules:
            return self.loaded_modules[module_name]
            
        if module_name not in self.modules:
            raise ValueError(f"Module {module_name} not found. Run discover_modules() first.")
            
        manifest = self.modules[module_name]
        
        # Load dependencies first
        for dep in manifest.dependencies:
            if dep not in self.loaded_modules:
                self.load_module(dep)
        
        # Load the module based on type
        module_obj = self._load_module_by_type(manifest)
        self.loaded_modules[module_name] = module_obj
        
        logger.info(f"Loaded module: {module_name}")
        return module_obj
    
    def _load_module_by_type(self, manifest: ModuleManifest) -> Any:
        """Load module based on its type"""
        if manifest.type == 'terraform':
            return self._load_terraform_module(manifest)
        elif manifest.type == 'ansible':
            return self._load_ansible_module(manifest)
        elif manifest.type == 'powershell-dsc':
            return self._load_dsc_module(manifest)
        else:
            logger.warning(f"Unknown module type: {manifest.type}")
            return manifest
    
    def _load_terraform_module(self, manifest: ModuleManifest) -> Dict[str, Any]:
        """Load Terraform module"""
        return {
            'type': 'terraform',
            'manifest': manifest,
            'path': manifest.path,
            'main_tf': manifest.path / 'main.tf',
            'variables_tf': manifest.path / 'variables.tf',
            'outputs_tf': manifest.path / 'outputs.tf'
        }
    
    def _load_ansible_module(self, manifest: ModuleManifest) -> Dict[str, Any]:
        """Load Ansible module"""
        return {
            'type': 'ansible',
            'manifest': manifest,
            'path': manifest.path,
            'playbook': manifest.path / 'playbook.yml',
            'roles': manifest.path / 'roles'
        }
    
    def _load_dsc_module(self, manifest: ModuleManifest) -> Dict[str, Any]:
        """Load PowerShell DSC module"""
        return {
            'type': 'powershell-dsc',
            'manifest': manifest,
            'path': manifest.path,
            'configuration': manifest.path / 'Configuration.ps1'
        }
    
    def get_module(self, module_name: str) -> Optional[ModuleManifest]:
        """Get module manifest by name"""
        return self.modules.get(module_name)
    
    def list_modules(self, module_type: Optional[str] = None) -> List[ModuleManifest]:
        """
        List all discovered modules, optionally filtered by type
        
        Args:
            module_type: Optional filter by module type
            
        Returns:
            List of module manifests
        """
        if module_type:
            return [m for m in self.modules.values() if m.type == module_type]
        return list(self.modules.values())
    
    def validate_dependencies(self, module_name: str) -> tuple[bool, List[str]]:
        """
        Validate that all dependencies for a module are available
        
        Args:
            module_name: Name of the module to validate
            
        Returns:
            Tuple of (is_valid, missing_dependencies)
        """
        if module_name not in self.modules:
            return False, [module_name]
            
        manifest = self.modules[module_name]
        missing = []
        
        for dep in manifest.dependencies:
            if dep not in self.modules:
                missing.append(dep)
            else:
                # Recursively check dependencies
                is_valid, sub_missing = self.validate_dependencies(dep)
                if not is_valid:
                    missing.extend(sub_missing)
        
        return len(missing) == 0, missing
