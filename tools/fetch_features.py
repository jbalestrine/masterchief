import urllib.request

ENDPOINTS = [
    '/api/features/enabled',
    '/api/features',
    '/api/features/list',
    '/features',
    '/api/features/enabled?raw=1',
]

BASE = 'http://127.0.0.1:8080'

for e in ENDPOINTS:
    url = BASE + e
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            print('---', e, '---')
            print(r.read().decode())
    except Exception as ex:
        print('---', e, 'ERROR:', ex)
