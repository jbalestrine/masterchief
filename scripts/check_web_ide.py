import urllib.request, json, urllib.error

def req(u, method='GET', data=None):
    try:
        if data is not None:
            b = json.dumps(data).encode()
            req = urllib.request.Request(u, data=b, headers={'Content-Type':'application/json'}, method='POST')
        else:
            req = urllib.request.Request(u)
        with urllib.request.urlopen(req, timeout=15) as r:
            print(u, r.status)
            body = r.read().decode(errors='replace')
            try:
                j = json.loads(body)
                print('JSON:', json.dumps(j))
            except Exception:
                print('BODYLEN', len(body))
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode(errors='replace')
        except Exception:
            body = '<no body>'
        print('HTTPERR', u, e.code, body)
    except Exception as e:
        print('ERR', u, e)

if __name__ == '__main__':
    req('http://127.0.0.1:8080')
    req('http://127.0.0.1:8080/web_ide')
    req('http://127.0.0.1:8080/web_ide.html')
    req('http://127.0.0.1:8080/api/ide/scripts')
    req('http://127.0.0.1:8080/api/ide/tree?path=')
    req('http://127.0.0.1:8080/api/ide/execute', data={'content':'echo web_ide_health'})
    # On Windows, executing a plain shell script will fail; also test with explicit python shell
    req('http://127.0.0.1:8080/api/ide/execute', data={'content':'print("web_ide_health")','shell':'python'})
    # Try loading an existing script from the scripts folder
    req('http://127.0.0.1:8080/api/ide/load', data={'filename':'ui_test.py'})
