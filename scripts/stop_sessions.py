import urllib.request
import json

URL = 'http://127.0.0.1:8080/irc/session/stop'
NICKS = ['session_bot','session_botg','session_botgg']

for nick in NICKS:
    data = json.dumps({'nick': nick}).encode('utf-8')
    req = urllib.request.Request(URL, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode('utf-8')
            print(nick + ': ' + body)
    except Exception as e:
        print(nick + ': ERROR ' + str(e))
