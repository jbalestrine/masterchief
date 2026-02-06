import json,urllib.request,sys
url='http://127.0.0.1:8080/api/echo/chat'
data={'message':'test message from debug','session_id':'debug_ui_session'}
req=urllib.request.Request(url, data=json.dumps(data).encode(), headers={'Content-Type':'application/json'})
try:
    r=urllib.request.urlopen(req, timeout=30)
    print('STATUS', r.status)
    print(r.read().decode())
except Exception as e:
    try:
        # If HTTPError, show body
        import urllib.error
        if isinstance(e, urllib.error.HTTPError):
            print('HTTP ERROR', e.code)
            try:
                print(e.read().decode())
            except Exception:
                print(repr(e))
        else:
            print('ERROR',repr(e))
    except Exception:
        print('ERROR',repr(e))
    sys.exit(1)
    sys.exit(1)
