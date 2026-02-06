#!/usr/bin/env python3
"""Simple local IRC server for development/testing.
Supports NICK/USER, JOIN, PART, PRIVMSG, NOTICE, PING/PONG, QUIT.
Not a production server — intended to replace a Docker InspIRCd for local dev.
"""
import socket
import os
import threading
import traceback

HOST = '0.0.0.0'
PORT = int(os.environ.get('LOCAL_IRC_PORT', '6667'))
SERVER_NAME = 'local-inspircd'

clients_lock = threading.Lock()
clients = set()
channels = {}  # channel -> set of handlers

class ClientHandler(threading.Thread):
    def __init__(self, conn, addr):
        super().__init__(daemon=True)
        self.conn = conn
        self.addr = addr
        self.nick = None
        self.user = None
        self.realname = None
        self.registered = False
        self.alive = True
        self.lock = threading.Lock()

    def send_line(self, line: str):
        try:
            data = (line + '\r\n').encode('utf-8')
            with self.lock:
                self.conn.sendall(data)
        except Exception:
            self.alive = False

    def broadcast_to_channel(self, channel, message_line):
        members = channels.get(channel, set()).copy()
        for m in members:
            if m is not self:
                m.send_line(message_line)

    def handle_line(self, line: str):
        parts = line.split()
        if not parts:
            return
        cmd = parts[0].upper()
        if cmd == 'PING':
            token = parts[1] if len(parts) > 1 else SERVER_NAME
            self.send_line(f'PONG {token}')
            return
        if cmd == 'NICK':
            self.nick = parts[1] if len(parts) > 1 else self.nick
            if self.nick and self.user and not self.registered:
                self.register()
            return
        if cmd == 'USER':
            if len(parts) >= 5:
                self.user = parts[1]
                self.realname = ' '.join(parts[4:]).lstrip(':')
            else:
                self.user = parts[1] if len(parts) > 1 else self.user
            if self.nick and self.user and not self.registered:
                self.register()
            return
        if cmd == 'JOIN':
            chan = parts[1] if len(parts) > 1 else None
            if not chan:
                return
            if chan.startswith(':'):
                chan = chan[1:]
            with clients_lock:
                channels.setdefault(chan, set()).add(self)
            # notify join to members
            join_line = f':{self.nick}!{self.user}@{self.addr[0]} JOIN {chan}'
            self.broadcast_to_channel(chan, join_line)
            # send simple RPL_TOPIC to joiner
            self.send_line(f':{SERVER_NAME} 332 {self.nick} {chan} :')
            return
        if cmd == 'PART':
            chan = parts[1] if len(parts) > 1 else None
            if chan and chan.startswith(':'):
                chan = chan[1:]
            if chan:
                with clients_lock:
                    channels.get(chan, set()).discard(self)
                part_line = f':{self.nick}!{self.user}@{self.addr[0]} PART {chan}'
                self.broadcast_to_channel(chan, part_line)
            return
        if cmd == 'PRIVMSG' or cmd == 'NOTICE':
            if len(parts) < 3:
                return
            target = parts[1]
            # message may include leading ':'
            msg = ' '.join(parts[2:])
            if msg.startswith(':'):
                msg = msg[1:]
            line_out = f':{self.nick}!{self.user}@{self.addr[0]} {cmd} {target} :{msg}'
            if target.startswith('#'):
                # channel broadcast
                self.broadcast_to_channel(target, line_out)
            else:
                # private message - find recipient
                with clients_lock:
                    for c in clients:
                        if c.nick == target:
                            c.send_line(line_out)
                            break
            return
        if cmd == 'QUIT':
            self.alive = False
            return
        # unknown: just ignore or echo

    def register(self):
        self.registered = True
        self.send_line(f':{SERVER_NAME} 001 {self.nick} :Welcome to {SERVER_NAME}, {self.nick}')

    def run(self):
        try:
            buf = b''
            while self.alive:
                data = self.conn.recv(4096)
                if not data:
                    break
                buf += data
                while b'\n' in buf:
                    line, buf = buf.split(b'\n', 1)
                    try:
                        line = line.decode('utf-8', errors='ignore').strip('\r')
                    except Exception:
                        continue
                    if not line:
                        continue
                    try:
                        self.handle_line(line)
                    except Exception:
                        traceback.print_exc()
                        continue
        except Exception:
            pass
        finally:
            # cleanup
            with clients_lock:
                clients.discard(self)
                for ch in list(channels.keys()):
                    channels[ch].discard(self)
                    if not channels[ch]:
                        del channels[ch]
            try:
                self.conn.close()
            except Exception:
                pass


def serve_forever():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(50)
    print(f'Local IRC server listening on {HOST}:{PORT}')
    try:
        while True:
            conn, addr = sock.accept()
            handler = ClientHandler(conn, addr)
            with clients_lock:
                clients.add(handler)
            handler.start()
    except KeyboardInterrupt:
        print('Shutting down')
    finally:
        sock.close()

if __name__ == '__main__':
    serve_forever()
