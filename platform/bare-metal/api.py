"""
Bare Metal Management API endpoints
"""

from flask import Blueprint, jsonify, request
from .hardware import HardwareDiscovery
from .storage import StorageManager
from .network import NetworkManager

bare_metal_bp = Blueprint('bare_metal', __name__)
hw_discovery = HardwareDiscovery()
storage_mgr = StorageManager()
network_mgr = NetworkManager()

@bare_metal_bp.route('/hardware', methods=['GET'])
def get_hardware():
    """Get hardware information"""
    return jsonify(hw_discovery.discover_all())

@bare_metal_bp.route('/storage/disks', methods=['GET'])
def list_disks():
    """List all disks"""
    return jsonify(storage_mgr.list_disks())

@bare_metal_bp.route('/network/interfaces', methods=['GET'])
def list_interfaces():
    """List network interfaces"""
    return jsonify(network_mgr.list_interfaces())
