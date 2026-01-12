"""
Folder structure generator for plugins.
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class FolderGenerator:
    """Generate plugin folder structures with proper permissions."""
    
    def __init__(self, base_dir: str = "/opt/masterchief/plugins"):
        """
        Initialize folder generator.
        
        Args:
            base_dir: Base directory for plugins
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_structure(self, plugin_name: str) -> Path:
        """
        Generate plugin folder structure.
        
        Structure:
            plugins/{plugin_name}/
            ├── src/                 # Source code
            ├── logs/                # Plugin logs
            ├── config/              # Configuration files
            │   ├── plugin.yaml      # Main config
            │   └── {type}_config.yaml  # Type-specific config
            ├── tests/               # Test files
            └── README.md            # Auto-generated documentation
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Path to plugin directory
        """
        plugin_path = self.base_dir / plugin_name
        
        if plugin_path.exists():
            logger.warning(f"Plugin directory already exists: {plugin_path}")
            raise ValueError(f"Plugin '{plugin_name}' already exists")
        
        # Create main plugin directory
        plugin_path.mkdir(parents=True, exist_ok=True)
        self._set_permissions(plugin_path, 0o755)
        logger.info(f"Created plugin directory: {plugin_path}")
        
        # Create subdirectories
        subdirs = ['src', 'logs', 'config', 'tests']
        for subdir in subdirs:
            dir_path = plugin_path / subdir
            dir_path.mkdir(parents=True, exist_ok=True)
            self._set_permissions(dir_path, 0o755)
            logger.info(f"Created subdirectory: {dir_path}")
        
        # Create empty __init__.py for Python packages
        init_file = plugin_path / 'src' / '__init__.py'
        init_file.touch()
        self._set_permissions(init_file, 0o644)
        
        # Create placeholder README.md
        readme_path = plugin_path / 'README.md'
        self._create_readme(readme_path, plugin_name)
        self._set_permissions(readme_path, 0o644)
        
        # Create .gitignore
        gitignore_path = plugin_path / '.gitignore'
        self._create_gitignore(gitignore_path)
        self._set_permissions(gitignore_path, 0o644)
        
        logger.info(f"Plugin structure created successfully: {plugin_path}")
        return plugin_path
    
    def _set_permissions(self, path: Path, mode: int):
        """
        Set file/directory permissions.
        
        Args:
            path: Path to file/directory
            mode: Permission mode (e.g., 0o755, 0o644)
        """
        try:
            os.chmod(path, mode)
            logger.debug(f"Set permissions {oct(mode)} on {path}")
        except Exception as e:
            logger.warning(f"Could not set permissions on {path}: {e}")
    
    def _create_readme(self, path: Path, plugin_name: str):
        """
        Create README.md file.
        
        Args:
            path: Path to README.md
            plugin_name: Plugin name
        """
        content = f"""# {plugin_name}

## Description

Plugin created with MasterChief Plugin Wizard.

## Installation

```bash
# Plugin installation instructions
```

## Usage

```bash
# Plugin usage examples
```

## Configuration

See `config/plugin.yaml` for configuration options.

## Development

```bash
# Development setup
cd {plugin_name}
```

## Testing

```bash
# Run tests
cd tests
```

## License

MIT License
"""
        path.write_text(content)
        logger.info(f"Created README.md: {path}")
    
    def _create_gitignore(self, path: Path):
        """
        Create .gitignore file.
        
        Args:
            path: Path to .gitignore
        """
        content = """# Logs
logs/
*.log

# Virtual environments
.venv/
venv/
env/

# Python
__pycache__/
*.py[cod]
*.so
.Python

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
"""
        path.write_text(content)
        logger.info(f"Created .gitignore: {path}")
