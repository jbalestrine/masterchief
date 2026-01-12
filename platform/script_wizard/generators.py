"""
Script Generators - Generate scripts from templates
"""

import logging
from pathlib import Path
from typing import Dict, Any
from .templates import get_template

logger = logging.getLogger(__name__)


class ScriptGenerator:
    """Generate scripts from templates with validation."""
    
    def __init__(self):
        """Initialize the script generator."""
        self.generated_scripts = []
    
    def generate(self, template_id: str, parameters: Dict[str, Any],
                output_path: str = None) -> str:
        """
        Generate a script from a template.
        
        Args:
            template_id: Template identifier
            parameters: Script parameters
            output_path: Optional path to save the script
            
        Returns:
            Generated script content
        """
        logger.info(f"Generating script from template: {template_id}")
        
        # Get template
        template = get_template(template_id)
        
        # Validate parameters
        if not self._validate_parameters(template, parameters):
            raise ValueError("Invalid parameters for template")
        
        # Render script
        script_content = template.render(parameters)
        
        # Save if path provided
        if output_path:
            try:
                # Validate output path
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'w') as f:
                    f.write(script_content)
                logger.info(f"Script saved to: {output_path}")
            except (IOError, OSError) as e:
                logger.error(f"Failed to save script: {e}")
                raise IOError(f"Cannot write to {output_path}: {e}")
        
        # Track generated script
        self.generated_scripts.append({
            "template_id": template_id,
            "parameters": parameters,
            "output_path": output_path
        })
        
        return script_content
    
    def _validate_parameters(self, template: Any, parameters: Dict[str, Any]) -> bool:
        """
        Validate parameters against template requirements.
        
        Args:
            template: Template instance
            parameters: Parameters to validate
            
        Returns:
            True if valid, False otherwise
        """
        for param in template.parameters:
            if param["required"] and param["name"] not in parameters:
                logger.error(f"Missing required parameter: {param['name']}")
                return False
        return True
    
    def list_generated(self) -> list:
        """
        List all generated scripts in this session.
        
        Returns:
            List of generated script information
        """
        return self.generated_scripts
