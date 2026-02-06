#!/usr/bin/env python3
import json,urllib.request,urllib.error,sys
url='http://127.0.0.1:8081/irc/send'
data=json.dumps({'session':'796c6efb-f07e-418e-8abd-63bb905bf78a','message':'PRIVMSG #masterchief :Hello from 8081 test'}).encode()
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
