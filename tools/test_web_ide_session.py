import http.cookiejar, urllib.request, urllib.parse, sys

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
try:
    opener.open('http://127.0.0.1:8080/web_ide/login', timeout=5)
    data = urllib.parse.urlencode({'username':'ide','password':'x'}).encode()
    opener.open('http://127.0.0.1:8080/web_ide/login', data=data, timeout=5)
    r = opener.open('http://127.0.0.1:8080/web_ide', timeout=5)
    print('WEBIDE', r.getcode())
    print(r.read(400).decode('utf-8', errors='ignore'))
    r2 = opener.open('http://127.0.0.1:8080/api/ide/scripts', timeout=5)
    print('SCRIPTS', r2.getcode())
    print(r2.read(2000).decode('utf-8', errors='ignore'))
except Exception as e:
    print('ERROR', e)
    sys.exit(1)
