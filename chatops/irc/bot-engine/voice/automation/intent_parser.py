"""Intent parser for voice commands."""

import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class Intent:
    """Parsed intent from voice command."""
    
    name: str
    entities: Dict[str, Any]
    confidence: float
    original_text: str
    requires_confirmation: bool = False
    
    @property
    def description(self) -> str:
        """Get human-readable description of intent."""
        descriptions = {
            "create_script": f"create a script: {self.entities.get('description', 'unknown')}",
            "run_script": f"run script {self.entities.get('name', 'unknown')}",
            "schedule_script": f"schedule script {self.entities.get('name', 'unknown')}",
            "delete_script": f"delete script {self.entities.get('name', 'unknown')}",
            "list_scripts": "list all scripts",
            "validate_script": f"validate script {self.entities.get('name', 'unknown')}",
            "deploy": f"deploy to {self.entities.get('environment', 'unknown')}",
            "rollback": f"rollback {self.entities.get('service', 'unknown')}",
            "deployment_status": "check deployment status",
            "system_status": "check system status",
            "get_metrics": f"get metrics for {self.entities.get('name', 'unknown')}",
            "check_alerts": "check for alerts",
            "read_logs": "read recent logs",
            "query_database": f"query {self.entities.get('database', 'unknown')}",
            "check_webhooks": "check for new webhooks",
            "stop_listening": "stop listening",
            "help": "show help",
        }
        return descriptions.get(self.name, f"execute {self.name}")


class IntentParser:
    """Parse intents from transcribed speech."""
    
    def __init__(self):
        """Initialize intent parser."""
        self.patterns = self._build_patterns()
        logger.info("IntentParser initialized")
    
    def _build_patterns(self) -> Dict[str, list]:
        """Build pattern matching rules for intents."""
        return {
            "create_script": [
                (r"create.*script.*to\s+(.*)", "description"),
                (r"make.*script.*to\s+(.*)", "description"),
                (r"generate.*script.*for\s+(.*)", "description"),
            ],
            "run_script": [
                (r"run\s+(?:script\s+)?(\w+)", "name"),
                (r"execute\s+(?:script\s+)?(\w+)", "name"),
            ],
            "schedule_script": [
                (r"schedule\s+(\w+).*at\s+(.*)", ["name", "time"]),
                (r"run\s+(\w+).*every\s+(.*)", ["name", "frequency"]),
            ],
            "list_scripts": [
                (r"list.*scripts?", None),
                (r"show.*scripts?", None),
                (r"what scripts", None),
            ],
            "delete_script": [
                (r"delete.*script\s+(\w+)", "name"),
                (r"remove.*script\s+(\w+)", "name"),
            ],
            "validate_script": [
                (r"validate.*script\s+(\w+)", "name"),
                (r"check.*script\s+(\w+)", "name"),
            ],
            "deploy": [
                (r"deploy.*to\s+(\w+)", "environment"),
                (r"push.*to\s+(\w+)", "environment"),
            ],
            "rollback": [
                (r"rollback\s+(\w+)", "service"),
                (r"undo.*deployment.*(\w+)", "service"),
            ],
            "deployment_status": [
                (r"deployment.*status", None),
                (r"what.*deployment", None),
            ],
            "system_status": [
                (r"system.*status", None),
                (r"how.*system", None),
                (r"server.*status", None),
            ],
            "get_metrics": [
                (r"(?:show|get).*metrics?.*for\s+(\w+)", "name"),
                (r"what.*(?:cpu|memory|disk)", "name"),
            ],
            "check_alerts": [
                (r"(?:any|check).*alerts?", None),
                (r"show.*alerts?", None),
            ],
            "read_logs": [
                (r"read.*logs?", None),
                (r"show.*logs?", None),
                (r"recent.*logs?", None),
            ],
            "stop_listening": [
                (r"stop.*listening", None),
                (r"go.*to.*sleep", None),
                (r"that'?s?\s*all", None),
            ],
            "help": [
                (r"what.*can.*you.*do", None),
                (r"help", None),
                (r"commands?", None),
            ],
        }
    
    def parse(self, text: str) -> Intent:
        """
        Parse text into an intent.
        
        Args:
            text: Transcribed text
            
        Returns:
            Parsed Intent object
        """
        import re
        
        text = text.lower().strip()
        
        # Try to match patterns
        for intent_name, patterns in self.patterns.items():
            for pattern_info in patterns:
                if isinstance(pattern_info, tuple):
                    pattern, entity_names = pattern_info if len(pattern_info) == 2 else (pattern_info[0], None)
                else:
                    pattern = pattern_info
                    entity_names = None
                
                match = re.search(pattern, text)
                if match:
                    entities = {}
                    
                    if entity_names:
                        if isinstance(entity_names, str):
                            entities[entity_names] = match.group(1).strip()
                        elif isinstance(entity_names, list):
                            for i, name in enumerate(entity_names, start=1):
                                if i <= len(match.groups()):
                                    entities[name] = match.group(i).strip()
                    
                    # Determine if confirmation is needed
                    requires_confirmation = intent_name in [
                        "delete_script", "deploy", "rollback"
                    ]
                    
                    return Intent(
                        name=intent_name,
                        entities=entities,
                        confidence=0.9,
                        original_text=text,
                        requires_confirmation=requires_confirmation
                    )
        
        # No match found
        return Intent(
            name="unknown",
            entities={},
            confidence=0.0,
            original_text=text,
            requires_confirmation=False
        )
