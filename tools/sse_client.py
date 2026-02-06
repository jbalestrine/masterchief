import requests, sseclient, sys, time

if len(sys.argv)<2:
    print('Usage: sse_client.py <session> [last]')
    sys.exit(1)
session = sys.argv[1]
last = int(sys.argv[2]) if len(sys.argv)>2 else 0
url = f'http://127.0.0.1:8080/irc/stream?session={session}&last={last}'
print('Connecting to', url)
try:
    resp = requests.get(url, stream=True, timeout=10)
    client = sseclient.SSEClient(resp)
    for ev in client.events():
        print('EVENT:', ev.data)
except Exception as e:
    print('SSE client error', e)
