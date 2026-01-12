"""
API Endpoints for Script Wizard
"""

from flask import Blueprint, jsonify, request
from .wizard import ScriptWizard
from .generators import ScriptGenerator

# Create blueprint
script_wizard_bp = Blueprint('script_wizard', __name__, url_prefix='/api/script-wizard')

# Initialize wizard and generator
wizard = ScriptWizard()
generator = ScriptGenerator()


@script_wizard_bp.route('/templates', methods=['GET'])
def list_templates():
    """
    GET /api/script-wizard/templates - List available templates
    
    Returns:
        JSON list of available script templates
    """
    templates = wizard.list_templates()
    return jsonify({
        "success": True,
        "templates": templates
    })


@script_wizard_bp.route('/generate', methods=['POST'])
def generate_script():
    """
    POST /api/script-wizard/generate - Generate script from template
    
    Request body:
        {
            "template_id": "deployment",
            "parameters": {"app_name": "myapp", "environment": "prod"}
        }
    
    Returns:
        Generated script content
    """
    data = request.get_json()
    
    if not data or 'template_id' not in data:
        return jsonify({
            "success": False,
            "error": "Missing template_id"
        }), 400
    
    template_id = data['template_id']
    parameters = data.get('parameters', {})
    
    try:
        script_content = generator.generate(template_id, parameters)
        return jsonify({
            "success": True,
            "script": script_content
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@script_wizard_bp.route('/validate', methods=['POST'])
def validate_parameters():
    """
    POST /api/script-wizard/validate - Validate script parameters
    
    Request body:
        {
            "parameters": {"app_name": "myapp", "environment": "prod"}
        }
    
    Returns:
        Validation result
    """
    data = request.get_json()
    
    if not data or 'parameters' not in data:
        return jsonify({
            "success": False,
            "error": "Missing parameters"
        }), 400
    
    parameters = data['parameters']
    is_valid = wizard.validate_parameters(parameters)
    
    return jsonify({
        "success": True,
        "valid": is_valid
    })


@script_wizard_bp.route('/preview', methods=['POST'])
def preview_script():
    """
    POST /api/script-wizard/preview - Preview generated script
    
    Request body:
        {
            "template_id": "deployment",
            "parameters": {"app_name": "myapp", "environment": "prod"}
        }
    
    Returns:
        Script preview (same as generate but without saving)
    """
    data = request.get_json()
    
    if not data or 'template_id' not in data:
        return jsonify({
            "success": False,
            "error": "Missing template_id"
        }), 400
    
    template_id = data['template_id']
    parameters = data.get('parameters', {})
    
    try:
        script_content = wizard.generate_script(template_id, parameters)
        return jsonify({
            "success": True,
            "preview": script_content
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
