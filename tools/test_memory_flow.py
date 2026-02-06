import requests, json, time
s = requests.Session()
base = 'http://127.0.0.1:8081'
try:
    print('Posting test message...')
    r = s.post(base + '/api/echo/chat', json={'message': "Test memory: my name is EchoTester and I like cyan."}, timeout=60)
    print('Status:', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
    time.sleep(1)
    print('\nGetting session...')
    r = s.get(base + '/api/session/get', timeout=10)
    print('Status:', r.status_code)
    print(r.text)
    print('\nListing conversations...')
    r = s.get(base + '/api/conversations/list', timeout=10)
    print('Status:', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
    convs = r.json().get('conversations', []) if r.status_code==200 else []
    if convs:
        cid = convs[0]['id']
        print('\nFetching summary for', cid)
        r = s.get(base + '/api/conversations/summary', params={'conv_id': cid}, timeout=10)
        print('Status:', r.status_code)
        try:
            print(json.dumps(r.json(), indent=2))
        except Exception:
            print(r.text)
        print('\nFetching facts file raw...')
        # try to fetch facts via direct file read endpoint not available; attempt to GET load view
        r = s.get(base + f'/conversations/load/{cid}', timeout=10)
        print('Load page status:', r.status_code)
        print('Page snippet:', r.text[:500])
except Exception as e:
    print('Error during test:', e)
