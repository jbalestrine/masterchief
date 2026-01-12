"""
Script Templates - Predefined templates for script generation
"""

from typing import Dict, List, Any


class ScriptTemplate:
    """Base class for script templates."""
    
    def __init__(self, template_id: str, name: str, description: str):
        """
        Initialize a script template.
        
        Args:
            template_id: Unique template identifier
            name: Template name
            description: Template description
        """
        self.template_id = template_id
        self.name = name
        self.description = description
        self.parameters: List[Dict[str, Any]] = []
    
    def add_parameter(self, name: str, param_type: str, required: bool = True,
                     default: Any = None, description: str = "") -> None:
        """
        Add a parameter to the template.
        
        Args:
            name: Parameter name
            param_type: Parameter type (string, int, bool, etc.)
            required: Whether parameter is required
            default: Default value
            description: Parameter description
        """
        self.parameters.append({
            "name": name,
            "type": param_type,
            "required": required,
            "default": default,
            "description": description
        })
    
    def render(self, parameters: Dict[str, Any]) -> str:
        """
        Render the template with given parameters.
        
        Args:
            parameters: Parameter values
            
        Returns:
            Rendered script content
        """
        raise NotImplementedError("Subclasses must implement render()")


class DeploymentTemplate(ScriptTemplate):
    """Template for deployment scripts."""
    
    def __init__(self):
        super().__init__(
            "deployment",
            "Deployment Script",
            "Deploy applications to environments"
        )
        self.add_parameter("app_name", "string", True, description="Application name")
        self.add_parameter("environment", "string", True, description="Target environment")
    
    def render(self, parameters: Dict[str, Any]) -> str:
        """Render deployment script."""
        app_name = parameters.get("app_name", "app")
        environment = parameters.get("environment", "dev")
        
        return f"""#!/usr/bin/env bash
set -euo pipefail

# Deploy {app_name} to {environment}
echo "[INFO] Deploying {app_name} to {environment}"
echo "[INFO] Deployment completed"
exit 0
"""


class MonitoringTemplate(ScriptTemplate):
    """Template for monitoring scripts."""
    
    def __init__(self):
        super().__init__(
            "monitoring",
            "Monitoring Script",
            "Monitor system health and metrics"
        )
        self.add_parameter("target", "string", True, description="Monitoring target")
    
    def render(self, parameters: Dict[str, Any]) -> str:
        """Render monitoring script."""
        target = parameters.get("target", "localhost")
        
        return f"""#!/usr/bin/env bash
set -euo pipefail

# Monitor {target}
echo "[INFO] Monitoring {target}"
echo "[INFO] Monitoring check completed"
exit 0
"""


def get_template(template_id: str) -> ScriptTemplate:
    """
    Get a template by ID.
    
    Args:
        template_id: Template identifier
        
    Returns:
        Template instance
    """
    templates = {
        "deployment": DeploymentTemplate(),
        "monitoring": MonitoringTemplate()
    }
    return templates.get(template_id, DeploymentTemplate())
