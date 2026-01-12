"""Natural language command processor using local LLM."""

import logging
import json
from typing import Optional
from .intent_parser import Intent, IntentParser

logger = logging.getLogger(__name__)


class CommandProcessor:
    """Process natural language commands using local LLM."""
    
    INTENTS = [
        "create_script", "run_script", "schedule_script", "list_scripts",
        "validate_script", "delete_script",
        "deploy", "rollback", "deployment_status",
        "system_status", "get_metrics", "check_alerts", "read_logs",
        "query_database", "check_webhooks",
        "stop_listening", "wake_up", "help", "unknown"
    ]
    
    def __init__(self, model: str = "mistral", ollama_url: str = "http://localhost:11434"):
        """
        Initialize command processor.
        
        Args:
            model: LLM model name (e.g., mistral, llama2)
            ollama_url: Ollama API URL
        """
        self.model = model
        self.ollama_url = ollama_url
        self.use_llm = False  # Will be set if Ollama is available
        self.intent_parser = IntentParser()
        
        self._check_ollama()
        logger.info(f"CommandProcessor initialized (LLM: {self.use_llm})")
    
    def _check_ollama(self):
        """Check if Ollama is available."""
        try:
            import httpx
            response = httpx.get(f"{self.ollama_url}/api/tags", timeout=2.0)
            if response.status_code == 200:
                self.use_llm = True
                logger.info("Ollama LLM available")
        except Exception as e:
            logger.info(f"Ollama not available, using pattern matching: {e}")
    
    def parse(self, text: str, context: Optional['ConversationContext'] = None) -> Intent:
        """
        Parse natural language into structured intent.
        
        Args:
            text: Command text
            context: Conversation context
            
        Returns:
            Parsed Intent
        """
        if self.use_llm:
            return self._parse_with_llm(text, context)
        else:
            return self._parse_with_patterns(text)
    
    def _parse_with_patterns(self, text: str) -> Intent:
        """Parse using pattern matching (fallback)."""
        return self.intent_parser.parse(text)
    
    def _parse_with_llm(self, text: str, context: Optional['ConversationContext']) -> Intent:
        """Parse using local LLM."""
        try:
            prompt = self._build_prompt(text, context)
            response = self._query_llm(prompt)
            return self._parse_llm_response(response, text)
        except Exception as e:
            logger.error(f"LLM parsing failed, falling back to patterns: {e}")
            return self._parse_with_patterns(text)
    
    def _build_prompt(self, text: str, context: Optional['ConversationContext']) -> str:
        """Build prompt for intent parsing."""
        context_summary = ""
        if context and context.turns:
            recent = context.turns[-3:]
            context_summary = "\n".join([
                f"User: {turn.user}\nBot: {turn.bot}"
                for turn in recent
            ])
        
        return f"""You are a command parser for a DevOps automation bot.
Parse the following voice command into a structured intent.

Available intents: {', '.join(self.INTENTS)}

Previous context:
{context_summary if context_summary else "None"}

Current command: "{text}"

Return ONLY valid JSON with this exact structure:
{{
  "intent": "<one of the available intents>",
  "entities": {{"key": "value"}},
  "confidence": 0.0
}}

Response:"""
    
    def _query_llm(self, prompt: str) -> str:
        """Query Ollama LLM."""
        try:
            import httpx
            
            response = httpx.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                    }
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"LLM query failed: {response.status_code}")
                return ""
        except Exception as e:
            logger.error(f"LLM query error: {e}")
            return ""
    
    def _parse_llm_response(self, response: str, original_text: str) -> Intent:
        """Parse LLM JSON response into Intent."""
        try:
            # Extract JSON from response (sometimes LLM adds extra text)
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                intent_name = data.get("intent", "unknown")
                entities = data.get("entities", {})
                confidence = float(data.get("confidence", 0.5))
                
                # Determine if confirmation is needed
                requires_confirmation = intent_name in [
                    "delete_script", "deploy", "rollback"
                ]
                
                return Intent(
                    name=intent_name,
                    entities=entities,
                    confidence=confidence,
                    original_text=original_text,
                    requires_confirmation=requires_confirmation
                )
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
        
        # Fallback to pattern matching
        return self._parse_with_patterns(original_text)
