#!/usr/bin/env python3
import json,urllib.request,sys
SERVER='http://127.0.0.1:8081'
# Edit these values if needed
session_a = '796c6efb-f07e-418e-8abd-63bb905bf78a'  # original tester8081
token_a = '4254cb4481b140148a1b64908fe6f61f'
session_b = 'd2ba990a-aa3d-414c-ac13-71a759c12285'  # sessionB
channel = '#masterchief'
# Send bridged message to session_a
url = SERVER + '/irc/bridge_send'
payload = {'session': session_a, 'channel': channel, 'message': 'Bridge test from script', 'bridge_token': token_a}
req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={'Content-Type':'application/json'})
print('POST', url, payload)
try:
    resp = urllib.request.urlopen(req)
    print('bridge_send status', resp.status)
    print(resp.read().decode())
except Exception as e:
    print('bridge_send error', e)
# Poll recv for session_b
try:
    r = urllib.request.urlopen(SERVER + f"/irc/recv?session={session_b}")
    print('\n/irc/recv for session_b:')
    print(r.read().decode())
except Exception as e:
    print('recv error', e)
# Poll history for session_b channel
try:
    r = urllib.request.urlopen(SERVER + f"/irc/history?session={session_b}&channel=%23masterchief")
    print('\n/irc/history for session_b:')
    print(r.read().decode())
except Exception as e:
    print('history error', e)
