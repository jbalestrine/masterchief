#!/usr/bin/env python3
"""Simple mock IRC server for local testing.
Listens on 0.0.0.0:6667 and responds to NICK/USER with basic registration numerics
and echoes PRIVMSG lines back to client. Useful for testing `main.py` IRC flows.
"""
import socket
import threading
import time

HOST = '0.0.0.0'
PORT = 6667

WELCOME_TEMPLATE = ":mock.local 001 {nick} :Welcome to Mock IRC\r\n"
MOTD_START = ":mock.local 375 {nick} :- \r\n"
MOTD_BODY = ":mock.local 372 {nick} :- This is a mock IRC server.\r\n"
MOTD_END = ":mock.local 376 {nick} :End of /MOTD command.\r\n"


def handle_client(conn, addr):
    try:
        f = conn.makefile('rw', encoding='utf-8', newline='\r\n')
        nick = 'guest'
        user = None
        registered = False
        while True:
            line = f.readline()
            if not line:
                break
            line = line.rstrip('\r\n')
            print(f"[mock] RECV: {line}")
            parts = line.split()
            if not parts:
                continue
            cmd = parts[0].upper()
            if cmd == 'NICK':
                if len(parts) > 1:
                    nick = parts[1]
                else:
                    nick = 'guest'
            elif cmd == 'USER':
                user = parts[1] if len(parts) > 1 else 'user'
            elif cmd == 'PING':
                token = parts[1] if len(parts) > 1 else ''
                f.write(f"PONG {token}\r\n")
                f.flush()
                continue
            # When we have both nick and user, send registration numerics
            if not registered and nick and user is not None:
                registered = True
                f.write(WELCOME_TEMPLATE.format(nick=nick))
                f.write(MOTD_START.format(nick=nick))
                f.write(MOTD_BODY.format(nick=nick))
                f.write(MOTD_END.format(nick=nick))
                f.flush()
                continue
            # If PRIVMSG, echo back as if from nick
            if cmd == 'PRIVMSG':
                # format: PRIVMSG <target> :message
                if len(parts) >= 3:
                    target = parts[1]
                    # rest after first ':'
                    idx = line.find(':')
                    msg = line[idx+1:] if idx != -1 else ''
                    # echo as coming from mockuser
                    f.write(f":mockuser!mock@local PRIVMSG {target} :{msg}\r\n")
                    f.flush()
    except Exception as e:
        print('[mock] client handler error:', e)
    finally:
        try:
            conn.close()
        except Exception:
            pass


def run_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"Mock IRC server listening on {HOST}:{PORT}")
    try:
        while True:
            conn, addr = sock.accept()
            print(f"[mock] connection from {addr}")
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print('Shutting down mock server')
    finally:
        sock.close()


if __name__ == '__main__':
    run_server()
