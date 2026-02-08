"""
CMDB & Asset Inventory API endpoints
"""

from flask import Blueprint, jsonify, request

cmdb_bp = Blueprint('cmdb', __name__)

@cmdb_bp.route('/assets', methods=['GET'])
def list_assets():
    """List all assets"""
    return jsonify({
        'assets': [
            {
                'id': 'srv-001',
                'type': 'server',
                'hostname': 'masterchief-01',
                'status': 'active'
            }
        ]
    })

@cmdb_bp.route('/assets/<asset_id>', methods=['GET'])
def get_asset(asset_id):
    """Get asset details"""
    return jsonify({
        'id': asset_id,
        'type': 'server',
        'hostname': 'masterchief-01',
        'hardware': {
            'cpu': 'Intel Xeon',
            'ram': '16GB',
            'disk': '500GB'
        },
        'software': {
            'os': 'MasterChief OS 1.0',
            'kernel': '5.15.0'
        }
    })

@cmdb_bp.route('/discover', methods=['POST'])
def discover_assets():
    """Trigger asset discovery"""
    return jsonify({'success': True, 'discovered': 1})
