import socket
import threading
import time

HOST='127.0.0.1'
PORT=6667

s = socket.create_connection((HOST, PORT), timeout=5)
print('Connected to', HOST, PORT)

stop = False


def reader(sock):
    bu = b''
    try:
        while not stop:
            data = sock.recv(4096)
            if not data:
                break
            text = data.decode('utf-8', errors='ignore')
            for line in text.split('\r\n'):
                if not line:
                    continue
                print('<<<', line)
                if line.startswith('PING'):
                    token = line.split(' ',1)[1] if ' ' in line else ''
                    resp = f'PONG {token}\r\n'
                    print('>>>', resp.strip())
                    sock.sendall(resp.encode('utf-8'))
    except Exception as e:
        print('Reader exception:', e)


t = threading.Thread(target=reader, args=(s,), daemon=True)

t.start()

# Send registration
s.sendall(b'NICK testmanual\r\n')
s.sendall(b'USER testmanual 0 * :manual tester\r\n')

# wait for welcome (001) or timeout
for i in range(10):
    time.sleep(0.5)

# Try join and message
s.sendall(b'JOIN #testroom\r\n')
s.sendall(b'PRIVMSG #testroom :Hello from manual tester\r\n')

# wait a bit then quit
time.sleep(1.5)
s.sendall(b'QUIT :bye\r\n')

# allow reader to print
time.sleep(0.5)
stop = True
s.close()
print('Done')
