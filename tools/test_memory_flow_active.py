import requests, json, time
s = requests.Session()
base = 'http://127.0.0.1:8081'
try:
    print('Listing conversations...')
    r = s.get(base + '/api/conversations/list', timeout=10)
    print('Status:', r.status_code)
    print(r.text)
    convs = r.json().get('conversations', []) if r.status_code==200 else []
    if not convs:
        print('No conversations found; creating one')
        r = s.post(base + '/api/conversations/create', json={'name':'Auto Test Conv2'}, timeout=10)
        print('create', r.status_code, r.text)
        convs = s.get(base + '/api/conversations/list').json().get('conversations', [])
    cid = convs[0]['id']
    print('Setting active conv to', cid)
    r = s.post(base + '/api/conversations/set_active', json={'conv_id': cid}, timeout=10)
    print('set active status', r.status_code, r.text)
    print('\nPosting test message...')
    r = s.post(base + '/api/echo/chat', json={'message': "Remember: my favorite drink is matcha."}, timeout=60)
    print('Chat Status:', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
    time.sleep(1)
    print('\nFetching summary for', cid)
    r = s.get(base + '/api/conversations/summary', params={'conv_id': cid}, timeout=10)
    print('Summary status', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
    print('\nFetching facts for', cid)
    r = s.get(base + '/api/conversations/facts', params={'conv_id': cid}, timeout=10)
    print('Facts status', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
except Exception as e:
    print('Error during test:', e)
