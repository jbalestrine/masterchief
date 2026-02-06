import time
import json
import requests
import subprocess
from datetime import datetime

BASE='http://127.0.0.1:8080'
OUT_DIR='data/install_status'
LOGFILE=f"{OUT_DIR}/inspircd.webui.test.{int(time.time())}.log"

sess = requests.Session()

def save(msg):
    print(msg)
    with open(LOGFILE,'a',encoding='utf-8') as f:
        f.write(f"{datetime.utcnow().isoformat()} {msg}\n")

def connect(nick='webtester', user='webtester', real='Web Tester'):
    payload={
        'host':'127.0.0.1','port':6667,'nick':nick,'username':user,'realname':real,'ssl':False
    }
    save(f"CONNECT payload: {payload}")
    r=sess.post(BASE+'/irc/connect',json=payload,timeout=10)
    save(f"CONNECT status: {r.status_code} {r.text}")
    try:
        return r.json()
    except Exception:
        return {}

def recv(session_id, attempts=10, wait=0.5):
    out=[]
    for i in range(attempts):
        try:
            r=sess.get(BASE+f'/irc/recv?session_id={session_id}',timeout=5)
            j=r.json()
            out.extend(j.get('messages',[]))
            save(f"recv[{i}] alive={j.get('alive')} messages={len(j.get('messages',[]))}")
            if not j.get('alive'):
                break
        except Exception as e:
            save(f"recv error: {e}")
        time.sleep(wait)
    return out

def send(session_id, line):
    payload={'session_id':session_id,'line':line}
    r=sess.post(BASE+'/irc/send',json=payload,timeout=5)
    save(f"SEND {line} -> {r.status_code} {r.text}")
    return r


def close(session_id):
    try:
        r=sess.post(BASE+'/irc/close',json={'session_id':session_id},timeout=5)
        save(f"CLOSE -> {r.status_code} {r.text}")
    except Exception as e:
        save(f"CLOSE error: {e}")


def tail_docker_logs():
    save('== docker logs start ==')
    try:
        p=subprocess.run(['docker','logs','--tail','200','inspircd'],capture_output=True,text=True,timeout=20)
        save(p.stdout)
    except Exception as e:
        save(f'docker logs error: {e}')
    save('== docker logs end ==')


if __name__=='__main__':
    save('Starting webui IRC automated test')
    # ensure out dir exists
    import os
    os.makedirs(OUT_DIR,exist_ok=True)

    info = connect()
    session_id = info.get('session_id')
    if not session_id:
        save('No session_id returned; aborting')
    else:
        save(f'Session id: {session_id}')
        time.sleep(1)
        msgs = recv(session_id, attempts=6, wait=1)
        save(f'Initial messages: {len(msgs)}')

        # Join a test channel
        chan = '#masterchief-test'
        send(session_id, f'JOIN {chan}')
        time.sleep(1)
        msgs = recv(session_id, attempts=6, wait=1)
        save(f'After JOIN messages: {len(msgs)}')

        # Send a PRIVMSG to channel
        send(session_id, f'PRIVMSG {chan} :Hello from webui test')
        time.sleep(1)
        msgs = recv(session_id, attempts=8, wait=1)
        save(f'After PRIVMSG messages: {len(msgs)}')

        # Optionally send a direct PRIVMSG to the nick
        send(session_id, f'PRIVMSG {session_id} :direct ping')
        time.sleep(1)
        msgs = recv(session_id, attempts=6, wait=1)
        save(f'After direct PRIVMSG messages: {len(msgs)}')

        close(session_id)

    # Gather docker logs
    tail_docker_logs()
    save('WebUI IRC automated test complete')
