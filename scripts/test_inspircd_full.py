import socket
import time

HOST='127.0.0.1'
PORT=6667

def recv_all(sock, timeout=1.0):
    sock.settimeout(timeout)
    out=''
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                break
            out += data.decode('utf-8', errors='ignore')
            if len(data)<4096:
                break
    except Exception:
        pass
    return out

print('Connecting to', HOST, PORT)
try:
    s = socket.create_connection((HOST, PORT), timeout=5)
    print('Connected')
    print('Initial:', recv_all(s, 0.5))
    s.sendall(b'NICK testbot123\r\n')
    s.sendall(b'USER testbot 0 * :testbot\r\n')
    time.sleep(0.5)
    print('After register:', recv_all(s, 0.5))
    # try to join and send a message
    s.sendall(b'JOIN #testchannel\r\n')
    time.sleep(0.3)
    print('After JOIN:', recv_all(s, 0.5))
    s.sendall(b'PRIVMSG #testchannel :Hello from testbot\r\n')
    time.sleep(0.3)
    print('After PRIVMSG:', recv_all(s, 0.5))
    s.sendall(b'QUIT :bye\r\n')
    time.sleep(0.2)
    print('Final:', recv_all(s, 0.5))
    s.close()
except Exception as e:
    print('ERROR:', e)
