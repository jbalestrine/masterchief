import sys
import json

urls = [
    'http://127.0.0.1:8080/api/addons/list',
    'http://127.0.0.1:8080/api/ide/ado/projects',
    'http://127.0.0.1:8080/api/ide/ado/pipelines',
]

try:
    import requests
except Exception:
    requests = None

for u in urls:
    try:
        if requests:
            r = requests.get(u, timeout=5)
            print('URL', u, 'STATUS', r.status_code)
            print(r.text)
        else:
            from urllib.request import urlopen
            from urllib.error import URLError
            try:
                r = urlopen(u, timeout=5)
                body = r.read().decode('utf-8')
                print('URL', u, 'STATUS', r.getcode())
                print(body)
            except URLError as e:
                print('ERR', u, 'URLError', e)
    except Exception as e:
        print('ERR', u, repr(e))
        try:
            import traceback
            traceback.print_exc()
        except Exception:
            pass

print('done')
