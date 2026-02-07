import urllib.request, json, sys

data = json.dumps({'id': 'reference:test-upload-1768722618.txt'}).encode('utf-8')
req = urllib.request.Request('http://127.0.0.1:8080/api/resources/toggle_persona', data=data, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    try:
        body = e.read().decode('utf-8')
    except Exception:
        body = ''
    print('HTTPError', e.code, body)
except Exception as e:
    print('ERROR', e)

def main():
    url = 'http://127.0.0.1:8080/api/admin/toggle_feature?feature=Echo_Chat'
    with urllib.request.urlopen(url, timeout=5) as r:
        print(r.read().decode('utf-8'))

if __name__ == '__main__':
    main()
