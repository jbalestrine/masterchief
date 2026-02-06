import importlib.util
import os
import json
import time

spec = importlib.util.spec_from_file_location('main', os.path.join(os.getcwd(), 'main.py'))
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)

app = getattr(main, 'app')
conv_mgr = getattr(main, 'conv_mgr')

# find any existing conversation under data/conversations
base_root = os.path.join(os.getcwd(), 'data', 'conversations')
username = None
conv_id = None
if os.path.exists(base_root):
    for user in os.listdir(base_root):
        ud = os.path.join(base_root, user)
        if not os.path.isdir(ud):
            continue
        files = [f for f in os.listdir(ud) if f.endswith('.json') and not f.endswith('.facts.json') and not f.endswith('.texts.json')]
        if files:
            username = user
            conv_id = files[0].replace('.json','')
            break
if not username or not conv_id:
    print('No existing conversations found under data/conversations')
    raise SystemExit(1)
print('Using user:', username, 'conv:', conv_id)

with app.test_client() as c:
    with c.session_transaction() as sess:
        sess['username'] = username
        sess['active_conv'] = conv_id
        sess['use_rag'] = False
    msg = 'Remember: my favorite drink is matcha.'
    r = c.post('/api/echo/chat', json={'message': msg, 'session_id': 'testsess'})
    print('POST status', r.status_code)
    try:
        print(json.dumps(r.get_json(), indent=2))
    except Exception:
        print(r.data.decode('utf-8'))
    # inspect session memory in-process
    try:
        mem = main.get_session_memory('testsess')
        print('\nSession memory facts:', mem.get('facts'))
        print('Session summary:', mem.get('summary'))
    except Exception as e:
        print('Failed to read session memory:', e)
    # allow background threads short time
    time.sleep(0.5)
    base = os.path.join(os.getcwd(), 'data', 'conversations', username)
    facts_file = os.path.join(base, f"{conv_id}.facts.json")
    conv_file = os.path.join(base, f"{conv_id}.json")
    print('\nFacts file exists:', os.path.exists(facts_file))
    if os.path.exists(facts_file):
        print('Facts:', json.dumps(json.loads(open(facts_file,'r',encoding='utf-8').read()), indent=2))
    print('\nConv summary (from file):')
    if os.path.exists(conv_file):
        print(json.dumps(json.loads(open(conv_file,'r',encoding='utf-8').read()).get('summary',''), indent=2))
    else:
        print('conv file missing')
