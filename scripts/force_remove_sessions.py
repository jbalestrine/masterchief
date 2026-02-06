import urllib.request, json, sys

URL = 'http://127.0.0.1:8080/irc/session/remove'
NICKS = ['session_bot','session_botg','session_botgg']

for n in NICKS:
    payload = json.dumps({'nick': n}).encode('utf-8')
    req = urllib.request.Request(URL, data=payload, headers={'Content-Type':'application/json'})
    try:
        resp = urllib.request.urlopen(req, timeout=5)
        print(n + ':', resp.read().decode())
    except Exception as e:
        print(n + ': ERROR', e)
        sys.exit(1)
