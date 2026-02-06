import socket, time, threading, requests

IRC_HOST='127.0.0.1'
IRC_PORT=6667
BASE='http://127.0.0.1:8080'

recv_buf = []

def client_listener():
    s = socket.socket()
    s.connect((IRC_HOST, IRC_PORT))
    s.settimeout(1.0)
    s.sendall(b'NICK realclient2\r\n')
    s.sendall(b'USER realclient2 0 * :realclient2\r\n')
    # wait for welcome
    start=time.time()
    got_welcome=False
    while time.time()-start < 10:
        try:
            d = s.recv(4096)
        except Exception:
            d=b''
        if d:
            txt = d.decode(errors='replace')
            print('CLIENT RECV:', txt)
            if ' 001 ' in txt:
                got_welcome=True
                break
    if not got_welcome:
        print('No welcome; exiting')
        s.close(); return
    s.sendall(b'JOIN #masterchief\r\n')
    print('CLIENT: joined #masterchief, listening for 8s')
    end=time.time()+8
    while time.time() < end:
        try:
            d = s.recv(4096)
        except Exception:
            time.sleep(0.1); continue
        if not d:
            time.sleep(0.1); continue
        txt = d.decode(errors='replace')
        print('CLIENT LINE:', txt.strip())
    s.close()

# run client in thread
th = threading.Thread(target=client_listener, daemon=True)
th.start()
# give it a moment
time.sleep(1.2)
# create bridge session and send message
try:
    r = requests.post(BASE + '/irc/connect', json={'host':IRC_HOST,'port':IRC_PORT,'nick':'bridgeposter2'}, timeout=5)
    print('CONNECT:', r.status_code, r.text)
    j=r.json(); session=j.get('session'); token=j.get('bridge_token')
    msg = 'Hello real client test at ' + time.strftime('%Y-%m-%d %H:%M:%S')
    body={'session':session,'channel':'#masterchief','message':msg}
    headers={'Content-Type':'application/json'}
    if token:
        headers['X-BRIDGE-TOKEN']=token; body['bridge_token']=token
    r2 = requests.post(BASE + '/irc/bridge_send', json=body, headers=headers, timeout=5)
    print('BRIDGE_SEND:', r2.status_code, r2.text)
except Exception as e:
    print('bridge error', e)
# wait for client thread
th.join(timeout=10)
print('done')
