import urllib.request,sys
url='http://127.0.0.1:8080/api/echo/model'
try:
    with urllib.request.urlopen(url,timeout=5) as r:
        print(r.status)
        print(r.read().decode())
except Exception as e:
    print('ERR',e)
    sys.exit(1)
