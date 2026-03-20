"""addon.py — MasterChief Blueprint for test-mod-fix"""
from flask import Blueprint, jsonify, request, render_template_string, session, abort
from pathlib import Path

bp = Blueprint('test-mod-fix', __name__, url_prefix='/modules/test-mod-fix')
@bp.route('/')
def index():
    return render_template_string(open(Path(__file__).parent / 'templates' / 'index.html').read())

@bp.route('/api/status', methods=['GET'])
def api_status():
    return jsonify({'module': 'test-mod-fix', 'status': 'ok'})

@bp.route('/api/action', methods=['POST'])
def api_action():
    payload = request.get_json() or {}
    # TODO: implement action logic
    return jsonify({'success': True, 'payload': payload})


def init(app):
    """Called by MasterChief to register this module."""
    app.register_blueprint(bp)
    print(f'Module test-mod-fix registered at /modules/test-mod-fix')
