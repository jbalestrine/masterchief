import socket
import time
import sys

HOST = '127.0.0.1'
PORT = 6667
NICK = 'simplecli'
USER = 'simplecli 0 * :simple client'
CHANNEL = '#masterchief'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)

try:
    print(f'Connecting to {HOST}:{PORT}...')
    s.connect((HOST, PORT))
    s.settimeout(None)
    def send(line):
        print('> ' + line)
        s.sendall((line + '\r\n').encode('utf-8'))

    send(f'NICK {NICK}')
    send(f'USER {USER}')

    # read until we see MOTD end or numeric 001
    start = time.time()
    joined = False
    # Give server up to 15s to register
    while time.time() - start < 15:
        data = s.recv(4096)
        if not data:
            print('Connection closed by server during registration')
            raise SystemExit(1)
        for line in data.decode('utf-8', errors='ignore').split('\r\n'):
            if not line: continue
            print('< ' + line)
            if line.startswith('PING'):
                token = line.split(' ',1)[1]
                send('PONG ' + token)
            # join after 001 welcome numeric
            if ' 001 ' in line and not joined:
                send('JOIN ' + CHANNEL)
                time.sleep(1)
                send('PRIVMSG ' + CHANNEL + ' :hello from simple IRC client')
                joined = True
                break

    # main loop: respond to PING and print messages for 60s
    print('Entering listen loop (60s)')
    end = time.time() + 60
    s.settimeout(2)
    while time.time() < end:
        try:
            data = s.recv(4096)
            if not data:
                print('EOF from server, socket closed')
                break
            for line in data.decode('utf-8', errors='ignore').split('\r\n'):
                if not line: continue
                print('< ' + line)
                if line.startswith('PING'):
                    token = line.split(' ',1)[1]
                    send('PONG ' + token)
        except socket.timeout:
            # keep-alive: send a CTCP or noop? we just continue
            continue
        except Exception as e:
            print('Error in recv loop:', e)
            break

    print('Done — closing socket')
    try:
        s.close()
    except:
        pass
except Exception as exc:
    print('Connection failed:', exc)
    try:
        s.close()
    except:
        pass
    sys.exit(1)
