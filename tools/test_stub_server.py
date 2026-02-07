#!/usr/bin/env python3
"""Minimal HTTP stub used to satisfy test imports that expect services on :8081

Run: python tools/test_stub_server.py
"""
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return jsonify({'ok': True, 'service': 'stub_server'})


@app.route('/api/session/get', methods=['GET'])
def session_get():
    return jsonify({'ok': True, 'session': {'id': 'stub-session', 'user': 'tester'}})


@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_catchall(path):
    # Generic stub response for any API path tests may call during collection
    data = {'ok': True, 'path': path, 'method': request.method}
    return jsonify(data)


if __name__ == '__main__':
    # Bind to 0.0.0.0 so tests can access via localhost/127.0.0.1
    app.run(host='0.0.0.0', port=8081)
