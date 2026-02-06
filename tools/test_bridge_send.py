import requests, time, json

BASE='http://127.0.0.1:8080'
print('base:', BASE)
try:
    r = requests.post(BASE + '/irc/connect', json={'host':'127.0.0.1','port':6667,'nick':'tester'})
    print('connect status:', r.status_code)
    print(r.text)
    j = r.json()
    session = j.get('session')
    token = j.get('bridge_token')
    print('session:', session, 'token:', token)
except Exception as e:
    print('connect failed', e)
    raise SystemExit(1)

# give server a moment
time.sleep(0.5)
msg = 'Hello from test bridge at ' + time.strftime('%Y-%m-%d %H:%M:%S')
body = {'session': session, 'channel': '#masterchief', 'message': msg}
headers = {'Content-Type':'application/json'}
if token:
    headers['X-BRIDGE-TOKEN'] = token
    body['bridge_token'] = token
try:
    r2 = requests.post(BASE + '/irc/bridge_send', json=body, headers=headers)
    print('bridge_send status:', r2.status_code)
    try:
        print(r2.json())
    except Exception:
        print(r2.text)
except Exception as e:
    print('bridge_send failed', e)
    raise SystemExit(1)

# poll recv to show message present
time.sleep(0.5)
try:
    r3 = requests.get(BASE + '/irc/recv', params={'session': session, 'last': 0})
    print('recv status:', r3.status_code)
    try:
        print(json.dumps(r3.json(), indent=2))
    except Exception:
        print(r3.text)
except Exception as e:
    print('recv failed', e)
    raise SystemExit(1)
