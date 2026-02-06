import socket
import ssl
import time


def try_plain():
    print('== Plain TCP 6667 ==')
    try:
        s = socket.create_connection(('127.0.0.1', 6667), timeout=5)
        s.settimeout(3)
        data = s.recv(4096).decode('utf-8', errors='ignore')
        print('RECV:', data)
        s.sendall(b'NICK pytestuser\r\n')
        s.sendall(b'USER pytest 0 * :pytest\r\n')
        time.sleep(0.5)
        try:
            more = s.recv(4096).decode('utf-8', errors='ignore')
            print('AFTER:', more)
        except Exception as e:
            print('AFTER recv error:', e)
        s.close()
    except Exception as e:
        print('PLAIN ERROR:', e)


def try_tls():
    print('\n== TLS 6697 ==')
    try:
        s = socket.create_connection(('127.0.0.1', 6697), timeout=5)
        context = ssl.create_default_context()
        ss = context.wrap_socket(s, server_hostname='127.0.0.1')
        ss.settimeout(3)
        data = ss.recv(4096).decode('utf-8', errors='ignore')
        print('TLS RECV:', data)
        ss.sendall(b'NICK pytls\r\n')
        ss.sendall(b'USER pytls 0 * :pytls\r\n')
        time.sleep(0.5)
        try:
            more = ss.recv(4096).decode('utf-8', errors='ignore')
            print('TLS AFTER:', more)
        except Exception as e:
            print('TLS AFTER recv error:', e)
        ss.close()
    except Exception as e:
        print('TLS ERROR:', e)


if __name__ == '__main__':
    try_plain()
    try_tls()
