import urllib.request, json, sys, time


def post_json(url, data, timeout=10):
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)

try:
    data = {"host":"127.0.0.1","port":6667,"nick":"reprobot"}
    j = post_json('http://127.0.0.1:8080/irc/connect', data, timeout=10)
    print('CONNECT_RESPONSE:', json.dumps(j))
    sid = j.get('session')
    if not sid:
        print('No session in response, aborting')
        sys.exit(1)
    print('SID:', sid)
except Exception as e:
    print('CONNECT_ERROR:', repr(e))
    sys.exit(1)

# give the connection a moment to register and join
time.sleep(1)

try:
    data = {'session': sid, 'channel': '#masterchief', 'message': 'hello from repro'}
    r = post_json('http://127.0.0.1:8080/irc/msg', data, timeout=10)
    print('MSG_RESPONSE:', json.dumps(r))
except Exception as e:
    print('MSG_ERROR:', repr(e))

# poll recv once
try:
    url = f'http://127.0.0.1:8080/irc/recv?session={sid}&last=0'
    with urllib.request.urlopen(url, timeout=5) as r:
        rr = json.load(r)
    print('RECV:', json.dumps(rr))
except Exception as e:
    print('RECV_ERROR', repr(e))
