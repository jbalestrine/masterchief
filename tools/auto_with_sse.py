#!/usr/bin/env python3
import subprocess, sys, time, socket, requests, json, os, threading

BASE='http://127.0.0.1:8080'
PY=sys.executable
server_script=os.path.join(os.path.dirname(__file__), 'real_irc_server.py')

# start IRC server
proc = subprocess.Popen([PY, server_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print('IRC server pid=', proc.pid)

# wait for listening
start=time.time()
while time.time()-start < 15:
    try:
        s=socket.create_connection(('127.0.0.1',6667),timeout=1)
        s.close(); break
    except Exception:
        time.sleep(0.5)

# create session
resp = requests.post(BASE + '/irc/connect', json={'host':'127.0.0.1','port':6667,'nick':'sse_tester'})
print('connect', resp.status_code, resp.text)
j = resp.json()
session = j.get('session')
token = j.get('bridge_token')
print('session', session, 'token', token)

# sse reader
stop_flag = False

def sse_reader():
    url = BASE + '/irc/stream?session=' + session + '&last=0'
    print('Opening SSE', url)
    try:
        r = requests.get(url, stream=True, timeout=10)
        buf = ''
        for chunk in r.iter_content(chunk_size=1):
            if stop_flag: break
            if not chunk: continue
            ch = chunk.decode(errors='ignore')
            buf += ch
            if buf.endswith('\n\n'):
                # parse event
                lines = buf.strip().splitlines()
                for ln in lines:
                    if ln.startswith('data:'):
                        data = ln[len('data:'):].strip()
                        try:
                            print('SSE DATA:', json.loads(data))
                        except Exception:
                            print('SSE RAW:', data)
                buf = ''
    except Exception as e:
        print('SSE reader error', e)

th = threading.Thread(target=sse_reader, daemon=True)
th.start()

# give sse a moment
time.sleep(0.8)
# send bridge message
msg = 'Hello SSE test at ' + time.strftime('%Y-%m-%d %H:%M:%S')
body = {'session': session, 'channel': '#masterchief', 'message': msg}
headers = {'Content-Type':'application/json'}
if token:
    headers['X-BRIDGE-TOKEN']=token; body['bridge_token']=token
r2 = requests.post(BASE + '/irc/bridge_send', json=body, headers=headers)
print('bridge_send', r2.status_code, r2.text)

# wait for events
time.sleep(2)
stop_flag = True
th.join(timeout=1)
print('Done. Leaving IRC server running (pid=%d)'%proc.pid)
