"""Core module loader for MasterChief platform."""
import importlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class ModuleManifest:
    """Module manifest schema."""

    def __init__(self, data: Dict[str, Any]):
        self.name = data.get("name", "")
        self.version = data.get("version", "1.0.0")
        self.description = data.get("description", "")
        self.author = data.get("author", "")
        self.dependencies = data.get("dependencies", [])
        self.inputs = data.get("inputs", {})
        self.outputs = data.get("outputs", {})
        self.module_type = data.get("type", "generic")
        self.entry_point = data.get("entry_point", "")
        self.config_schema = data.get("config_schema", {})

    @classmethod
    def from_file(cls, manifest_path: Path) -> "ModuleManifest":
        """Load manifest from YAML or JSON file."""
        with open(manifest_path, "r") as f:
            if manifest_path.suffix in [".yaml", ".yml"]:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        return cls(data)


class Module:
    """Base module class."""

    def __init__(self, manifest: ModuleManifest, path: Path):
        self.manifest = manifest
        self.path = path
        self.instance = None
        self.loaded = False

    def load(self) -> bool:
        """Load the module."""
        try:
            if self.manifest.entry_point:
                module_path = f"{self.path.parent.name}.{self.path.name}.{self.manifest.entry_point}"
                mod = importlib.import_module(module_path)
                self.instance = mod
                self.loaded = True
                logger.info(f"Loaded module: {self.manifest.name} v{self.manifest.version}")
                return True
            else:
                logger.warning(f"No entry point defined for module: {self.manifest.name}")
                return False
        except Exception as e:
            logger.error(f"Failed to load module {self.manifest.name}: {e}")
            return False

    def unload(self) -> bool:
        """Unload the module."""
        self.instance = None
        self.loaded = False
        logger.info(f"Unloaded module: {self.manifest.name}")
        return True

    def reload(self) -> bool:
        """Reload the module (hot-reload)."""
        if self.unload():
            return self.load()
        return False


class ModuleLoader:
    """Dynamic module loader with hot-reload capabilities."""

    def __init__(self, module_dirs: Optional[List[Path]] = None):
        self.module_dirs = module_dirs or []
        self.modules: Dict[str, Module] = {}
        self.load_order: List[str] = []

    def discover_modules(self) -> List[Path]:
        """Discover modules in configured directories."""
        discovered = []
        for module_dir in self.module_dirs:
            if not module_dir.exists():
                logger.warning(f"Module directory does not exist: {module_dir}")
                continue

            for item in module_dir.iterdir():
                if item.is_dir():
                    manifest_paths = [
                        item / "manifest.yaml",
                        item / "manifest.yml",
                        item / "manifest.json",
                    ]
                    for manifest_path in manifest_paths:
                        if manifest_path.exists():
                            discovered.append(manifest_path)
                            break

        logger.info(f"Discovered {len(discovered)} modules")
        return discovered

    def resolve_dependencies(self, modules: List[Module]) -> List[str]:
        """Resolve module dependencies and determine load order."""
        # Simple topological sort for dependency resolution
        graph = {m.manifest.name: m.manifest.dependencies for m in modules}
        visited = set()
        order = []

        def visit(name: str):
            if name in visited:
                return
            visited.add(name)
            if name in graph:
                for dep in graph[name]:
                    visit(dep)
            order.append(name)

        for name in graph:
            visit(name)

        return order

    def register_module(self, manifest_path: Path) -> bool:
        """Register a module from its manifest."""
        try:
            manifest = ModuleManifest.from_file(manifest_path)
            module = Module(manifest, manifest_path.parent)
            self.modules[manifest.name] = module
            logger.info(f"Registered module: {manifest.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register module from {manifest_path}: {e}")
            return False

    def load_modules(self) -> bool:
        """Load all registered modules in dependency order."""
        if not self.modules:
            logger.warning("No modules registered")
            return False

        # Resolve dependencies
        self.load_order = self.resolve_dependencies(list(self.modules.values()))

        # Load modules in order
        success = True
        for module_name in self.load_order:
            if module_name in self.modules:
                if not self.modules[module_name].load():
                    success = False
                    logger.error(f"Failed to load module: {module_name}")

        return success

    def unload_module(self, module_name: str) -> bool:
        """Unload a specific module."""
        if module_name in self.modules:
            return self.modules[module_name].unload()
        return False

    def reload_module(self, module_name: str) -> bool:
        """Reload a specific module (hot-reload)."""
        if module_name in self.modules:
            return self.modules[module_name].reload()
        return False

    def get_module(self, module_name: str) -> Optional[Module]:
        """Get a loaded module by name."""
        return self.modules.get(module_name)

    def list_modules(self) -> List[Dict[str, Any]]:
        """List all registered modules."""
        return [
            {
                "name": m.manifest.name,
                "version": m.manifest.version,
                "description": m.manifest.description,
                "loaded": m.loaded,
                "type": m.manifest.module_type,
            }
            for m in self.modules.values()
        ]


def create_module_sdk():
    """Create SDK utilities for module development."""
    return {
        "ModuleManifest": ModuleManifest,
        "Module": Module,
        "ModuleLoader": ModuleLoader,
    }
