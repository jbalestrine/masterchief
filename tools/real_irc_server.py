#!/usr/bin/env python3
"""Minimal multi-client IRC server for local testing.

Features:
- Accepts connections on 0.0.0.0:6667
- Handles NICK, USER, JOIN, PART, PRIVMSG, PING, QUIT
- Sends basic numerics: 001 (welcome), MOTD (375/372/376), 353 (NAMES), 366
- Broadcasts PRIVMSG to channel members
- Thread-per-client model, suitable for local development/testing only
"""
import socket
import threading
import time
import re

HOST = '0.0.0.0'
PORT = 6667

clients_lock = threading.Lock()
clients = {}  # sock -> client dict
channels = {}  # channel -> set of client dicts

MOTD_LINES = ["Welcome to Minimal IRC Server","This server is for local testing only."]


def send_line(f, line):
    try:
        f.write(line + '\r\n')
        f.flush()
    except Exception:
        pass


def broadcast_channel(channel, from_client, text):
    with clients_lock:
        members = list(channels.get(channel, []))
    prefix = f":{from_client['nick']}!{from_client.get('user','user')}@{from_client['addr'][0]}"
    for c in members:
        if c is from_client:
            continue
        try:
            send_line(c['file'], f"{prefix} PRIVMSG {channel} :{text}")
        except Exception:
            pass


def handle_client(conn, addr):
    f = conn.makefile('rw', encoding='utf-8', newline='\r\n')
    client = {'sock': conn, 'file': f, 'nick': None, 'user': None, 'host': addr[0], 'addr': addr, 'channels': set()}
    with clients_lock:
        clients[conn] = client
    try:
        while True:
            line = f.readline()
            if not line:
                break
            line = line.rstrip('\r\n')
            if not line:
                continue
            parts = line.split()
            cmd = parts[0].upper()
            if cmd == 'NICK':
                if len(parts) > 1:
                    client['nick'] = parts[1]
                # send welcome if USER already provided
                if client['nick'] and client['user']:
                    send_welcome(client)
            elif cmd == 'USER':
                # format: USER <user> <mode> <unused> :<realname>
                if len(parts) > 1:
                    client['user'] = parts[1]
                if client['nick'] and client['user']:
                    send_welcome(client)
            elif cmd == 'PING':
                token = parts[1] if len(parts) > 1 else ''
                send_line(f, f'PONG {token}')
            elif cmd == 'JOIN':
                if len(parts) > 1:
                    chan = parts[1]
                    join_channel(client, chan)
            elif cmd == 'PART':
                if len(parts) > 1:
                    chan = parts[1]
                    part_channel(client, chan)
            elif cmd == 'PRIVMSG':
                if len(parts) >= 3:
                    target = parts[1]
                    idx = line.find(':')
                    msg = line[idx+1:] if idx != -1 else ''
                    if target.startswith('#'):
                        # deliver to channel
                        broadcast_channel(target, client, msg)
                    else:
                        # user-to-user (simple linear scan)
                        deliver_to_user(target, client, msg)
            elif cmd == 'QUIT':
                break
            else:
                # ignore other commands for now
                pass
    except Exception as e:
        # connection error
        pass
    finally:
        # cleanup
        try:
            with clients_lock:
                clients.pop(conn, None)
            for ch in list(client['channels']):
                try:
                    with clients_lock:
                        channels.get(ch, set()).discard(client)
                except Exception:
                    pass
            try:
                f.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass
        except Exception:
            pass


def send_welcome(client):
    f = client['file']
    nick = client['nick'] or 'guest'
    send_line(f, f":minimal 001 {nick} :Welcome to Minimal IRC Server")
    # MOTD
    send_line(f, f":minimal 375 {nick} :- \"\"-\" MOTD \"\"")
    for l in MOTD_LINES:
        send_line(f, f":minimal 372 {nick} :- {l}")
    send_line(f, f":minimal 376 {nick} :End of /MOTD command.")


def join_channel(client, channel):
    with clients_lock:
        channels.setdefault(channel, set()).add(client)
        client['channels'].add(channel)
        # send NAMES list
        nicks = [c['nick'] or 'guest' for c in channels.get(channel, [])]
    # 353 names
    send_line(client['file'], f":minimal 353 {client['nick']} = {channel} :{' '.join(nicks)}")
    send_line(client['file'], f":minimal 366 {client['nick']} {channel} :End of /NAMES list.")
    # announce JOIN to others
    prefix = f":{client['nick']}!{client.get('user','user')}@{client['addr'][0]}"
    with clients_lock:
        for c in channels.get(channel, []):
            if c is client:
                continue
            send_line(c['file'], f"{prefix} JOIN {channel}")


def part_channel(client, channel):
    with clients_lock:
        if channel in client['channels']:
            client['channels'].discard(channel)
            channels.get(channel, set()).discard(client)
            prefix = f":{client['nick']}!{client.get('user','user')}@{client['addr'][0]}"
            # announce PART
            for c in channels.get(channel, []):
                send_line(c['file'], f"{prefix} PART {channel}")


def deliver_to_user(target, from_client, msg):
    with clients_lock:
        for c in clients.values():
            if c is from_client:
                continue
            if c.get('nick') == target:
                send_line(c['file'], f":{from_client['nick']}!{from_client.get('user','user')}@{from_client['addr'][0]} PRIVMSG {target} :{msg}")


def run_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(100)
    print(f"Real IRC server listening on {HOST}:{PORT}")
    try:
        while True:
            conn, addr = sock.accept()
            print(f"connection from {addr}")
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print('Shutting down')
    finally:
        sock.close()


if __name__ == '__main__':
    run_server()
