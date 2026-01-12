"""
Script Template Manager
Pre-built templates for common DevOps tasks
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template

logger = logging.getLogger(__name__)


class ScriptTemplates:
    """Manage script templates with variable substitution."""
    
    def __init__(self, templates_dir: Optional[Path] = None, custom_dir: Optional[Path] = None):
        """
        Initialize template manager.
        
        Args:
            templates_dir: Path to built-in templates directory
            custom_dir: Path to custom templates directory
        """
        if templates_dir is None:
            templates_dir = Path(__file__).parent
        
        self.templates_dir = Path(templates_dir)
        self.custom_dir = Path(custom_dir) if custom_dir else None
        
        # Create Jinja2 environment
        loader = FileSystemLoader([str(self.templates_dir)])
        if self.custom_dir and self.custom_dir.exists():
            loader = FileSystemLoader([str(self.templates_dir), str(self.custom_dir)])
        
        self.env = Environment(loader=loader, autoescape=False)
    
    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, str]]:
        """
        List available templates.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of template information dictionaries
        """
        templates = []
        
        search_dirs = [self.templates_dir]
        if self.custom_dir and self.custom_dir.exists():
            search_dirs.append(self.custom_dir)
        
        for base_dir in search_dirs:
            if not base_dir.exists():
                continue
                
            for template_file in base_dir.rglob("*.j2"):
                rel_path = template_file.relative_to(base_dir)
                template_category = rel_path.parent.name
                
                if category and template_category != category:
                    continue
                
                template_name = rel_path.stem  # Remove .j2 extension
                template_path = f"{template_category}/{template_name}"
                
                templates.append({
                    "name": template_name,
                    "category": template_category,
                    "path": template_path,
                    "full_path": str(template_file)
                })
        
        return templates
    
    def get(self, template_path: str, variables: Optional[Dict[str, Any]] = None) -> str:
        """
        Get a template with variable substitution.
        
        Args:
            template_path: Path to template (e.g., "backup/postgres")
            variables: Dictionary of variables to substitute
            
        Returns:
            Rendered template content
        """
        try:
            # Add .j2 extension if not present
            if not template_path.endswith(".j2"):
                # Try different extensions
                for ext in [".sh.j2", ".py.j2", ".ps1.j2"]:
                    try:
                        template = self.env.get_template(f"{template_path}{ext}")
                        break
                    except:
                        continue
                else:
                    raise ValueError(f"Template not found: {template_path}")
            else:
                template = self.env.get_template(template_path)
            
            # Render with variables
            variables = variables or {}
            rendered = template.render(**variables)
            
            return rendered
            
        except Exception as e:
            logger.error(f"Failed to render template {template_path}: {e}")
            raise
    
    def get_variables(self, template_path: str) -> List[str]:
        """
        Get list of variables required by a template.
        
        Args:
            template_path: Path to template
            
        Returns:
            List of variable names
        """
        # Return empty list if nodes module not available
        if nodes is None:
            logger.warning("Jinja2 nodes module not available, cannot parse template variables")
            return []
        
        try:
            # Load template source
            if not template_path.endswith(".j2"):
                for ext in [".sh.j2", ".py.j2", ".ps1.j2"]:
                    try:
                        source = self.env.loader.get_source(self.env, f"{template_path}{ext}")[0]
                        break
                    except:
                        continue
                else:
                    raise ValueError(f"Template not found: {template_path}")
            else:
                source = self.env.loader.get_source(self.env, template_path)[0]
            
            # Parse template to find variables
            parsed = self.env.parse(source)
            variables = list(parsed.find_all(nodes.Name))
            
            # Return unique variable names
            return list(set(var.name for var in variables))
            
        except Exception as e:
            logger.error(f"Failed to get variables for template {template_path}: {e}")
            return []
    
    def save_custom_template(self, name: str, category: str, content: str) -> bool:
        """
        Save a custom template.
        
        Args:
            name: Template name
            category: Template category
            content: Template content
            
        Returns:
            True if saved successfully
        """
        try:
            if not self.custom_dir:
                raise ValueError("Custom templates directory not configured")
            
            # Create category directory
            category_dir = self.custom_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            # Save template
            template_path = category_dir / f"{name}.j2"
            template_path.write_text(content)
            
            logger.info(f"Saved custom template: {category}/{name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save custom template: {e}")
            return False
    
    def get_categories(self) -> List[str]:
        """
        Get list of available template categories.
        
        Returns:
            List of category names
        """
        categories = set()
        
        search_dirs = [self.templates_dir]
        if self.custom_dir and self.custom_dir.exists():
            search_dirs.append(self.custom_dir)
        
        for base_dir in search_dirs:
            if not base_dir.exists():
                continue
                
            for item in base_dir.iterdir():
                if item.is_dir() and not item.name.startswith("_"):
                    categories.add(item.name)
        
        return sorted(list(categories))


# Import for template parsing
try:
    from jinja2 import nodes
except ImportError:
    nodes = None
