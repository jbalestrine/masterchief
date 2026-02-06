import urllib.request, json, sys
req = urllib.request.Request('http://127.0.0.1:8080/api/resources/rescan', data=b'{}', headers={'Content-Type':'application/json'})
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        print(r.read().decode())
except Exception as e:
    print('ERROR', e)
