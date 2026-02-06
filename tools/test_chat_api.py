import json
import urllib.request

url = 'http://127.0.0.1:8081/api/echo/chat'
body = json.dumps({"message": "automated test", "llm_only": True}).encode('utf-8')
req = urllib.request.Request(url, data=body, headers={'Content-Type':'application/json'})
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        print('STATUS', resp.status)
        print(resp.read().decode('utf-8'))
except Exception as e:
    print('ERROR', repr(e))
