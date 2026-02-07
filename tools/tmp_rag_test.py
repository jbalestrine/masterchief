import requests
import sys


def main():
    s = requests.Session()
    base = 'http://127.0.0.1:8081'
    user = 'tmpagent'
    passw = 'agentpass'
    # Register (form-encoded)
    r = s.post(base + '/register', data={'username': user, 'password': passw}, timeout=30)
    print('REGISTER', r.status_code)
    # Login (form-encoded)
    r = s.post(base + '/login', data={'username': user, 'password': passw}, timeout=30)
    print('LOGIN', r.status_code)
    # Create conversation
    r = s.post(base + '/api/conversations/create', json={'username': user, 'title': 'tmp conv'}, timeout=30)
    print('CREATE CONV', r.status_code, r.text)
    conv_id = None
    try:
        conv_id = r.json().get('conv_id')
    except Exception:
        pass
    if not conv_id:
        r = s.get(base + '/api/conversations/list?username=' + user, timeout=30)
        print('LIST', r.status_code, r.text)
        try:
            conv_id = r.json()['conversations'][0]['id']
        except Exception:
            print('No conv found, abort')
            raise SystemExit(1)
    print('USING CONV', conv_id)
    # Post a message to ensure texts exist
    r = s.post(base + '/api/chat', json={'message': 'Testing installation steps and setup', 'username': user, 'conv_id': conv_id}, timeout=30)
    print('CHAT', r.status_code, r.text)
    # Index
    r = s.post(base + '/api/rag/index', json={'username': user, 'conv_id': conv_id}, timeout=120)
    print('INDEX', r.status_code, r.text)
    # Query
    r = s.post(base + '/api/rag/query', json={'username': user, 'conv_id': conv_id, 'query': 'installation'}, timeout=60)
    print('QUERY', r.status_code, r.text)


if __name__ == '__main__':
    main()
