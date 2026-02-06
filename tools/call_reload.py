import requests
import sys

try:
    r = requests.post('http://127.0.0.1:8081/api/rag/reload', timeout=30)
    print(r.status_code)
    try:
        print(r.json())
    except Exception:
        print(r.text)
except Exception as e:
    print('error', e)
    sys.exit(1)
