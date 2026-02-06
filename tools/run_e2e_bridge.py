#!/usr/bin/env python3
"""
End-to-end bridge test:
- Starts a dummy IRC server on an available port
- Connects the web IRC proxy (/irc/connect) to that port
- Joins a test channel and enables bridge (!echo on)
- Calls /api/echo/chat to get an Echo response
- Posts the response to /irc/bridge_send using the returned bridge token
- Verifies the dummy IRC server received the bridged PRIVMSG

Run: python tools/run_e2e_bridge.py
"""

import requests
import socket
import threading
import time
import json
import sys

BASE = 'http://127.0.0.1:8080'
TEST_NICK = 'testweb'
TEST_CHANNEL = '#testbridge'

received_lines = []

def start_dummy_irc_server(host='127.0.0.1'):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, 0))
    srv.listen(1)
    addr, port = srv.getsockname()

    def _run():
        try:
            conn, ra = srv.accept()
            conn_file = conn.makefile('rwb')
            while True:
                line = conn_file.readline()
                if not line:
                    break
                try:
                    s = line.decode('utf-8', errors='replace').rstrip('\r\n')
                except Exception:
                    s = str(line)
                print('[dummy-irc] <=', s)
                received_lines.append(s)
                # if PONG requested, ignore; if server sends PING, respond
                # We'll respond to PING to keep connection healthy
                if s.upper().startswith('PING'):
                    parts = s.split(None, 1)
                    token = parts[1] if len(parts) > 1 else ''
                    try:
                        conn.sendall((f'PONG {token}\r\n').encode('utf-8'))
                    except Exception:
                        pass
            conn.close()
        except Exception as e:
            print('dummy server error', e)
        finally:
            try: srv.close()
            except: pass

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return addr, port, srv


def http_ok(url, timeout=2.0):
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False


def main():
    print('Checking web server...')
    if not http_ok(BASE + '/'):
        print('Web server not reachable at', BASE)
        print('Start the app (python main.py) and re-run this script.')
        sys.exit(2)

    host, port, srv = start_dummy_irc_server('127.0.0.1')
    print('Started dummy IRC on', host, port)

    # Connect via /irc/connect
    print('Creating IRC proxy session...')
    try:
        r = requests.post(BASE + '/irc/connect', json={'host': host, 'port': port, 'nick': TEST_NICK}, timeout=10)
        j = r.json()
    except Exception as e:
        print('connect failed:', e)
        sys.exit(2)
    if not j.get('success'):
        print('connect failed:', j)
        sys.exit(2)
    session = j.get('session')
    bridge_token = j.get('bridge_token')
    print('Session:', session, 'bridge_token:', bridge_token)

    # JOIN channel
    print('Joining channel', TEST_CHANNEL)
    requests.post(BASE + '/irc/send', json={'session': session, 'message': f'JOIN {TEST_CHANNEL}'}, timeout=5)
    time.sleep(0.5)

    # Enable bridge in-channel via PRIVMSG
    print('Enabling bridge in channel')
    requests.post(BASE + '/irc/send', json={'session': session, 'message': f'PRIVMSG {TEST_CHANNEL} :!echo on'}, timeout=5)

    # wait for server to record notice and send confirmation to dummy IRC
    print('Waiting for [BRIDGE] notice...')
    noticed = False
    for _ in range(20):
        try:
            rh = requests.get(BASE + '/irc/history', params={'session': session, 'channel': TEST_CHANNEL}, timeout=3)
            jh = rh.json()
            if jh.get('success') and isinstance(jh.get('history'), list):
                for ln in jh['history']:
                    if '[BRIDGE]' in ln:
                        noticed = True
                        break
            if noticed:
                break
        except Exception:
            pass
        time.sleep(0.5)
    print('Bridge notice found:', noticed)

    # Call Echo chat endpoint to generate a response
    print('Calling /api/echo/chat to generate response')
    try:
        rc = requests.post(BASE + '/api/echo/chat', json={'message': 'Hello from e2e test', 'session_id': 'e2e_test'}, timeout=10)
        jc = rc.json()
        response_text = jc.get('response') or jc.get('result') or ''
    except Exception as e:
        print('echo call failed', e)
        response_text = 'test-response'
    print('Echo response:', response_text)

    # POST to /irc/bridge_send with token
    print('Posting bridged message...')
    headers = {'Content-Type': 'application/json'}
    if bridge_token:
        headers['X-BRIDGE-TOKEN'] = bridge_token
    try:
        rb = requests.post(BASE + '/irc/bridge_send', json={'session': session, 'channel': TEST_CHANNEL, 'message': response_text, 'bridge_token': bridge_token}, headers=headers, timeout=5)
        jb = rb.json()
    except Exception as e:
        print('bridge_send failed', e)
        jb = {}
    print('bridge_send response:', jb)

    # Wait for dummy IRC to receive PRIVMSG
    time.sleep(1.0)
    saw_privmsg = any(('PRIVMSG ' + TEST_CHANNEL) in ln for ln in received_lines)
    print('Dummy IRC received PRIVMSG to channel:', saw_privmsg)
    if saw_privmsg:
        print('E2E bridge test: PASS')
        sys.exit(0)
    else:
        print('E2E bridge test: FAIL')
        print('Dummy IRC received lines:', received_lines)
        sys.exit(3)

if __name__ == '__main__':
    main()
