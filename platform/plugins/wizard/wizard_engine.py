"""
Main wizard orchestration engine for plugin creation.
"""

import uuid
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class WizardStep(Enum):
    """Wizard step enumeration."""
    TYPE_SELECTION = 1
    METADATA = 2
    CONFIGURATION = 3
    REVIEW = 4
    COMPLETE = 5


class PluginType(Enum):
    """Supported plugin types."""
    PHP = "php"
    PYTHON = "python"
    POWERSHELL = "powershell"
    NODEJS = "nodejs"
    SHELL = "shell"


@dataclass
class PluginMetadata:
    """Plugin metadata container."""
    name: str
    description: str
    version: str = "1.0.0"
    author: str = ""
    dependencies: List[str] = field(default_factory=list)
    plugin_type: str = "python"
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'author': self.author,
            'dependencies': self.dependencies,
            'plugin_type': self.plugin_type,
            'tags': self.tags,
        }


@dataclass
class WizardSession:
    """Wizard session state."""
    session_id: str
    current_step: WizardStep = WizardStep.TYPE_SELECTION
    plugin_type: Optional[PluginType] = None
    metadata: Optional[PluginMetadata] = None
    configuration: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    completed: bool = False
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'session_id': self.session_id,
            'current_step': self.current_step.name,
            'plugin_type': self.plugin_type.value if self.plugin_type else None,
            'metadata': self.metadata.to_dict() if self.metadata else None,
            'configuration': self.configuration,
            'created_at': self.created_at.isoformat(),
            'completed': self.completed,
            'error': self.error,
        }


class WizardEngine:
    """Main wizard orchestration engine."""
    
    def __init__(self, plugins_base_dir: str = "/opt/masterchief/plugins"):
        """
        Initialize wizard engine.
        
        Args:
            plugins_base_dir: Base directory for plugin installation
        """
        self.plugins_base_dir = plugins_base_dir
        self.sessions: Dict[str, WizardSession] = {}
        logger.info(f"Wizard engine initialized with base dir: {plugins_base_dir}")
    
    def start_session(self) -> WizardSession:
        """
        Start a new wizard session.
        
        Returns:
            New wizard session
        """
        session_id = str(uuid.uuid4())
        session = WizardSession(session_id=session_id)
        self.sessions[session_id] = session
        logger.info(f"Started wizard session: {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[WizardSession]:
        """
        Get an existing wizard session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Wizard session or None if not found
        """
        return self.sessions.get(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a wizard session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted wizard session: {session_id}")
            return True
        return False
    
    def advance_step(self, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Advance wizard to next step with provided data.
        
        Args:
            session_id: Session ID
            data: Step data
            
        Returns:
            Result dictionary with status and next step info
        """
        session = self.get_session(session_id)
        if not session:
            return {
                'success': False,
                'error': 'Session not found'
            }
        
        try:
            if session.current_step == WizardStep.TYPE_SELECTION:
                return self._process_type_selection(session, data)
            elif session.current_step == WizardStep.METADATA:
                return self._process_metadata(session, data)
            elif session.current_step == WizardStep.CONFIGURATION:
                return self._process_configuration(session, data)
            elif session.current_step == WizardStep.REVIEW:
                return self._process_review(session, data)
            else:
                return {
                    'success': False,
                    'error': 'Invalid step'
                }
        except Exception as e:
            logger.error(f"Error advancing wizard step: {e}")
            session.error = str(e)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_type_selection(self, session: WizardSession, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process plugin type selection."""
        plugin_type = data.get('plugin_type')
        
        if not plugin_type:
            return {
                'success': False,
                'error': 'Plugin type is required'
            }
        
        try:
            session.plugin_type = PluginType(plugin_type)
            session.current_step = WizardStep.METADATA
            logger.info(f"Session {session.session_id}: Selected type {plugin_type}")
            
            return {
                'success': True,
                'current_step': session.current_step.name,
                'message': f'Selected plugin type: {plugin_type}'
            }
        except ValueError:
            return {
                'success': False,
                'error': f'Invalid plugin type: {plugin_type}'
            }
    
    def _process_metadata(self, session: WizardSession, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process metadata collection."""
        required_fields = ['name', 'description']
        
        for field in required_fields:
            if not data.get(field):
                return {
                    'success': False,
                    'error': f'Missing required field: {field}'
                }
        
        # Create metadata
        session.metadata = PluginMetadata(
            name=data['name'],
            description=data['description'],
            version=data.get('version', '1.0.0'),
            author=data.get('author', ''),
            dependencies=data.get('dependencies', []),
            plugin_type=session.plugin_type.value if session.plugin_type else 'python',
            tags=data.get('tags', [])
        )
        
        session.current_step = WizardStep.CONFIGURATION
        logger.info(f"Session {session.session_id}: Set metadata for {data['name']}")
        
        return {
            'success': True,
            'current_step': session.current_step.name,
            'message': 'Metadata collected successfully'
        }
    
    def _process_configuration(self, session: WizardSession, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process plugin-specific configuration."""
        session.configuration = data
        session.current_step = WizardStep.REVIEW
        logger.info(f"Session {session.session_id}: Configuration set")
        
        return {
            'success': True,
            'current_step': session.current_step.name,
            'message': 'Configuration collected successfully'
        }
    
    def _process_review(self, session: WizardSession, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process review and finalize."""
        if data.get('confirm') != True:
            return {
                'success': False,
                'error': 'Confirmation required'
            }
        
        # Import here to avoid circular dependency (these modules import from wizard_engine)
        from .folder_generator import FolderGenerator
        from .template_generator import TemplateGenerator
        
        # Create folder structure
        folder_gen = FolderGenerator(self.plugins_base_dir)
        plugin_path = folder_gen.generate_structure(session.metadata.name)
        
        # Generate templates
        template_gen = TemplateGenerator()
        template_gen.generate_templates(
            plugin_path,
            session.plugin_type.value if session.plugin_type else 'python',
            session.metadata,
            session.configuration
        )
        
        session.current_step = WizardStep.COMPLETE
        session.completed = True
        logger.info(f"Session {session.session_id}: Plugin created at {plugin_path}")
        
        return {
            'success': True,
            'current_step': session.current_step.name,
            'message': 'Plugin created successfully',
            'plugin_path': str(plugin_path)
        }
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get wizard session status.
        
        Args:
            session_id: Session ID
            
        Returns:
            Status dictionary
        """
        session = self.get_session(session_id)
        if not session:
            return {
                'success': False,
                'error': 'Session not found'
            }
        
        return {
            'success': True,
            'session': session.to_dict()
        }
