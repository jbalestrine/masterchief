#!/usr/bin/env python3
import requests, subprocess, time, os, sys, json, uuid

BRIDGE_CONNECT = 'http://127.0.0.1:8080/irc/connect'
RUNNER = os.path.join('modules','qwen_inspircd','run.py')
LOG = os.path.join('logs','module_runner.log')

print('Requesting session/bridge token from', BRIDGE_CONNECT)
payload = {'host':'127.0.0.1','port':6667,'nick': 'runner-' + uuid.uuid4().hex[:6]}
try:
    r = requests.post(BRIDGE_CONNECT, json=payload, timeout=10)
    r.raise_for_status()
except Exception as e:
    print('Failed to contact server:', e, file=sys.stderr)
    sys.exit(2)

try:
    data = r.json()
except Exception:
    print('Non-JSON response:', r.text)
    sys.exit(2)

token = data.get('bridge_token') or data.get('bridgeToken')
session = data.get('session') or data.get('id')
if not token:
    print('No bridge token returned:', data, file=sys.stderr)
    sys.exit(3)

print('Got bridge token:', token)

channel = os.environ.get('MC_CHANNEL', '#masterchief')
cmd = [sys.executable, RUNNER, '--bridge-token', token, '--session', session, '--channel', channel]
print('Starting runner:', ' '.join(cmd))
os.makedirs(os.path.dirname(LOG), exist_ok=True)
logf = open(LOG, 'ab')
proc = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT)
print('Runner PID', proc.pid, 'stdout->', LOG)
print('Done. Tail the runner log with PowerShell:')
print('  Get-Content -Path "{}" -Wait -Tail 200'.format(LOG))
