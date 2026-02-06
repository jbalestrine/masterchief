import socket
try:
    s=socket.create_connection(('127.0.0.1',8081),2)
    print('open')
    s.close()
except Exception as e:
    print('closed',e)
