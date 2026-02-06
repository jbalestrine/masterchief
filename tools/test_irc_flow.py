import urllib.request, json, sys, time


def post_json(url, data, timeout=10):
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)

try:
    data = {"host":"127.0.0.1","port":6667,"nick":"testbot"}
    j = post_json('http://127.0.0.1:8080/irc/connect', data, timeout=10)
    print('CONNECT_RESPONSE:', json.dumps(j))
    sid = j.get('session')
    if not sid:
        print('No session in response, aborting')
        sys.exit(0)
    print('SID:', sid)
except Exception as e:
    print('CONNECT_ERROR:', repr(e))
    sys.exit(0)

for i in range(3):
    try:
        url = f'http://127.0.0.1:8080/irc/recv?session={sid}&last=0'
        with urllib.request.urlopen(url, timeout=5) as r:
            rr = json.load(r)
        print('RECV', i, json.dumps(rr))
    except Exception as e:
        print('RECV_ERROR', i, repr(e))
    time.sleep(1)

# close
try:
    cr = post_json('http://127.0.0.1:8080/irc/close', {'session': sid}, timeout=5)
    print('CLOSE_RESPONSE:', json.dumps(cr))
except Exception as e:
    print('CLOSE_ERROR:', repr(e))

# final recv
try:
    url = f'http://127.0.0.1:8080/irc/recv?session={sid}&last=0'
    with urllib.request.urlopen(url, timeout=5) as r:
        fr = json.load(r)
    print('FINAL_RECV:', json.dumps(fr))
except Exception as e:
    print('FINAL_RECV_ERROR:', repr(e))
