import json
import sys
from urllib import request, error


def main():
    ports = (8081, 8080)
    payload = {'message': 'Hello from test client - checking GGUF load', 'session_id': 'test_session'}
    data = json.dumps(payload).encode('utf-8')
    resp_ok = False
    last_err = None
    for p in ports:
        url = f'http://localhost:{p}/api/echo/chat'
        req = request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
        try:
            with request.urlopen(req, timeout=15) as resp:
                body = resp.read().decode('utf-8')
                print('STATUS', resp.status)
                print('RESPONSE', body)
                resp_ok = True
                break
        except error.HTTPError as e:
            print('HTTP ERROR', e.code, e.read().decode('utf-8'))
            last_err = e
        except Exception as e:
            print('ERROR', e)
            last_err = e

    if not resp_ok:
        # exit with non-zero to indicate test failure
        sys.exit(2)


if __name__ == '__main__':
    main()
