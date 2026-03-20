"""addon.py — MasterChief Blueprint for test-mod-fix2"""
from flask import Blueprint, jsonify, request, render_template_string, session, abort
from pathlib import Path

bp = Blueprint('test-mod-fix2', __name__, url_prefix='/modules/test-mod-fix2')
@bp.route('/')
def index():
    return render_template_string(open(Path(__file__).parent / 'templates' / 'index.html').read())


def init(app):
    """Called by MasterChief to register this module."""
    app.register_blueprint(bp)
    print(f'Module test-mod-fix2 registered at /modules/test-mod-fix2')
