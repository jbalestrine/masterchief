import time
import subprocess
import psutil
import requests
import os
import sys

PROJECT_DIR = r"C:\Users\Echo\masterchief"
VENV_PY = os.path.join(PROJECT_DIR, 'venv', 'Scripts', 'python.exe')
MAIN_PY = os.path.join(PROJECT_DIR, 'main.py')
PORT = 8080

def kill_port(port):
    for conn in psutil.net_connections():
        if conn.laddr and conn.laddr.port == port:
            try:
                p = psutil.Process(conn.pid)
                print(f'Killing pid {p.pid} ({p.name()}) holding port {port}')
                p.kill()
            except Exception as e:
                print('Failed to kill', conn.pid, e)

def start_server():
    if not os.path.exists(VENV_PY):
        print('Venv python not found at', VENV_PY)
        print('Falling back to current Python executable:', sys.executable)
        py = sys.executable
    else:
        py = VENV_PY
    print('Starting server with', py)
    proc = subprocess.Popen([py, MAIN_PY, '--port', str(PORT)], cwd=PROJECT_DIR)
    print('Started server pid', proc.pid)
    return proc


def call(path):
    url = f'http://127.0.0.1:{PORT}{path}'
    try:
        r = requests.get(url, timeout=10)
        print(f'[{r.status_code}] {path} ->', r.text[:800])
    except Exception as e:
        print('ERROR calling', path, e)

if __name__ == '__main__':
    print('Stopping any process on port', PORT)
    kill_port(PORT)
    proc = start_server()
    print('Waiting 3s for server to start...')
    time.sleep(3)
    print('\n---TEST: /api/resources/list---')
    call('/api/resources/list')
    print('\n---TEST: /api/echo/training_files---')
    call('/api/echo/training_files')
    print('\n---TEST: /resources/preview?id=error---')
    call('/resources/preview?id=error')
    print('\nDone. Server pid', proc.pid)
    print('If you want to stop server, kill the pid above or CTRL+C the terminal running it.')
