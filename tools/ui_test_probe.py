import urllib.request, json, time
base='http://127.0.0.1:8080'
print('Probing', base)
try:
    r=urllib.request.urlopen(base+'/api/echo/sessions', timeout=5)
    print('sessions before:', r.read().decode())
except Exception as e:
    print('sessions before error', e)
# send message
req=urllib.request.Request(base+'/api/echo/chat', data=json.dumps({'message':'hello from ui test','session_id':'ui_test_tab'}).encode(), headers={'Content-Type':'application/json'})
try:
    r=urllib.request.urlopen(req, timeout=30)
    print('/api/echo/chat ->', r.status, r.read().decode()[:1000])
except Exception as e:
    print('/api/echo/chat error', e)
# wait a bit
time.sleep(1)
try:
    r=urllib.request.urlopen(base+'/api/echo/sessions', timeout=5)
    print('sessions after:', r.read().decode())
    r=urllib.request.urlopen(base+'/api/echo/session/ui_test_tab', timeout=5)
    print('session content:', r.read().decode()[:1000])
except Exception as e:
    print('post-check error', e)
