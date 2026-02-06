import socket
import time

HOST = '127.0.0.1'
PORT = 6668

try:
    s = socket.create_connection((HOST, PORT), timeout=5)
    s.settimeout(2)
    def send(line):
        s.sendall((line + "\r\n").encode('utf-8'))
    send('NICK testbot')
    send('USER testbot 0 * :Test Bot')
    time.sleep(0.5)
    send('JOIN #masterchief')
    send('PRIVMSG #masterchief :hello from testbot')
    time.sleep(0.5)
    try:
        data = s.recv(8192)
        print(data.decode('utf-8', errors='replace'))
    except socket.timeout:
        print('<no response received within timeout>')
    s.close()
except Exception as e:
    print('ERROR:', e)
