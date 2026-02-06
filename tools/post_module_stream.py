import urllib.request, json, sys
url = 'http://127.0.0.1:8080/irc/module/stream'
data = json.dumps({"session":"a61274d0-6284-425c-a41e-a7cf13de8af5","module":"demo","args":[]}).encode()
req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json"})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    print('STATUS', resp.status)
    body = resp.read().decode(errors='replace')
    print('BODY:', body)
    try:
        print('JSON:', json.loads(body))
    except Exception as e:
        print('JSON parse error', e)
except Exception as e:
    print('ERR', type(e), e)
    try:
        if hasattr(e, 'read'):
            print('ERRBODY', e.read().decode(errors='replace'))
    except Exception:
        pass
