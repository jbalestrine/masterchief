import http.cookiejar, urllib.request, urllib.parse, sys


def main():
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
        raise SystemExit(1)

    import json, time, urllib.request

    root = __file__
    payload = {'type': 'session.create', 'name': 'test-session'}
    req = urllib.request.Request('http://127.0.0.1:8080/api/web_ide/session', data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as r:
        resp = json.loads(r.read().decode('utf-8'))
    print('resp', resp)
    if resp.get('ok') != True:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
