import sys, time, json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

BASE='http://127.0.0.1:8081'

def wait_up(timeout=15):
    deadline=time.time()+timeout
    while time.time()<deadline:
        try:
            r=urlopen(BASE+'/features', timeout=3)
            if r.getcode()==200:
                print('up')
                return True
        except Exception as e:
            time.sleep(1)
    print('timeout')
    return False


def post_features(features):
    data=json.dumps({'features': features}).encode('utf-8')
    req=Request(BASE+'/api/features/save', data=data, headers={'Content-Type':'application/json'})
    try:
        r=urlopen(req, timeout=5)
        print('post_status', r.getcode())
        print(r.read().decode('utf-8'))
        return r.getcode()==200
    except HTTPError as e:
        print('post_error', e.code, e.read().decode('utf-8'))
        return False
    except URLError as e:
        print('post_error', e)
        return False


def check_nav_contains(path):
    try:
        r=urlopen(BASE+'/', timeout=5)
        content=r.read().decode('utf-8')
        ok = path in content
        print('contains', ok)
        return ok
    except Exception as e:
        print('nav_error', e)
        return False

if __name__=='__main__':
    if not wait_up(20):
        sys.exit(2)
    success=post_features(['addons'])
    if not success:
        sys.exit(3)
    time.sleep(1)
    ok=check_nav_contains('/feature/addons')
    if ok:
        print('TEST OK')
        sys.exit(0)
    else:
        print('TEST FAIL')
        sys.exit(4)
