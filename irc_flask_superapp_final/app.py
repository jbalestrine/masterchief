from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import socket
import time

# Simple in-memory notice store for UI polling
NOTICES = []
SESSIONS = {}
SESSIONS_MAX = 5

import threading


app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plugins/<path:path>')
def plugins(path):
    return send_from_directory(os.path.join(app.static_folder,'plugins'), path)


@app.route('/irc/send', methods=['POST'])
def irc_send():
    """Send raw IRC lines to the local InspIRCd (127.0.0.1:6668 by default).
    Expects JSON: {"lines": ["NICK ...","USER ...","JOIN ...", ...]}
    Returns the server reply (first 8KB) as JSON.
    """
    data = request.get_json() or {}
    lines = data.get('lines') or ([] if not data else [data.get('line')])
    host = os.environ.get('LOCAL_IRC_HOST', '127.0.0.1')
    port = int(os.environ.get('LOCAL_IRC_PORT', os.environ.get('IRC_PORT', '6667')))
    reply = ''
    try:
        with socket.create_connection((host, port), timeout=5) as s:
            s.settimeout(2.0)
            for l in lines:
                if not l.endswith('\r\n'):
                    l = l + '\r\n'
                s.sendall(l.encode('utf-8'))
                time.sleep(0.05)
            try:
                data = s.recv(8192)
                reply = data.decode('utf-8', errors='replace')
            except socket.timeout:
                reply = ''
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})
    # store notices for UI polling
    if reply:
        for line in reply.splitlines():
            NOTICES.append(line)
            if len(NOTICES) > 200:
                NOTICES.pop(0)
    return jsonify({'ok': True, 'reply': reply})


@app.route('/irc/notices', methods=['POST', 'GET'])
def irc_notices():
    return jsonify({'lines': NOTICES[-50:]})


@app.route('/irc/send_registered', methods=['POST'])
def irc_send_registered():
    """Send IRC lines but perform full registration: respond to PINGs and
    wait for numeric 001 (RPL_WELCOME) before issuing channel commands.
    Payload: {"nick":"botnick","user":"userdesc","lines": ["JOIN ...","PRIVMSG ..."]}
    """
    data = request.get_json() or {}
    nick = data.get('nick', 'webui_bot')
    user = data.get('user', f'{nick} 0 * :Web UI Bot')
    lines = data.get('lines', [])
    host = os.environ.get('LOCAL_IRC_HOST', '127.0.0.1')
    port = int(os.environ.get('LOCAL_IRC_PORT', os.environ.get('IRC_PORT', '6667')))
    reply_accum = []
    try:
        with socket.create_connection((host, port), timeout=5) as s:
            s.settimeout(1.0)
            def send(l):
                if not l.endswith('\r\n'):
                    l = l + '\r\n'
                s.sendall(l.encode('utf-8'))
            # send registration
            send(f'NICK {nick}')
            send(f'USER {user}')
            # wait for welcome (001) or timeout, respond to PINGs
            start = time.time()
            registered = False
            buf = ''
            while time.time() - start < 10:
                try:
                    data_in = s.recv(4096)
                    if not data_in:
                        break
                    chunk = data_in.decode('utf-8', errors='replace')
                    buf += chunk
                    reply_accum.append(chunk)
                    # handle PING lines
                    for line in chunk.splitlines():
                        if line.startswith('PING'):
                            # PING :token or PING token
                            token = line.split(' ',1)[1].lstrip(':')
                            send(f'PONG :{token}')
                        if ' 001 ' in line:
                            registered = True
                            break
                    if registered:
                        break
                except socket.timeout:
                    continue
            # if registered, send remaining lines
            if registered:
                for l in lines:
                    send(l)
                # collect responses briefly
                time.sleep(0.2)
                try:
                    while True:
                        data_in = s.recv(8192)
                        if not data_in:
                            break
                        chunk = data_in.decode('utf-8', errors='replace')
                        reply_accum.append(chunk)
                except socket.timeout:
                    pass
            else:
                # not registered; return what we saw
                pass
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})

    reply = ''.join(reply_accum)
    if reply:
        for line in reply.splitlines():
            NOTICES.append(line)
            if len(NOTICES) > 200:
                NOTICES.pop(0)
    return jsonify({'ok': True, 'reply': reply, 'registered': registered})


def _session_worker(nick, user, channels, stop_event):
    host = os.environ.get('LOCAL_IRC_HOST', '127.0.0.1')
    port = int(os.environ.get('LOCAL_IRC_PORT', os.environ.get('IRC_PORT', '6667')))
    backoff = 2
    while not stop_event.is_set():
        try:
            with socket.create_connection((host, port), timeout=5) as s:
                s.settimeout(1.0)
                def send(l):
                    if not l.endswith('\r\n'):
                        l = l + '\r\n'
                    try:
                        s.sendall(l.encode('utf-8'))
                    except Exception:
                        pass
                send(f'NICK {nick}')
                send(f'USER {user}')
                # wait for 001
                buf = ''
                start = time.time()
                registered = False
                while time.time() - start < 10 and not stop_event.is_set():
                    try:
                        data_in = s.recv(4096)
                        if not data_in:
                            break
                        chunk = data_in.decode('utf-8', errors='replace')
                        buf += chunk
                        for line in chunk.splitlines():
                            if line.startswith('PING'):
                                token = line.split(' ',1)[1].lstrip(':')
                                send(f'PONG :{token}')
                            NOTICES.append(line)
                            if len(NOTICES) > 500:
                                NOTICES.pop(0)
                            if ' 001 ' in line:
                                registered = True
                                break
                        if registered:
                            break
                    except socket.timeout:
                        continue
                if registered:
                    # reset backoff on success
                    backoff = 2
                    # join channels
                    for c in channels:
                        send(f'JOIN {c}')
                    # small read loop
                    while not stop_event.is_set():
                        try:
                            data_in = s.recv(4096)
                            if not data_in:
                                break
                            chunk = data_in.decode('utf-8', errors='replace')
                            for line in chunk.splitlines():
                                if line.startswith('PING'):
                                    token = line.split(' ',1)[1].lstrip(':')
                                    send(f'PONG :{token}')
                                NOTICES.append(line)
                                if len(NOTICES) > 500:
                                    NOTICES.pop(0)
                        except socket.timeout:
                            continue
                else:
                    # failed to register; increase backoff
                    NOTICES.append(f"[session-{nick}] registration failed, backing off {backoff}s")
                    if len(NOTICES) > 500:
                        NOTICES.pop(0)
        except Exception as e:
            NOTICES.append(f"[session-{nick}] error: {e}")
            if len(NOTICES) > 500:
                NOTICES.pop(0)
        # reconnect/backoff with exponential backoff
        if not stop_event.is_set():
            time.sleep(backoff)
            backoff = min(backoff * 2, 600)


@app.route('/irc/register_session', methods=['POST'])
def irc_register_session():
    data = request.get_json() or {}
    nick = data.get('nick', 'session_bot')
    user = data.get('user', f'{nick} 0 * :Session Bot')
    channels = data.get('channels', ['#masterchief'])
    if nick in SESSIONS:
        return jsonify({'ok': False, 'error': 'session exists', 'nick': nick})
    if len(SESSIONS) >= SESSIONS_MAX:
        return jsonify({'ok': False, 'error': 'max sessions reached', 'limit': SESSIONS_MAX})
    stop_event = threading.Event()
    th = threading.Thread(target=_session_worker, args=(nick, user, channels, stop_event), daemon=True)
    SESSIONS[nick] = {'thread': th, 'stop': stop_event, 'channels': channels}
    th.start()
    return jsonify({'ok': True, 'nick': nick})


@app.route('/irc/sessions', methods=['GET'])
def irc_sessions():
    return jsonify({'sessions': {n:{'channels':v['channels']} for n,v in SESSIONS.items()}})


@app.route('/irc/session/stop', methods=['POST'])
def irc_session_stop():
    data = request.get_json() or {}
    nick = data.get('nick')
    if not nick or nick not in SESSIONS:
        return jsonify({'ok': False, 'error': 'unknown session'})
    SESSIONS[nick]['stop'].set()
    return jsonify({'ok': True, 'nick': nick})


@app.route('/irc/session/remove', methods=['POST'])
def irc_session_remove():
    """Force-remove a session from the in-memory registry.
    Payload: {"nick":"session_bot"}
    This sets the stop event (if present) and deletes the entry.
    """
    data = request.get_json() or {}
    nick = data.get('nick')
    if not nick:
        return jsonify({'ok': False, 'error': 'missing nick'})
    if nick not in SESSIONS:
        return jsonify({'ok': False, 'error': 'unknown session'})
    try:
        try:
            SESSIONS[nick]['stop'].set()
        except Exception:
            pass
        # remove the entry
        del SESSIONS[nick]
        return jsonify({'ok': True, 'nick': nick})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8080'))
    print(f"Flask SuperApp Final starting on port {port}...")
    # ensure any leftover in-memory session records are cleared on (re)start
    try:
        SESSIONS.clear()
    except Exception:
        pass
    app.run(debug=True, host='0.0.0.0', port=port)
