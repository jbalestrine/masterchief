import requests, time, json

# Auto-detect running server port (try common dev ports)
s = requests.Session()
base = None
for p in (8081, 8080, 5000):
    try:
        probe = s.get(f'http://127.0.0.1:{p}/api/echo/sessions', timeout=1)
        if probe.status_code == 200:
            base = f'http://127.0.0.1:{p}'
            break
    except Exception:
        pass
if not base:
    base = 'http://127.0.0.1:8080'
print('Using base', base)
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
r = s.post(base + '/api/echo/chat', json={'message':'what\'s my name?', 'session_id':'testsession'}, timeout=30)
print('Status', r.status_code)
try:
    print(json.dumps(r.json(), indent=2))
except Exception:
    print(r.text)
