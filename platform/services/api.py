"""
Service Manager API endpoints
"""

from flask import Blueprint, jsonify, request
from .manager import ServiceManager

services_bp = Blueprint('services', __name__)
service_manager = ServiceManager()

@services_bp.route('/', methods=['GET'])
def list_services():
    """List all services"""
    services = service_manager.list_services()
    return jsonify([
        {
            'name': s.name,
            'status': s.status.value,
            'enabled': s.enabled,
            'description': s.description
        }
        for s in services
    ])

@services_bp.route('/<service>', methods=['GET'])
def get_service(service):
    """Get specific service status"""
    svc = service_manager.get_status(service)
    if svc:
        return jsonify({
            'name': svc.name,
            'status': svc.status.value,
            'enabled': svc.enabled,
            'description': svc.description
        })
    return jsonify({'error': 'Service not found'}), 404

@services_bp.route('/<service>/start', methods=['POST'])
def start_service(service):
    """Start a service"""
    success = service_manager.start(service)
    return jsonify({'success': success})

@services_bp.route('/<service>/stop', methods=['POST'])
def stop_service(service):
    """Stop a service"""
    success = service_manager.stop(service)
    return jsonify({'success': success})

@services_bp.route('/<service>/restart', methods=['POST'])
def restart_service(service):
    """Restart a service"""
    success = service_manager.restart(service)
    return jsonify({'success': success})

@services_bp.route('/<service>/enable', methods=['POST'])
def enable_service(service):
    """Enable a service"""
    success = service_manager.enable(service)
    return jsonify({'success': success})

@services_bp.route('/<service>/disable', methods=['POST'])
def disable_service(service):
    """Disable a service"""
    success = service_manager.disable(service)
    return jsonify({'success': success})

@services_bp.route('/<service>/logs', methods=['GET'])
def get_logs(service):
    """Get service logs"""
    lines = request.args.get('lines', 100, type=int)
    logs = service_manager.get_logs(service, lines)
    return jsonify({'logs': logs})
