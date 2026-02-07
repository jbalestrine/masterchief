import requests
import json

url = 'http://127.0.0.1:8080/api/echo/chat'
payload = {'message': 'Say hello and summarize your capabilities briefly.'}
try:
    r = requests.post(url, json=payload, timeout=60)
    print('STATUS', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
except Exception as e:
    print('ERROR', e)
