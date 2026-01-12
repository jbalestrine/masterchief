"""Deployment API endpoints."""
import logging

from flask import Blueprint, jsonify, request

from .manager import DeploymentManager

logger = logging.getLogger(__name__)

deployments_bp = Blueprint('deployments', __name__)
deployment_manager = DeploymentManager()


@deployments_bp.route('/', methods=['GET'])
def list_deployments():
    """List all deployments.
    
    Query parameters:
        - status: Filter by status (pending, running, success, failed, stopped)
        - limit: Maximum number of deployments to return
        
    Returns:
        JSON response with list of deployments
    """
    try:
        status = request.args.get('status')
        limit = request.args.get('limit', type=int)
        
        deployments = deployment_manager.list_deployments(status=status, limit=limit)
        
        return jsonify({
            'success': True,
            'deployments': [d.to_dict() for d in deployments],
            'count': len(deployments)
        })
    except Exception as e:
        logger.error(f"Error listing deployments: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@deployments_bp.route('/<deployment_id>', methods=['GET'])
def get_deployment(deployment_id):
    """Get deployment information by ID.
    
    Args:
        deployment_id: Deployment identifier
        
    Returns:
        JSON response with deployment information
    """
    try:
        deployment = deployment_manager.get_deployment(deployment_id)
        
        if deployment:
            return jsonify({
                'success': True,
                'deployment': deployment.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Deployment not found'
            }), 404
    except Exception as e:
        logger.error(f"Error getting deployment {deployment_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@deployments_bp.route('/start', methods=['POST'])
def start_deployment():
    """Create and start a new deployment.
    
    Expects JSON body with:
        - name: Deployment name
        - target: Deployment target (e.g., environment)
        - config (optional): Deployment configuration
        
    Returns:
        JSON response with deployment result
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        name = data.get('name')
        target = data.get('target')
        config = data.get('config', {})
        
        if not name:
            return jsonify({
                'success': False,
                'error': 'Deployment name is required'
            }), 400
        
        if not target:
            return jsonify({
                'success': False,
                'error': 'Deployment target is required'
            }), 400
        
        # Create deployment
        deployment = deployment_manager.create_deployment(name, target, config)
        
        # Start deployment
        result = deployment_manager.start_deployment(deployment.id)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error starting deployment: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@deployments_bp.route('/<deployment_id>/stop', methods=['POST'])
def stop_deployment(deployment_id):
    """Stop a running deployment.
    
    Args:
        deployment_id: Deployment identifier
        
    Returns:
        JSON response with stop result
    """
    try:
        result = deployment_manager.stop_deployment(deployment_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error stopping deployment {deployment_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@deployments_bp.route('/<deployment_id>/logs', methods=['GET'])
def get_deployment_logs(deployment_id):
    """Get logs for a deployment.
    
    Args:
        deployment_id: Deployment identifier
        
    Returns:
        JSON response with deployment logs
    """
    try:
        logs = deployment_manager.get_deployment_logs(deployment_id)
        
        if logs is not None:
            return jsonify({
                'success': True,
                'logs': logs
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Deployment not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting logs for deployment {deployment_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
