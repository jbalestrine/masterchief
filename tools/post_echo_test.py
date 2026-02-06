import requests
r = requests.post('http://127.0.0.1:8080/api/echo/chat', json={'message':'hello test','session_id':'test_restore'})
print('STATUS', r.status_code)
try:
    print(r.json())
except Exception:
    print(r.text)
