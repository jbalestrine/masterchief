import urllib.request, json, sys, subprocess, os, time

BASE='http://127.0.0.1:8080'

def get(path):
    with urllib.request.urlopen(BASE+path, timeout=30) as r:
        return json.load(r)

def post(path, data):
    b = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(BASE+path, data=b, headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def main():
    try:
        m = get('/api/echo/model')
    except Exception as e:
        print('GET /api/echo/model failed:', e)
        sys.exit(1)
    print('MODEL:', json.dumps(m, indent=2))
    model = m.get('model')
    print('\nCalling /api/echo/preload_model to warm the model...')
    try:
        warmed = get('/api/echo/preload_model')
        print('PRELOAD:', json.dumps(warmed, indent=2))
    except Exception as e:
        print('PRELOAD failed:', e)

    msg = 'How do I deploy a Docker container using Docker Compose and environment variables?'
    print('\nPOST /api/echo/chat with message:', msg)
    try:
        resp = post('/api/echo/chat', {'message': msg, 'session_id': 'diag_'+str(int(time.time()))})
        print('CHAT RESPONSE:', json.dumps(resp, indent=2))
    except Exception as e:
        try:
            print('CHAT failed, reading error body...')
        except Exception:
            pass
        print('CHAT request exception:', e)

    # If model exists, try running the worker directly
    if model:
        print('\nInvoking llm_worker directly to test generation...')
        worker = os.path.join(os.path.dirname(__file__), '..', 'echo', 'llm_worker.py')
        worker = os.path.abspath(worker)
        if not os.path.exists(worker):
            print('llm_worker not found at', worker)
            return
        cmd = [sys.executable, worker, '--model', model, '--max_tokens', '128', '--temperature', '0.2']
        print('CMD:', cmd)
        try:
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            out, err = p.communicate(msg, timeout=60)
            print('\nLLM_WORKER STDOUT:\n', out)
            print('\nLLM_WORKER STDERR:\n', err)
        except Exception as e:
            print('Worker invocation failed:', e)

if __name__=='__main__':
    main()
