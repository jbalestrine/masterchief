import urllib.request, json
req=urllib.request.Request('http://127.0.0.1:8080/api/echo/preload_model', data=json.dumps({'warm':False}).encode(), headers={'Content-Type':'application/json'})
with urllib.request.urlopen(req, timeout=120) as r:
    print('HTTP', r.status)
    print(r.read().decode())
