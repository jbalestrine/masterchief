"""
REST API endpoints for Plugin Wizard.
"""

from flask import Blueprint, request, jsonify
import logging
from typing import Dict, Any

from .wizard_engine import WizardEngine
from .step_handlers import StepHandler
from .validators import PluginValidator

logger = logging.getLogger(__name__)

# Create blueprint
wizard_bp = Blueprint('wizard', __name__)

# Initialize components
wizard_engine = WizardEngine()
step_handler = StepHandler()
validator = PluginValidator()


@wizard_bp.route('/start', methods=['POST'])
def start_wizard():
    """
    Start a new wizard session.
    
    POST /api/wizard/start
    
    Returns:
        JSON response with session_id and initial step data
    """
    try:
        session = wizard_engine.start_session()
        
        # Get initial step data
        step_data = step_handler.get_step_data('type_selection')
        
        return jsonify({
            'success': True,
            'session_id': session.session_id,
            'current_step': session.current_step.name,
            'step_data': step_data
        }), 201
        
    except Exception as e:
        logger.error(f"Error starting wizard: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@wizard_bp.route('/<session_id>/step/<int:step_num>', methods=['GET'])
def get_step(session_id: str, step_num: int):
    """
    Get step data for a specific step.
    
    GET /api/wizard/{session_id}/step/{step_num}
    
    Args:
        session_id: Wizard session ID
        step_num: Step number (1-5)
        
    Returns:
        JSON response with step data
    """
    try:
        session = wizard_engine.get_session(session_id)
        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        # Map step number to step type
        step_types = {
            1: 'type_selection',
            2: 'metadata',
            3: 'configuration',
            4: 'review',
            5: 'complete'
        }
        
        step_type = step_types.get(step_num)
        if not step_type:
            return jsonify({
                'success': False,
                'error': 'Invalid step number'
            }), 400
        
        # Get step data
        plugin_type = session.plugin_type.value if session.plugin_type else None
        step_data = step_handler.get_step_data(step_type, plugin_type)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'current_step': session.current_step.name,
            'step_data': step_data
        })
        
    except Exception as e:
        logger.error(f"Error getting step: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@wizard_bp.route('/<session_id>/step/<int:step_num>', methods=['POST'])
def submit_step(session_id: str, step_num: int):
    """
    Submit step data and advance to next step.
    
    POST /api/wizard/{session_id}/step/{step_num}
    
    Args:
        session_id: Wizard session ID
        step_num: Step number (1-5)
        
    Request Body:
        JSON data for the step
        
    Returns:
        JSON response with result and next step data
    """
    try:
        session = wizard_engine.get_session(session_id)
        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        # Validate based on current step
        if step_num == 2:  # Metadata step
            is_valid, error = validator.validate_metadata(data)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': error
                }), 400
        
        elif step_num == 3:  # Configuration step
            plugin_type = session.plugin_type.value if session.plugin_type else None
            if plugin_type:
                is_valid, error = validator.validate_configuration(plugin_type, data)
                if not is_valid:
                    return jsonify({
                        'success': False,
                        'error': error
                    }), 400
        
        # Advance to next step
        result = wizard_engine.advance_step(session_id, data)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        # Get next step data if not complete
        if session.current_step.value < 5:
            step_types = ['type_selection', 'metadata', 'configuration', 'review', 'complete']
            next_step_type = step_types[session.current_step.value - 1]
            plugin_type = session.plugin_type.value if session.plugin_type else None
            step_data = step_handler.get_step_data(next_step_type, plugin_type)
            result['step_data'] = step_data
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error submitting step: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@wizard_bp.route('/<session_id>/complete', methods=['POST'])
def complete_wizard(session_id: str):
    """
    Finalize and complete the wizard session.
    
    POST /api/wizard/{session_id}/complete
    
    Args:
        session_id: Wizard session ID
        
    Request Body:
        {
            "confirm": true
        }
        
    Returns:
        JSON response with completion status
    """
    try:
        session = wizard_engine.get_session(session_id)
        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        data = request.get_json() or {}
        
        # Advance to complete step
        result = wizard_engine.advance_step(session_id, data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error completing wizard: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@wizard_bp.route('/<session_id>/status', methods=['GET'])
def get_wizard_status(session_id: str):
    """
    Get wizard session status.
    
    GET /api/wizard/{session_id}/status
    
    Args:
        session_id: Wizard session ID
        
    Returns:
        JSON response with session status
    """
    try:
        result = wizard_engine.get_session_status(session_id)
        
        if not result.get('success'):
            return jsonify(result), 404
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@wizard_bp.route('/<session_id>', methods=['DELETE'])
def cancel_wizard(session_id: str):
    """
    Cancel and delete wizard session.
    
    DELETE /api/wizard/{session_id}
    
    Args:
        session_id: Wizard session ID
        
    Returns:
        JSON response with deletion status
    """
    try:
        success = wizard_engine.delete_session(session_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Session cancelled successfully'
        })
        
    except Exception as e:
        logger.error(f"Error cancelling wizard: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@wizard_bp.route('/sessions', methods=['GET'])
def list_sessions():
    """
    List all active wizard sessions.
    
    GET /api/wizard/sessions
    
    Returns:
        JSON response with list of sessions
    """
    try:
        sessions = [
            session.to_dict()
            for session in wizard_engine.sessions.values()
        ]
        
        return jsonify({
            'success': True,
            'sessions': sessions,
            'count': len(sessions)
        })
        
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
