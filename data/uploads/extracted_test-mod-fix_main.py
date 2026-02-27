"""
Main server for test-mod-fix
test module
Run directly:  python main.py
Or load via the addon system which calls addon.py init().
"""
from flask import Flask, jsonify, render_template_string
import os

app = Flask(__name__)

INDEX_HTML = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>test-mod-fix</title>
  <style>
    body {background:#1a1a1a;color:#e0e0e0;font-family:Arial,sans-serif;padding:40px;text-align:center;}
    h1 {color:#4CAF50;} a {color:#7B1FA2;}
  </style>
</head>
<body>
  <h1>🧩 test-mod-fix</h1>
  <p>test module</p>
  <p><a href="/api/status">API Status</a></p>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/api/status')
def status():
    return jsonify({'module': 'test-mod-fix', 'status': 'ok', 'version': '0.1.0'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f'[MC] Running on http://localhost:{port}', flush=True)
    app.run(host='0.0.0.0', port=port, debug=False)
