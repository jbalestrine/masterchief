import urllib.request, urllib.parse, http.cookiejar, json, sys

BASE = 'http://127.0.0.1:8081'
CJ = http.cookiejar.CookieJar()
OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CJ))

def get(path):
    try:
        r = OPENER.open(BASE + path, timeout=5)
        print(f'GET {path} ->', r.getcode())
        return r.read().decode('utf-8')
    except Exception as e:
        print(f'GET {path} ERROR:', e)
        return None

def post_cmd(cmd):
    url = BASE + '/api/echo/chat'
    payload = json.dumps({'message': cmd}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type':'application/json'})
    try:
        r = OPENER.open(req, timeout=10)
        body = r.read().decode('utf-8')
        print(f'POST {cmd} -> {r.getcode()}')
        print(body)
        return body
    except Exception as e:
        print(f'POST {cmd} ERROR:', e)
        return None

if __name__ == '__main__':
    print('Checking root')
    get('/')
    print('\nAttempting !ops')
    post_cmd('!ops changeme')
    print('\nAttempting !drop')
    post_cmd('!drop gold 3')
    print('\nAttempting !revoke')
    post_cmd('!revoke')
    print('\nDone')
