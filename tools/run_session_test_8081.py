import requests, time, json
s = requests.Session()
base = 'http://127.0.0.1:8081'
print('Posting name message...')
r = s.post(base + '/api/echo/chat', json={'message':'my name is joe', 'session_id':'testsession'}, timeout=30)
print('Status', r.status_code)
try:
    print(json.dumps(r.json(), indent=2))
except Exception:
    print(r.text)
print('Sleeping 1s...')
time.sleep(1)
print('Asking name...')
r = s.post(base + '/api/echo/chat', json={'message':"what's my name?", 'session_id':'testsession'}, timeout=30)
print('Status', r.status_code)
try:
    print(json.dumps(r.json(), indent=2))
except Exception:
    print(r.text)
