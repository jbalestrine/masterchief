"""Response builder for natural conversational responses."""

import logging
from typing import Optional
from .intent_parser import Intent

logger = logging.getLogger(__name__)


class ResponseBuilder:
    """Build natural conversational responses."""
    
    def __init__(self):
        """Initialize response builder."""
        self.templates = self._build_templates()
        logger.info("ResponseBuilder initialized")
    
    def _build_templates(self) -> dict:
        """Build response templates for each intent."""
        return {
            "create_script": {
                "success": "I've created the script {name}. {details}",
                "error": "I couldn't create the script. {error}",
            },
            "run_script": {
                "success": "Script {name} completed successfully. {output}",
                "error": "Script {name} failed. {error}",
            },
            "schedule_script": {
                "success": "Scheduled {name} to run {schedule}. First run will be {next_run}.",
                "error": "Couldn't schedule the script. {error}",
            },
            "list_scripts": {
                "success": "I found {count} scripts: {names}.",
                "empty": "There are no scripts available.",
            },
            "delete_script": {
                "success": "Deleted script {name}.",
                "error": "Couldn't delete {name}. {error}",
            },
            "validate_script": {
                "success": "Script {name} passed all checks. {details}",
                "error": "Script {name} has issues: {issues}",
            },
            "deploy": {
                "success": "Deployment to {environment} started. {details}",
                "error": "Deployment failed. {error}",
            },
            "rollback": {
                "success": "Rolled back {service} to previous version.",
                "error": "Rollback failed. {error}",
            },
            "deployment_status": {
                "success": "Current deployment: {status}. {details}",
            },
            "system_status": {
                "success": "System is {status}. CPU: {cpu}%, Memory: {memory}%, Disk: {disk}%. {alerts}",
            },
            "get_metrics": {
                "success": "Metrics for {name}: {metrics}",
                "error": "Couldn't get metrics. {error}",
            },
            "check_alerts": {
                "success": "You have {count} active alerts. {details}",
                "no_alerts": "No active alerts. All systems are operational.",
            },
            "read_logs": {
                "success": "Recent logs: {logs}",
            },
            "stop_listening": {
                "success": "Standing by. Say the wake word to activate me again.",
            },
            "help": {
                "success": "I can help you with scripts, deployments, monitoring, and system management. Try saying things like 'create a script', 'deploy to staging', or 'what's the system status'.",
            },
            "unknown": {
                "error": "I didn't understand that. Try asking for help.",
            },
            "cancelled": {
                "success": "Okay, cancelled.",
            },
        }
    
    def build(self, intent: Intent, result: 'ActionResult') -> str:
        """
        Build a natural response.
        
        Args:
            intent: The parsed intent
            result: The action result
            
        Returns:
            Natural language response
        """
        if result.cancelled:
            return self._format_response("cancelled", "success", {})
        
        intent_templates = self.templates.get(intent.name, self.templates["unknown"])
        
        if result.success:
            template_key = "success"
            if intent.name == "check_alerts" and result.data.get("count", 0) == 0:
                template_key = "no_alerts"
            elif intent.name == "list_scripts" and result.data.get("count", 0) == 0:
                template_key = "empty"
        else:
            template_key = "error"
        
        template = intent_templates.get(template_key, intent_templates.get("success", "Done."))
        
        return self._format_response(intent.name, template_key, result.data)
    
    def _format_response(self, intent_name: str, template_key: str, data: dict) -> str:
        """Format a response template with data."""
        templates = self.templates.get(intent_name, {})
        template = templates.get(template_key, "Done.")
        
        try:
            # Fill in template placeholders
            return template.format(**data)
        except KeyError as e:
            # Missing data, return template with available data
            logger.warning(f"Missing data for template: {e}")
            try:
                # Try with defaults for missing keys
                import string
                formatter = string.Formatter()
                field_names = [field_name for _, field_name, _, _ in formatter.parse(template) if field_name]
                
                filled_data = {}
                for field in field_names:
                    filled_data[field] = data.get(field, f"<{field}>")
                
                return template.format(**filled_data)
            except:
                return template
    
    def build_error_response(self, error_message: str) -> str:
        """
        Build an error response.
        
        Args:
            error_message: Error description
            
        Returns:
            Natural error response
        """
        return f"I encountered an error: {error_message}"
    
    def build_confirmation_prompt(self, intent: Intent) -> str:
        """
        Build a confirmation prompt.
        
        Args:
            intent: Intent to confirm
            
        Returns:
            Confirmation question
        """
        return f"You want me to {intent.description}. Is that correct? Say yes or no."
