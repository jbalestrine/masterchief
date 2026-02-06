import requests, time, sys
base='http://127.0.0.1:8080'
try:
    r = requests.post(base + '/irc/connect', json={'host':'127.0.0.1','port':6667,'nick':'web-tail'}, timeout=5)
    j = r.json()
    sid = j.get('session')
    token = j.get('bridge_token')
    print('Session:', sid)
    print('Bridge token:', token)
except Exception as e:
    print('Failed to create session:', e)
    sys.exit(1)
last = 0
print('Starting recv poller (ctrl-C to exit)')
while True:
    try:
        r = requests.get(base + f'/irc/recv?session={sid}&last={last}', timeout=10)
        j = r.json()
        msgs = j.get('messages', [])
        total = j.get('total', 0)
        if msgs:
            for m in msgs:
                print(time.strftime('%Y-%m-%d %H:%M:%S'), m)
            last = total
        time.sleep(1)
    except KeyboardInterrupt:
        print('Exiting')
        break
    except Exception as e:
        print('Poll error:', e)
        time.sleep(1)
