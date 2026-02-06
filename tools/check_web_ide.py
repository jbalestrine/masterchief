import urllib.request, json, sys
url = 'http://127.0.0.1:8080/api/ide/scripts'
try:
    r = urllib.request.urlopen(url, timeout=5)
    data = r.read().decode('utf-8', errors='ignore')
    print('STATUS', r.status)
    print(data[:2000])
except Exception as e:
    print('ERROR', e)
    sys.exit(1)
