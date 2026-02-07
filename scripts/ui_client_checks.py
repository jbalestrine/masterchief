import urllib.request, urllib.error, json

BASE='http://127.0.0.1:8080'

def fetch(u):
    try:
        with urllib.request.urlopen(u, timeout=10) as r:
            return (r.status, r.read().decode(errors='replace'))
    except urllib.error.HTTPError as e:
        try:
            b=e.read().decode(errors='replace')
        except Exception:
            b=''
        return (e.code, b)
    except Exception as e:
        return ('ERR', str(e))

# check web_ide HTML for JS functions
status, body = fetch(BASE + '/web_ide')
print('/web_ide status ->', status)
if isinstance(body, str):
    keys = ['ideRun','ideRunAuto','ideSave','runAsync','runSync','loadFile','ideRefresh','ideUpload']
    found = {k: (k in body) for k in keys}
    print('JS function presence:')
    for k,v in found.items():
        print(' ',k,':',v)
else:
    print('No body fetched for /web_ide')

# test core endpoints
def test(name, path, method='GET', data=None):
    print('\nTesting',name, path)
    try:
        if method=='GET':
            s,b=fetch(BASE+path)
            print(' ',s, ('(JSON)' if b.strip().startswith('{') else ''))
        else:
            payload=json.dumps(data).encode()
            req=urllib.request.Request(BASE+path, data=payload, headers={'Content-Type':'application/json'}, method='POST')
            with urllib.request.urlopen(req, timeout=10) as r:
                print(' ', r.status)
                print(' ', r.read().decode(errors='replace')[:800])
    except Exception as e:
        print(' ERR', e)

test('scripts list','/api/ide/scripts')
test('tree','/api/ide/tree?path=')
test('load sample','/api/ide/load','POST', {'filename':'ui_test.py'})
test('save temp','/api/ide/save','POST', {'filename':'ui_check_tmp.py','content':'print("ok")'})
test('execute auto (content)','/api/ide/execute','POST', {'content':'print("auto_test")'})

print('\nDone')
