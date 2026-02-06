import requests, sys
base='http://127.0.0.1:8081'
conv_id='conv_1768665425393'
try:
    r = requests.get(base + '/api/conversations/summary', params={'conv_id': conv_id}, timeout=10)
    print('Status:', r.status_code)
    try:
        print(r.json())
    except Exception:
        print('Text response:\n', r.text)
except Exception as e:
    print('Request failed:', e)
