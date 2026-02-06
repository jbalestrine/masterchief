import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

url = 'http://127.0.0.1:8080/api/echo/chat'
data = json.dumps({'message': 'smoke test: hello'}).encode('utf-8')
req = Request(url, data=data, headers={'Content-Type': 'application/json'})
try:
	resp = urlopen(req, timeout=10)
	print(json.dumps(json.loads(resp.read().decode('utf-8')), indent=2))
except HTTPError as e:
	body = e.read().decode('utf-8', errors='replace')
	print(f'HTTP {e.code}: {body}')
