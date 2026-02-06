#!/usr/bin/env python3
import json,urllib.request,urllib.error,sys
url='http://127.0.0.1:8080/irc/send'
data=json.dumps({'session':'b79850fc-5dfa-4005-b6ed-3c87e962a28f','message':'PRIVMSG #masterchief :Hello again from test'}).encode()
req=urllib.request.Request(url, data=data, headers={'Content-Type':'application/json'})
try:
    with urllib.request.urlopen(req) as r:
        print('STATUS', r.status)
        print(r.read().decode())
except urllib.error.HTTPError as e:
    print('HTTP ERROR', e.code)
    try:
        print(e.read().decode())
    except Exception as e2:
        print('failed to read body', e2)
except Exception as e:
    print('ERROR', e)
    sys.exit(1)
