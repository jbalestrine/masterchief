import requests
import time

BASE = 'http://127.0.0.1:8081'
USERNAME = 'testuser'
PASSWORD = 'TestPass123'

s = requests.Session()
# Register (ignore failure)
try:
    r = s.post(BASE + '/register', data={'username': USERNAME, 'password': PASSWORD}, timeout=10)
    print('register status', r.status_code)
except Exception as e:
    print('register failed', e)

# Login
r = s.post(BASE + '/login', data={'username': USERNAME, 'password': PASSWORD}, allow_redirects=True, timeout=10)
print('login status', r.status_code)

# Create conversation
r = s.post(BASE + '/api/conversations/create', json={'name': 'Auto Test Conv'}, timeout=10)
print('create conv', r.status_code, r.text)
try:
    conv_id = r.json().get('conv_id')
except Exception:
    conv_id = None

if conv_id:
    print('conv id', conv_id)
    # Set active
    r = s.post(BASE + '/api/conversations/set_active', json={'conv_id': conv_id}, timeout=10)
    print('set active', r.status_code, r.text)
    # Send a few messages
    msgs = [
        'Hello, this is an automated test message about installation and indexing.',
        'Please remember that we discussed database backups and retention policies.'
    ]
    for m in msgs:
        r = s.post(BASE + '/api/echo/chat', json={'message': m, 'session_id': 'auto_test'}, timeout=30)
        print('chat ->', r.status_code, r.text)
        time.sleep(1)
    # Request manual index
    r = s.post(BASE + '/api/rag/index', json={'conv_id': conv_id}, timeout=30)
    print('index request', r.status_code, r.text)
else:
    print('no conv created; aborting')
