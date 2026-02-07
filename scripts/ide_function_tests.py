import urllib.request, urllib.error, json, time

BASE = 'http://127.0.0.1:8080'


def request(url, method='GET', data=None):
    try:
        if data is not None:
            b = json.dumps(data).encode()
            req = urllib.request.Request(url, data=b, headers={'Content-Type':'application/json'}, method='POST')
        else:
            req = urllib.request.Request(url, method='GET')
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode(errors='replace')
            try:
                j = json.loads(body)
                return (r.status, j)
            except Exception:
                return (r.status, body)
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode(errors='replace')
        except Exception:
            body = '<no body>'
        return (e.code, body)
    except Exception as e:
        return ('ERR', str(e))


def save_file(name, content):
    return request(BASE + '/api/ide/save', 'POST', {'filename': name, 'content': content})


def load_file(name):
    return request(BASE + '/api/ide/load', 'POST', {'filename': name})


def exec_async(cmd):
    return request(BASE + '/api/ide/exec_async', 'POST', {'command': cmd})


def exec_status(exec_id):
    return request(BASE + '/api/ide/exec_status?exec_id=' + urllib.request.quote(exec_id))


def exec_execute(content, shell=None):
    payload = {'content': content}
    if shell:
        payload['shell'] = shell
    return request(BASE + '/api/ide/execute', 'POST', payload)


def remote_save(target, username, password):
    return request(BASE + '/api/ide/remote/creds', 'POST', {'target': target, 'username': username, 'password': password})


def remote_get(target):
    return request(BASE + '/api/ide/remote/creds?target=' + urllib.request.quote(target))


def ado_projects(org=''):
    return request(BASE + '/api/ide/ado/projects?org=' + urllib.request.quote(org))


def ado_pipelines(org=''):
    return request(BASE + '/api/ide/ado/pipelines?org=' + urllib.request.quote(org))


def az_login(check=False):
    return request(BASE + '/api/ide/azure/login', 'POST', {'check': check})


def az_resources():
    return request(BASE + '/api/ide/azure/resources')


if __name__ == '__main__':
    print('1) Save+Load round-trip')
    name = 'roundtrip_test.py'
    content = 'print("roundtrip ok")\n'
    s = save_file(name, content)
    print(' save:', s)
    l = load_file(name)
    print(' load:', l)
    ok_round = (isinstance(l, tuple) and l[0] == 200 and isinstance(l[1], dict) and l[1].get('content', '').strip() == content.strip())
    print(' roundtrip ok:', ok_round)

    print('\n2) Exec (sync) with python shell')
    exec_res = exec_execute('print("sync_ok")', shell='python')
    print(' exec:', exec_res)

    print('\n3) Exec async lifecycle')
    # create a tiny async script
    async_name = 'test_async_exec.py'
    async_content = 'import time\nprint("async start")\ntime.sleep(1)\nprint("async end")\n'
    print(' saving async script...')
    print(save_file(async_name, async_content))
    cmd = f'python {async_name}'
    start = exec_async(cmd)
    print(' exec_async start:', start)
    exec_id = None
    if isinstance(start, tuple) and start[0] == 200 and isinstance(start[1], dict):
        exec_id = start[1].get('exec_id')
    if exec_id:
        print(' polling exec_id', exec_id)
        total_wait = 0
        while total_wait < 30:
            st = exec_status(exec_id)
            print(' status:', st)
            if isinstance(st, tuple) and st[0] == 200 and isinstance(st[1], dict):
                job = st[1].get('job', {})
                if job.get('status') in ('finished','error'):
                    print(' final job:', job)
                    break
            time.sleep(1)
            total_wait += 1
        else:
            print(' timeout waiting for async job')
    else:
        print(' failed to start async job; response:', start)

    print('\n4) Remote creds save/load')
    targ='testhost'
    rs = remote_save(targ, 'testuser', 'p@ss')
    print(' save creds:', rs)
    rg = remote_get(targ)
    print(' get creds:', rg)

    print('\n5) ADO/Azure endpoint probes')
    print(' ado projects (empty org):', ado_projects(''))
    print(' ado pipelines (empty org):', ado_pipelines(''))
    print(' az login (check):', az_login(check=True))
    print(' az resources:', az_resources())

    print('\nDone')
