import json
import urllib.request
import sys

url = 'http://127.0.0.1:8090/api/echo/generate_image'
payload = {
    'prompt': 'A serene mountain landscape at sunrise in photorealistic style.',
    'size': '512x512',
    'style': 'photorealistic',
    'session_id': 'test'
}

req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read().decode('utf-8')
        print('STATUS', resp.status)
        print('BODY', body)
except Exception as e:
    print('ERROR', repr(e))
    sys.exit(2)
