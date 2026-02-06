#!/usr/bin/env python3
import requests, json, time, sys
BASE='http://127.0.0.1:8080'

# attempt connect
for attempt in range(1,8):
    print('\nAttempt', attempt)
    try:
        r = requests.post(BASE + '/irc/connect', json={'host':'127.0.0.1','port':6667,'nick':'tester'}, timeout=5)
        print('connect status:', r.status_code)
        print('connect body:', r.text)
        j = r.json()
        session = j.get('session')
        token = j.get('bridge_token')
        print('session:', session, 'token:', token)
    except Exception as e:
        print('connect failed', e)
        session=None
        token=None

    if not session:
        print('waiting and retrying...')
        time.sleep(1)
        continue

    msg = 'Hello from auto test at ' + time.strftime('%Y-%m-%d %H:%M:%S')
    body = {'session': session, 'channel': '#masterchief', 'message': msg}
    headers = {'Content-Type':'application/json'}
    if token:
        headers['X-BRIDGE-TOKEN'] = token
        body['bridge_token'] = token
    try:
        r2 = requests.post(BASE + '/irc/bridge_send', json=body, headers=headers, timeout=5)
        print('bridge_send status:', r2.status_code)
        try:
            print('bridge_send json:', r2.json())
        except Exception:
            print('bridge_send text:', r2.text)
    except Exception as e:
        print('bridge_send failed', e)
        time.sleep(1)
        continue

    time.sleep(0.5)
    try:
        r3 = requests.get(BASE + '/irc/recv', params={'session': session, 'last': 0}, timeout=5)
        print('recv status:', r3.status_code)
        try:
            print(json.dumps(r3.json(), indent=2))
        except Exception:
            print(r3.text)
        break
    except Exception as e:
        print('recv failed', e)
        time.sleep(1)

print('\nTest finished.')
