#!/usr/bin/env python3
"""Extended benchmark: reload each discovered GGUF model, run longer prompts,
record timestamps, memory and CPU usage, and save results to data/bench_results.json
"""
import json
import time
import urllib.request
import psutil
from pathlib import Path

BASE='http://localhost:8081'
OUT=Path(__file__).parent.parent/'data'/'bench_results.json'
OUT.parent.mkdir(parents=True,exist_ok=True)

PROMPT = (
    "Explain step-by-step how to deploy a containerized web application to a Kubernetes "
    "cluster, including building the image, configuring manifests, applying resources, "
    "setting up ingress, and monitoring best practices. Provide commands and short "
    "examples."
)


def get(path):
    url = BASE + path
    with urllib.request.urlopen(url, timeout=600) as r:
        return json.load(r)


def post(path, data, timeout=600):
    url = BASE + path
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def sample_stats(pid):
    p = psutil.Process(pid)
    mem = p.memory_info().rss
    cpu = p.cpu_percent(interval=0.1)
    return {'rss_bytes': mem, 'cpu_percent': cpu}


def run():
    try:
        models = get('/api/echo/available_models').get('models', [])
    except Exception as e:
        print('Failed to list models:', e)
        models = []
    results = []
    # find Flask process
    flask_procs = [p for p in psutil.process_iter(['pid','name','cmdline']) if 'main.py' in ' '.join(p.info.get('cmdline') or [])]
    flask_pid = flask_procs[0].info['pid'] if flask_procs else None

    for m in models:
        name = m.get('name')
        print('=== Model:', name)
        record = {'name': name, 'path': m.get('path'), 'reload': {}, 'generations': []}
        # reload
        t0 = time.time()
        try:
            reload_res = post('/api/echo/reload_model', {'model_name': name})
            t1 = time.time()
            record['reload']['elapsed_s'] = round(t1-t0,2)
            record['reload']['result'] = reload_res
            print('Reload elapsed:', record['reload']['elapsed_s'], 's')
        except Exception as e:
            record['reload']['error'] = str(e)
            print('Reload failed:', e)
            results.append(record)
            continue
        time.sleep(1)
        # run a longer generation while sampling process stats
        gen_entry = {'prompt_len': len(PROMPT), 'samples': []}
        try:
            # sample before
            if flask_pid:
                gen_entry['samples'].append({'when':'before', **sample_stats(flask_pid)})
            t2 = time.time()
            chat_res = post('/api/echo/chat', {'message': PROMPT, 'session_id': 'bench_long'}, timeout=600)
            t3 = time.time()
            gen_entry['elapsed_s'] = round(t3-t2,2)
            gen_entry['response_snippet'] = (chat_res.get('response') or '')[:800]
            if flask_pid:
                gen_entry['samples'].append({'when':'after', **sample_stats(flask_pid)})
            print('Gen elapsed:', gen_entry['elapsed_s'], 's')
        except Exception as e:
            gen_entry['error'] = str(e)
            print('Generation failed:', e)
        record['generations'].append(gen_entry)
        results.append(record)
        # small cooldown
        time.sleep(2)
    OUT.write_text(json.dumps({'timestamp': time.time(), 'results': results}, indent=2))
    print('Saved results to', OUT)


if __name__=='__main__':
    run()
