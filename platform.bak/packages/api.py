"""
Package Manager Hub API endpoints
"""

from flask import Blueprint, jsonify, request
from .manager import PackageManager

packages_bp = Blueprint('packages', __name__)
package_manager = PackageManager()

@packages_bp.route('/search', methods=['GET'])
def search_packages():
    """Search for packages"""
    query = request.args.get('q', '')
    manager = request.args.get('manager', 'all')
    results = package_manager.search(query, manager)
    return jsonify(results)

@packages_bp.route('/installed', methods=['GET'])
def list_installed():
    """List installed packages"""
    manager = request.args.get('manager', 'all')
    packages = package_manager.list_installed(manager)
    return jsonify(packages)

@packages_bp.route('/install', methods=['POST'])
def install_package():
    """Install a package"""
    data = request.json
    package = data.get('package')
    manager = data.get('manager', 'apt')
    success = package_manager.install(package, manager)
    return jsonify({'success': success})

@packages_bp.route('/remove', methods=['POST'])
def remove_package():
    """Remove a package"""
    data = request.json
    package = data.get('package')
    manager = data.get('manager', 'apt')
    success = package_manager.remove(package, manager)
    return jsonify({'success': success})

@packages_bp.route('/update', methods=['POST'])
def update_packages():
    """Update all packages"""
    manager = request.json.get('manager', 'apt') if request.json else 'apt'
    success = package_manager.update_all(manager)
    return jsonify({'success': success})
