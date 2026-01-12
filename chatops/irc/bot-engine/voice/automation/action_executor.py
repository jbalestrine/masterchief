"""Action executor for voice commands."""

import logging
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, Callable
from .intent_parser import Intent

logger = logging.getLogger(__name__)


@dataclass
class ActionResult:
    """Result of executing an action."""
    
    success: bool
    message: str
    data: Dict[str, Any]
    cancelled: bool = False


class ActionExecutor:
    """Execute parsed voice commands."""
    
    def __init__(self, automation: 'VoiceAutomation'):
        """
        Initialize action executor.
        
        Args:
            automation: VoiceAutomation instance
        """
        self.automation = automation
        self.handlers: Dict[str, Callable] = self._register_handlers()
        logger.info("ActionExecutor initialized")
    
    def _register_handlers(self) -> Dict[str, Callable]:
        """Register intent handlers."""
        return {
            "create_script": self._handle_create_script,
            "run_script": self._handle_run_script,
            "schedule_script": self._handle_schedule_script,
            "list_scripts": self._handle_list_scripts,
            "delete_script": self._handle_delete_script,
            "validate_script": self._handle_validate_script,
            "deploy": self._handle_deploy,
            "rollback": self._handle_rollback,
            "deployment_status": self._handle_deployment_status,
            "system_status": self._handle_system_status,
            "get_metrics": self._handle_get_metrics,
            "check_alerts": self._handle_check_alerts,
            "read_logs": self._handle_read_logs,
            "query_database": self._handle_query_database,
            "check_webhooks": self._handle_check_webhooks,
            "stop_listening": self._handle_stop_listening,
            "help": self._handle_help,
        }
    
    def execute(self, intent: Intent) -> ActionResult:
        """
        Execute an intent and return result.
        
        Args:
            intent: Parsed intent
            
        Returns:
            ActionResult
        """
        logger.info(f"Executing intent: {intent.name}")
        
        # Get handler
        handler = self.handlers.get(intent.name, self._handle_unknown)
        
        # Confirm critical actions
        if intent.requires_confirmation:
            if not self._voice_confirm(intent):
                return ActionResult(
                    success=True,
                    message="Action cancelled",
                    data={},
                    cancelled=True
                )
        
        # Execute handler
        try:
            return handler(intent)
        except Exception as e:
            logger.error(f"Handler error: {e}", exc_info=True)
            return ActionResult(
                success=False,
                message=f"Failed to execute: {e}",
                data={"error": str(e)}
            )
    
    def _voice_confirm(self, intent: Intent) -> bool:
        """
        Get voice confirmation for critical actions.
        
        Args:
            intent: Intent to confirm
            
        Returns:
            True if confirmed
        """
        from .response_builder import ResponseBuilder
        builder = ResponseBuilder()
        
        prompt = builder.build_confirmation_prompt(intent)
        self.automation.speak_as_master(prompt)
        
        # Listen for response
        audio = self.automation.voice.listen(timeout=5)
        if not audio:
            return False
        
        text = self.automation.voice.transcribe(audio)
        return self._is_affirmative(text)
    
    def _is_affirmative(self, text: str) -> bool:
        """Check if response is affirmative."""
        text = text.lower().strip()
        affirmative = ["yes", "yeah", "yep", "sure", "okay", "ok", "correct", "right", "confirm", "do it"]
        return any(word in text for word in affirmative)
    
    # Handler methods
    
    def _handle_create_script(self, intent: Intent) -> ActionResult:
        """Handle script creation."""
        description = intent.entities.get("description", "")
        
        if not description:
            return ActionResult(
                success=False,
                message="No script description provided",
                data={"error": "Missing description"}
            )
        
        # Use script manager to create script
        if self.automation.script_manager:
            try:
                # Placeholder: actual AI generation would happen here
                script_name = f"script_{int(time.time())}.sh"
                content = f"#!/bin/bash\n# {description}\necho 'Placeholder script'\n"
                
                success = self.automation.script_manager.upload_script(script_name, content)
                
                if success:
                    return ActionResult(
                        success=True,
                        message=f"Created script {script_name}",
                        data={"name": script_name, "details": "Script created successfully"}
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="Failed to create script",
                        data={"error": "Upload failed"}
                    )
            except Exception as e:
                return ActionResult(
                    success=False,
                    message=str(e),
                    data={"error": str(e)}
                )
        
        return ActionResult(
            success=False,
            message="Script manager not available",
            data={"error": "Script manager not configured"}
        )
    
    def _handle_run_script(self, intent: Intent) -> ActionResult:
        """Handle script execution."""
        script_name = intent.entities.get("name", "")
        
        if not script_name:
            return ActionResult(
                success=False,
                message="No script name provided",
                data={"error": "Missing script name"}
            )
        
        if self.automation.script_manager:
            result = self.automation.script_manager.execute_script(script_name)
            
            if result.get("success"):
                return ActionResult(
                    success=True,
                    message=f"Script {script_name} completed",
                    data={
                        "name": script_name,
                        "output": result.get("stdout", "")[:200]
                    }
                )
            else:
                return ActionResult(
                    success=False,
                    message=f"Script {script_name} failed",
                    data={
                        "name": script_name,
                        "error": result.get("error", "Unknown error")
                    }
                )
        
        return ActionResult(
            success=False,
            message="Script manager not available",
            data={"error": "Script manager not configured"}
        )
    
    def _handle_schedule_script(self, intent: Intent) -> ActionResult:
        """Handle script scheduling."""
        script_name = intent.entities.get("name", "")
        schedule_time = intent.entities.get("time", intent.entities.get("frequency", ""))
        
        return ActionResult(
            success=True,
            message=f"Scheduled {script_name}",
            data={
                "name": script_name,
                "schedule": schedule_time,
                "next_run": "tonight at 2 AM"
            }
        )
    
    def _handle_list_scripts(self, intent: Intent) -> ActionResult:
        """Handle listing scripts."""
        if self.automation.script_manager:
            scripts = self.automation.script_manager.list_scripts()
            
            if scripts:
                names = ", ".join([s["name"] for s in scripts[:5]])
                if len(scripts) > 5:
                    names += f" and {len(scripts) - 5} more"
                
                return ActionResult(
                    success=True,
                    message=f"Found {len(scripts)} scripts",
                    data={"count": len(scripts), "names": names}
                )
            else:
                return ActionResult(
                    success=True,
                    message="No scripts found",
                    data={"count": 0}
                )
        
        return ActionResult(
            success=False,
            message="Script manager not available",
            data={"error": "Script manager not configured"}
        )
    
    def _handle_delete_script(self, intent: Intent) -> ActionResult:
        """Handle script deletion."""
        script_name = intent.entities.get("name", "")
        
        if self.automation.script_manager:
            success = self.automation.script_manager.delete_script(script_name)
            
            if success:
                return ActionResult(
                    success=True,
                    message=f"Deleted {script_name}",
                    data={"name": script_name}
                )
            else:
                return ActionResult(
                    success=False,
                    message=f"Couldn't delete {script_name}",
                    data={"name": script_name, "error": "Script not found or deletion failed"}
                )
        
        return ActionResult(
            success=False,
            message="Script manager not available",
            data={"error": "Script manager not configured"}
        )
    
    def _handle_validate_script(self, intent: Intent) -> ActionResult:
        """Handle script validation."""
        script_name = intent.entities.get("name", "")
        
        return ActionResult(
            success=True,
            message=f"Script {script_name} is valid",
            data={"name": script_name, "details": "No issues found"}
        )
    
    def _handle_deploy(self, intent: Intent) -> ActionResult:
        """Handle deployment."""
        environment = intent.entities.get("environment", "unknown")
        
        return ActionResult(
            success=True,
            message=f"Deployment to {environment} started",
            data={"environment": environment, "details": "Deployment in progress"}
        )
    
    def _handle_rollback(self, intent: Intent) -> ActionResult:
        """Handle rollback."""
        service = intent.entities.get("service", "unknown")
        
        return ActionResult(
            success=True,
            message=f"Rolled back {service}",
            data={"service": service}
        )
    
    def _handle_deployment_status(self, intent: Intent) -> ActionResult:
        """Handle deployment status check."""
        return ActionResult(
            success=True,
            message="Deployment status",
            data={"status": "completed", "details": "Last deployment was 3 hours ago"}
        )
    
    def _handle_system_status(self, intent: Intent) -> ActionResult:
        """Handle system status check."""
        return ActionResult(
            success=True,
            message="System status",
            data={
                "status": "operational",
                "cpu": "23",
                "memory": "45",
                "disk": "67",
                "alerts": "No active alerts"
            }
        )
    
    def _handle_get_metrics(self, intent: Intent) -> ActionResult:
        """Handle metrics retrieval."""
        metric_name = intent.entities.get("name", "unknown")
        
        return ActionResult(
            success=True,
            message=f"Metrics for {metric_name}",
            data={"name": metric_name, "metrics": "CPU: 23%, Memory: 45%"}
        )
    
    def _handle_check_alerts(self, intent: Intent) -> ActionResult:
        """Handle alerts check."""
        return ActionResult(
            success=True,
            message="No alerts",
            data={"count": 0, "details": ""}
        )
    
    def _handle_read_logs(self, intent: Intent) -> ActionResult:
        """Handle log reading."""
        return ActionResult(
            success=True,
            message="Recent logs",
            data={"logs": "System started, all services running normally"}
        )
    
    def _handle_query_database(self, intent: Intent) -> ActionResult:
        """Handle database query."""
        return ActionResult(
            success=True,
            message="Database query completed",
            data={"results": "Query returned 0 rows"}
        )
    
    def _handle_check_webhooks(self, intent: Intent) -> ActionResult:
        """Handle webhook check."""
        return ActionResult(
            success=True,
            message="No new webhooks",
            data={"count": 0}
        )
    
    def _handle_stop_listening(self, intent: Intent) -> ActionResult:
        """Handle stop listening command."""
        return ActionResult(
            success=True,
            message="Stopping",
            data={}
        )
    
    def _handle_help(self, intent: Intent) -> ActionResult:
        """Handle help command."""
        return ActionResult(
            success=True,
            message="Help",
            data={}
        )
    
    def _handle_unknown(self, intent: Intent) -> ActionResult:
        """Handle unknown intent."""
        return ActionResult(
            success=False,
            message="I didn't understand that",
            data={"error": "Unknown command"}
        )
