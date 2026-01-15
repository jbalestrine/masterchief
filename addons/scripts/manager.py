"""
Custom Script Manager
Upload, manage, and execute custom scripts with AI generation, templates, validation, and scheduling
"""

import os
import subprocess
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import hashlib
import time

logger = logging.getLogger(__name__)

# Import new automation features
try:
    from .ai_generator import AIScriptGenerator, GeneratedScript
except ImportError:
    AIScriptGenerator = None
    GeneratedScript = None

try:
    from .voice_scripter import VoiceToScript, MockVoiceEngine
except ImportError:
    VoiceToScript = None
    MockVoiceEngine = None

try:
    from .templates import ScriptTemplates
except ImportError:
    ScriptTemplates = None

try:
    from .validator import ScriptValidator, ValidationResult
except ImportError:
    ScriptValidator = None
    ValidationResult = None

try:
    from .scheduler import ScriptScheduler, ScheduledJob, ExecutionRecord
except ImportError:
    ScriptScheduler = None
    ScheduledJob = None
    ExecutionRecord = None

class ScriptManager:
        def generate_arm_template(self, description: str, save: bool = True) -> Optional[GeneratedScript]:
            """
            Generate an ARM template using AI from a natural language description.
            Args:
                description: Natural language description of the ARM template
                save: Whether to save the generated template
            Returns:
                GeneratedScript object or None if failed
            """
            if not self.ai_generator:
                logger.error("AI generator not initialized")
                return None
            try:
                # Use 'json' as the language for ARM templates
                script = self.ai_generator.generate(description, language="json")
                # Ensure .json extension for ARM templates
                if not script.name.endswith(".json"):
                    script.name = script.name.rsplit('.', 1)[0] + ".json"
                if save:
                    self.upload_script(script.name, script.content)
                return script
            except Exception as e:
                logger.error(f"Failed to generate ARM template: {e}")
                return None
    """Manage custom scripts with AI generation, templates, validation, and scheduling"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize ScriptManager with automation features.
        
        Args:
            config: Optional configuration dictionary
        """
        self.scripts_dir = Path("/var/lib/masterchief/scripts")
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
        self.config = config or {}
        
        # Initialize AI generator if enabled
        self.ai_generator = None
        if AIScriptGenerator and self.config.get('ai_generation', {}).get('enabled', False):
            try:
                self.ai_generator = AIScriptGenerator(
                    model=self.config.get('ai_generation', {}).get('model', 'codellama'),
                    ollama_url=self.config.get('ai_generation', {}).get('ollama_url', 'http://localhost:11434')
                )
                logger.info("AI script generator initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize AI generator: {e}")
        
        # Initialize voice-to-script if enabled
        self.voice_scripter = None
        if VoiceToScript and self.config.get('voice', {}).get('enabled', False):
            # Will be initialized when voice engine is available
            logger.info("Voice-to-script support available")
        
        # Initialize templates
        self.templates = None
        if ScriptTemplates:
            try:
                templates_dir = self.config.get('templates', {}).get('directory')
                custom_dir = self.config.get('templates', {}).get('custom_directory')
                self.templates = ScriptTemplates(
                    templates_dir=Path(templates_dir) if templates_dir else None,
                    custom_dir=Path(custom_dir) if custom_dir else None
                )
                logger.info("Script templates initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize templates: {e}")
        
        # Initialize validator
        self.validator = None
        if ScriptValidator and self.config.get('validation', {}).get('enabled', True):
            try:
                self.validator = ScriptValidator(
                    block_dangerous=self.config.get('validation', {}).get('block_dangerous', True),
                    require_validation=self.config.get('validation', {}).get('require_validation', False)
                )
                logger.info("Script validator initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize validator: {e}")
        
        # Initialize scheduler
        self.scheduler = None
        if ScriptScheduler and self.config.get('scheduling', {}).get('enabled', False):
            try:
                db_path = Path(self.config.get('scheduling', {}).get('database', '/var/lib/masterchief/schedules.db'))
                db_path.parent.mkdir(parents=True, exist_ok=True)
                self.scheduler = ScriptScheduler(
                    scripts_dir=self.scripts_dir,
                    db_path=db_path
                )
                logger.info("Script scheduler initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize scheduler: {e}")
    
    def list_scripts(self) -> List[Dict[str, Any]]:
        """List all uploaded scripts"""
        scripts = []
        for script_file in self.scripts_dir.glob("*.sh"):
            scripts.append({
                'name': script_file.name,
                'path': str(script_file),
                'size': script_file.stat().st_size,
                'modified': script_file.stat().st_mtime,
                'executable': os.access(script_file, os.X_OK)
            })
        return scripts
    
    def upload_script(self, name: str, content: str) -> bool:
        """Upload a new script"""
        try:
            script_path = self.scripts_dir / name
            with open(script_path, 'w') as f:
                f.write(content)
            
            # Make executable
            os.chmod(script_path, 0o755)
            
            logger.info(f"Script uploaded: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload script {name}: {e}")
            return False
    
    def execute_script(self, name: str, args: List[str] = None) -> Dict[str, Any]:
        """Execute a script"""
        try:
            script_path = self.scripts_dir / name
            if not script_path.exists():
                return {
                    'success': False,
                    'error': 'Script not found'
                }
            
            cmd = [str(script_path)]
            if args:
                cmd.extend(args)
            
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            execution_time = time.time() - start_time
            
            return {
                'success': result.returncode == 0,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'execution_time': execution_time
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Script execution timed out'
            }
        except Exception as e:
            logger.error(f"Failed to execute script {name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_script(self, name: str) -> bool:
        """Delete a script"""
        try:
            script_path = self.scripts_dir / name
            if script_path.exists():
                script_path.unlink()
                logger.info(f"Script deleted: {name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete script {name}: {e}")
            return False
    
    def get_script_content(self, name: str) -> Optional[str]:
        """Get script content"""
        try:
            script_path = self.scripts_dir / name
            if script_path.exists():
                with open(script_path, 'r') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Failed to read script {name}: {e}")
        return None
    
    # AI Generation Methods
    
    def generate_script(
        self,
        description: str,
        language: str = "bash",
        save: bool = True
    ) -> Optional[GeneratedScript]:
        """
        Generate a script using AI from natural language description.
        
        Args:
            description: Natural language description
            language: Target language (bash, python, powershell)
            save: Whether to save the generated script
            
        Returns:
            GeneratedScript object or None if failed
        """
        if not self.ai_generator:
            logger.error("AI generator not initialized")
            return None
        
        try:
            script = self.ai_generator.generate(description, language=language)
            
            if save:
                self.upload_script(script.name, script.content)
            
            return script
        except Exception as e:
            logger.error(f"Failed to generate script: {e}")
            return None
    
    def explain_script(self, name: str) -> Optional[str]:
        """
        Get AI explanation of what a script does.
        
        Args:
            name: Script name
            
        Returns:
            Explanation text or None if failed
        """
        if not self.ai_generator:
            logger.error("AI generator not initialized")
            return None
        
        content = self.get_script_content(name)
        if not content:
            return None
        
        try:
            return self.ai_generator.explain(content)
        except Exception as e:
            logger.error(f"Failed to explain script: {e}")
            return None
    
    def improve_script(self, name: str) -> Optional[str]:
        """
        Get AI suggestions to improve a script.
        
        Args:
            name: Script name
            
        Returns:
            Improvement suggestions or None if failed
        """
        if not self.ai_generator:
            logger.error("AI generator not initialized")
            return None
        
        content = self.get_script_content(name)
        if not content:
            return None
        
        try:
            return self.ai_generator.improve(content)
        except Exception as e:
            logger.error(f"Failed to improve script: {e}")
            return None
    
    # Template Methods
    
    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, str]]:
        """
        List available script templates.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of template info dictionaries
        """
        if not self.templates:
            return []
        
        return self.templates.list_templates(category)
    
    def get_template(self, template_path: str, variables: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Get a template with variable substitution.
        
        Args:
            template_path: Path to template (e.g., "backup/postgres")
            variables: Variables to substitute
            
        Returns:
            Rendered template content or None if failed
        """
        if not self.templates:
            logger.error("Templates not initialized")
            return None
        
        try:
            return self.templates.get(template_path, variables)
        except Exception as e:
            logger.error(f"Failed to get template: {e}")
            return None
    
    def create_from_template(
        self,
        template_path: str,
        script_name: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create a script from a template.
        
        Args:
            template_path: Path to template
            script_name: Name for the new script
            variables: Variables to substitute
            
        Returns:
            True if created successfully
        """
        content = self.get_template(template_path, variables)
        if not content:
            return False
        
        return self.upload_script(script_name, content)
    
    # Validation Methods
    
    def validate_script(self, name: str) -> Optional[ValidationResult]:
        """
        Validate a script for safety and correctness.
        
        Args:
            name: Script name
            
        Returns:
            ValidationResult or None if failed
        """
        if not self.validator:
            logger.warning("Validator not initialized, skipping validation")
            return None
        
        script_path = self.scripts_dir / name
        if not script_path.exists():
            logger.error(f"Script not found: {name}")
            return None
        
        try:
            return self.validator.validate(str(script_path))
        except Exception as e:
            logger.error(f"Failed to validate script: {e}")
            return None
    
    def dry_run_script(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Perform a dry run of a script (syntax check without execution).
        
        Args:
            name: Script name
            
        Returns:
            Dry run results or None if failed
        """
        if not self.validator:
            logger.warning("Validator not initialized")
            return None
        
        script_path = self.scripts_dir / name
        if not script_path.exists():
            logger.error(f"Script not found: {name}")
            return None
        
        try:
            return self.validator.dry_run(str(script_path))
        except Exception as e:
            logger.error(f"Failed to dry run script: {e}")
            return None
    
    # Scheduling Methods
    
    def schedule_script(
        self,
        script_name: str,
        cron: str,
        args: List[str] = None,
        notify: bool = False
    ) -> Optional[ScheduledJob]:
        """
        Schedule a script for recurring execution.
        
        Args:
            script_name: Name of script to schedule
            cron: Cron expression
            args: Optional command line arguments
            notify: Whether to send notifications
            
        Returns:
            ScheduledJob or None if failed
        """
        if not self.scheduler:
            logger.error("Scheduler not initialized")
            return None
        
        try:
            return self.scheduler.add(script_name, cron, args, notify)
        except Exception as e:
            logger.error(f"Failed to schedule script: {e}")
            return None
    
    def unschedule_script(self, script_name: str) -> bool:
        """
        Remove a scheduled script.
        
        Args:
            script_name: Name of script to unschedule
            
        Returns:
            True if successful
        """
        if not self.scheduler:
            return False
        
        return self.scheduler.remove(script_name)
    
    def list_schedules(self) -> List[ScheduledJob]:
        """
        List all scheduled scripts.
        
        Returns:
            List of ScheduledJob objects
        """
        if not self.scheduler:
            return []
        
        return self.scheduler.list_jobs()
    
    def get_execution_history(
        self,
        script_name: Optional[str] = None,
        limit: int = 100
    ) -> List[ExecutionRecord]:
        """
        Get script execution history.
        
        Args:
            script_name: Optional script name filter
            limit: Maximum number of records
            
        Returns:
            List of ExecutionRecord objects
        """
        if not self.scheduler:
            return []
        
        return self.scheduler.get_history(script_name, limit)
