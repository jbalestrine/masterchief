#!/usr/bin/env python3
import json
import time
import urllib.request

BASE='http://localhost:8081'

def get(path):
    url = BASE + path
    with urllib.request.urlopen(url, timeout=600) as r:
        return json.load(r)

def post(path, data):
    url = BASE + path
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)

if __name__=='__main__':
    try:
        models = get('/api/echo/available_models').get('models', [])
    except Exception as e:
        print('Failed to list models:', e)
        models = []
    if not models:
        print('No models found under models/.')
    for m in models:
        name = m.get('name')
        path = m.get('path')
        print('=== Model:', name, 'path:', path)
        try:
            t1 = time.time()
            reload_res = post('/api/echo/reload_model', {'model_name': name})
            t2 = time.time()
            print('Reload elapsed:', round(t2-t1,2), 's, loaded:', reload_res.get('model_loaded'))
        except Exception as e:
            print('Reload failed:', e)
            continue
        time.sleep(1)
        try:
            t3 = time.time()
            chat_res = post('/api/echo/chat', {'message':'Summarize how to deploy a containerized app', 'session_id':'bench'})
            t4 = time.time()
            print('Gen elapsed:', round(t4-t3,2), 's')
            resp = chat_res.get('response','')
            print('Response (trim):', resp.replace('\n',' ')[:400])
        except Exception as e:
            print('Generation failed:', e)
        print()