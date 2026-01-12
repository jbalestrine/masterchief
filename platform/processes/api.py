"""
Process Manager API endpoints
"""

from flask import Blueprint, jsonify, request
from .manager import ProcessManager

processes_bp = Blueprint('processes', __name__)
process_manager = ProcessManager()

@processes_bp.route('/', methods=['GET'])
def list_processes():
    """List all processes"""
    processes = process_manager.list_processes()
    return jsonify(processes)

@processes_bp.route('/<int:pid>', methods=['GET'])
def get_process(pid):
    """Get specific process info"""
    proc = process_manager.get_process(pid)
    if proc:
        return jsonify(proc)
    return jsonify({'error': 'Process not found'}), 404

@processes_bp.route('/<int:pid>/kill', methods=['POST'])
def kill_process(pid):
    """Kill a process"""
    signal = request.json.get('signal', 'TERM') if request.json else 'TERM'
    success = process_manager.kill_process(pid, signal)
    return jsonify({'success': success})
