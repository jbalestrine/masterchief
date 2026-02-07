import requests
import json

try:
    r = requests.post('http://127.0.0.1:8080/api/echo/preload_model', json={'warm': True}, timeout=120)
    print('STATUS', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
except Exception as e:
    print('ERROR', e)
