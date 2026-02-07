import urllib.request, json, sys
payload = {
    'message': 'How do I deploy a Docker container using Docker Compose?',
    'session_id': 'default',
    'debug': True
}
req = urllib.request.Request('http://127.0.0.1:8080/api/echo/chat', data=json.dumps(payload).encode(), headers={'Content-Type':'application/json'})
try:
    with urllib.request.urlopen(req, timeout=120) as r:
        print(r.read().decode())
except Exception as e:
    print('request failed:', e, file=sys.stderr)
    sys.exit(1)
