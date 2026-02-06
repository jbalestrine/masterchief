#!/usr/bin/env python3
import socket, time
s=socket.create_connection(('127.0.0.1',6667), timeout=5)
f=s.makefile('rw', encoding='utf-8', newline='\r\n')
# send NICK/USER
f.write('NICK testclient\r\n')
f.write('USER testclient 0 * :testclient\r\n')
f.flush()
# read initial numerics
for _ in range(5):
    line=f.readline()
    if not line:
        break
    print('RECV:', line.rstrip('\r\n'))
# send PRIVMSG
f.write('PRIVMSG #masterchief :hello from direct client\r\n')
f.flush()
# read echo
for _ in range(3):
    line=f.readline()
    if not line:
        break
    print('ECHO:', line.rstrip('\r\n'))
s.close()
