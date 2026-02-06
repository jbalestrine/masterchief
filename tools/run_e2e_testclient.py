import importlib.util
import os
import json
import time

spec = importlib.util.spec_from_file_location('main_mod', os.path.join(os.getcwd(), 'main.py'))
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)

app = getattr(main, 'app')

def post_chat(client, message, session_id='testsession'):
    r = client.post('/api/echo/chat', json={'message': message, 'session_id': session_id})
    try:
        return r.status_code, r.get_json()
    except Exception:
        return r.status_code, r.data.decode('utf-8')

with app.test_client() as c:
    print('--- run_session_test (via test client) ---')
    status, body = post_chat(c, 'my name is joe', 'testsession')
    print('POST my name is joe ->', status)
    print(json.dumps(body, indent=2))
    time.sleep(0.5)
    status, body = post_chat(c, "what's my name?", 'testsession')
    print("POST what's my name? ->", status)
    print(json.dumps(body, indent=2))

    print('\n--- test_memory_flow_active_fixed (partial) ---')
    # Call conversations summary and facts endpoints for a sample conv id if present
    # Use defaults from main.ConvManager if available
    conv_id = 'conv_test'
    r = c.get(f'/api/conversations/summary?username=default&conv_id={conv_id}')
    print('/api/conversations/summary ->', r.status_code)
    try:
        print(json.dumps(r.get_json(), indent=2))
    except Exception:
        print(r.data.decode('utf-8'))
    r2 = c.get(f'/api/conversations/facts?username=default&conv_id={conv_id}')
    print('/api/conversations/facts ->', r2.status_code)
    try:
        print(json.dumps(r2.get_json(), indent=2))
    except Exception:
        print(r2.data.decode('utf-8'))

    print('\nE2E (via test client) completed')
