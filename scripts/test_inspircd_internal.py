import socket, time
HOST='172.17.0.2'
PORT=6667
print('Connecting to', HOST)
s=socket.create_connection((HOST,PORT),timeout=5)
s.settimeout(2)
print('Connected, recv:')
try:
    data=s.recv(4096).decode('utf-8',errors='ignore')
    print('RECV:',repr(data))
except Exception as e:
    print('recv err',e)
# send NICK/USER and handle PING
s.sendall(b'NICK ci_test\r\n')
s.sendall(b'USER ci_test 0 * :ci test\r\n')
for i in range(6):
    try:
        d=s.recv(4096).decode('utf-8',errors='ignore')
        if d:
            print('RECV2:',repr(d))
            if d.strip().startswith('PING'):
                tok=d.strip().split(' ',1)[1] if ' ' in d else ''
                s.sendall(f'PONG {tok}\r\n'.encode('utf-8'))
        else:
            break
    except Exception as e:
        print('recv loop err',e)
    time.sleep(0.3)
# attempt JOIN
s.sendall(b'JOIN #test\r\n')
try:
    print('After JOIN recv:', s.recv(4096).decode('utf-8',errors='ignore'))
except Exception as e:
    print('join recv err',e)
s.close()
print('Done')
