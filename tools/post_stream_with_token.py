import urllib.request, json, sys
session = 'b9b289a8-2025-4da2-8bf3-cf58ce3a6913'
token = 'd10f2177431c478c80741b9dba24923d'
url = 'http://127.0.0.1:8080/irc/module/stream'
data = json.dumps({"session": session, "module": "demo", "args": []}).encode()
req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json", 'X-BRIDGE-TOKEN': token})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    body = resp.read().decode()
    print('STATUS', resp.status)
    print('BODY:', body)
    print('JSON:', json.loads(body))
except urllib.error.HTTPError as e:
    print('HTTPERR', e.code)
    try:
        print(e.read().decode())
    except Exception:
        pass
except Exception as e:
    print('ERR', e)
