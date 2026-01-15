"""
AI Script Generator using Local LLM via Ollama
Generate shell scripts from natural language descriptions
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
import httpx

logger = logging.getLogger(__name__)


@dataclass
class GeneratedScript:
    """Represents a generated script."""
    name: str
    content: str
    language: str
    description: str


class AIScriptGenerator:
    """Generate scripts using local LLM via Ollama."""
    
    def __init__(self, model: str = "codellama", ollama_url: str = "http://localhost:11434"):
        """
        Initialize AI Script Generator.
        
        Args:
            model: Ollama model name (codellama, llama2, mistral, etc.)
            ollama_url: URL of the Ollama API server
        """
        self.model = model
        self.ollama_url = ollama_url.rstrip('/')
        self.client = httpx.Client(timeout=60.0)
        
    def _call_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Call Ollama API to generate text.
        
        Args:
            prompt: The prompt to send to the model
            system_prompt: Optional system prompt for context
            
        Returns:
            Generated text response
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False
                }
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("message", {}).get("content", "")
            
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            raise
    
    def generate(
        self,
        description: str,
        language: str = "bash",
        include_comments: bool = True,
        include_error_handling: bool = True
    ) -> GeneratedScript:
        """
        Generate a script or template from natural language description.
        
        Args:
            description: Natural language description of what the script or template should do
            language: Target language (bash, python, powershell, arm, json)
            include_comments: Whether to include explanatory comments
            include_error_handling: Whether to include error handling
        
        Returns:
            GeneratedScript object with the generated script or template
        """
        if language.lower() in ["arm", "json", "arm-template", "azure-arm"]:
            system_prompt = (
                "You are an expert in Azure ARM templates. Generate a valid Azure Resource Manager (ARM) template in JSON format. "
                "Output only the ARM template JSON code, no explanations. Follow best practices for Azure deployments."
            )
            prompt = f"""Generate an Azure ARM template in JSON that does the following:

{description}

Requirements:
- Use valid ARM schema and structure
- Follow Azure best practices
- Output only the ARM template JSON code, no explanations."""
            ext_language = "json"
        else:
            system_prompt = f"You are an expert script developer. Generate clean, production-ready {language} scripts. Follow best practices and include proper error handling. Output only the script code without explanations."
            prompt = f"""Generate a {language} script that does the following:

{description}

Requirements:
- Include comments: {include_comments}
- Include error handling: {include_error_handling}
- Follow best practices for {language}
- Make it production-ready
- Include shebang line for shell scripts

Output only the script code, no explanations."""
            ext_language = language
        try:
            script_content = self._call_ollama(prompt, system_prompt)
            # Clean up the response - remove markdown code blocks if present
            script_content = script_content.strip()
            if script_content.startswith("```"):
                lines = script_content.split("\n")
                # Remove first and last lines if they're markdown code fences
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                script_content = "\n".join(lines)
            # Generate a filename
            script_name = self._generate_filename(description, ext_language)
            return GeneratedScript(
                name=script_name,
                content=script_content,
                language=language,
                description=description
            )
        except Exception as e:
            logger.error(f"Failed to generate script: {e}")
            raise
    
    def explain(self, script: str) -> str:
        """
        Explain what a script does.
        
        Args:
            script: The script content to explain
            
        Returns:
            Plain text explanation of the script
        """
        system_prompt = "You are an expert at analyzing and explaining code. Provide clear, concise explanations."
        
        prompt = f"""Analyze this script and explain what it does in plain language:

```
{script}
```

Provide:
1. A one-line summary
2. What the script does step by step
3. Any potential issues or concerns
4. Requirements or dependencies"""

        try:
            explanation = self._call_ollama(prompt, system_prompt)
            return explanation
        except Exception as e:
            logger.error(f"Failed to explain script: {e}")
            raise
    
    def improve(self, script: str) -> str:
        """
        Suggest improvements for a script.
        
        Args:
            script: The script content to improve
            
        Returns:
            Suggestions for improving the script
        """
        system_prompt = "You are an expert code reviewer. Provide actionable improvement suggestions."
        
        prompt = f"""Review this script and suggest improvements:

```
{script}
```

Focus on:
1. Error handling
2. Security concerns
3. Best practices
4. Performance optimizations
5. Code clarity

Provide specific, actionable suggestions."""

        try:
            suggestions = self._call_ollama(prompt, system_prompt)
            return suggestions
        except Exception as e:
            logger.error(f"Failed to improve script: {e}")
            raise
    
    def convert(self, script: str, from_lang: str, to_lang: str) -> str:
        """
        Convert script from one language to another.
        
        Args:
            script: The script content to convert
            from_lang: Source language
            to_lang: Target language
            
        Returns:
            Converted script in target language
        """
        system_prompt = f"You are an expert at converting scripts between languages. Convert code accurately while maintaining functionality."
        
        prompt = f"""Convert this {from_lang} script to {to_lang}:

```{from_lang}
{script}
```

Requirements:
- Maintain all functionality
- Follow {to_lang} best practices
- Include appropriate error handling
- Add comments where helpful

Output only the converted {to_lang} code."""

        try:
            converted = self._call_ollama(prompt, system_prompt)
            
            # Clean up markdown code blocks
            converted = converted.strip()
            if converted.startswith("```"):
                lines = converted.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                converted = "\n".join(lines)
            
            return converted
        except Exception as e:
            logger.error(f"Failed to convert script: {e}")
            raise
    
    def _generate_filename(self, description: str, language: str) -> str:
        """
        Generate a filename from description and language.
        
        Args:
            description: Script description
            language: Script language
            
        Returns:
            Generated filename
        """
        # Take first few words of description
        words = description.lower().split()[:3]
        name = "_".join(words)
        
        # Remove special characters
        name = "".join(c if c.isalnum() or c == "_" else "_" for c in name)
        
        # Add appropriate extension
        extensions = {
            "bash": ".sh",
            "python": ".py",
            "powershell": ".ps1",
            "shell": ".sh",
            "sh": ".sh",
            "py": ".py",
            "json": ".json",
            "arm": ".json",
            "arm-template": ".json",
            "azure-arm": ".json"
        }
        ext = extensions.get(language.lower(), ".sh")
        return f"{name}{ext}"
    
    def check_availability(self) -> bool:
        """
        Check if Ollama is available and model is loaded.
        
        Returns:
            True if Ollama is available, False otherwise
        """
        try:
            response = self.client.get(f"{self.ollama_url}/api/tags")
            response.raise_for_status()
            
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            
            # Check if our model is available
            return any(self.model in name for name in model_names)
            
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False
