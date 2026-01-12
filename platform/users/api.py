"""
User Management API endpoints
"""

from flask import Blueprint, jsonify, request

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
def list_users():
    """List all users"""
    return jsonify({
        'users': [
            {'username': 'root', 'uid': 0, 'groups': ['root']},
            {'username': 'masterchief', 'uid': 1000, 'groups': ['sudo', 'docker']},
        ]
    })

@users_bp.route('/<username>', methods=['GET'])
def get_user(username):
    """Get user details"""
    return jsonify({
        'username': username,
        'uid': 1000,
        'groups': ['sudo', 'docker'],
        'shell': '/bin/bash',
        'home': f'/home/{username}'
    })
