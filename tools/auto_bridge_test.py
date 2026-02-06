#!/usr/bin/env python3
import subprocess, sys, time, socket, requests, json, os

BASE='http://127.0.0.1:8080'
PY=sys.executable
server_script=os.path.join(os.path.dirname(__file__), 'real_irc_server.py')

print('Starting local IRC server...')
logpath = os.path.join(os.path.dirname(__file__), 'real_irc_server.log')
logf = open(logpath, 'a', encoding='utf-8')
proc = subprocess.Popen([PY, '-u', server_script], stdout=logf, stderr=logf)
print('IRC server pid=', proc.pid)

# wait until port 6667 is accepting
timeout=15
start=time.time()
listening=False
while time.time()-start < timeout:
    try:
        s=socket.create_connection(('127.0.0.1',6667),timeout=1)
        s.close()
        listening=True
        break
    except Exception:
        time.sleep(0.5)

if not listening:
    print('IRC server did not start listening within', timeout, 'seconds')
    print('stdout/stderr:')
    try:
        out,err = proc.communicate(timeout=1)
        print(out.decode(errors='ignore'))
        print(err.decode(errors='ignore'))
    except Exception:
        pass
    sys.exit(2)

print('IRC server is listening on 6667')

# run the bridge test (retry a few times)
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

print('\nLeaving IRC server running (pid='+str(proc.pid)+').')
print('If you want to stop it: kill PID or find process and terminate.')
print('Server log file:', logpath)
