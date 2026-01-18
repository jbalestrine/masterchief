#!/usr/bin/env python3
import requests, json, sys

def main():
    try:
        r = requests.get('http://127.0.0.1:8080/api/resources/list', timeout=5)
        print('GET /api/resources/list ->', r.status_code)
        idx = r.json()
        if not idx:
            print('No resources available to enqueue.')
            return
        first = list(idx.keys())[0]
        print('Enqueueing resource:', first)
        r2 = requests.post('http://127.0.0.1:8080/api/resources/enqueue_ingest', json={'id': first, 'session_id': 'verify_ingest_cli'}, timeout=5)
        print('POST /api/resources/enqueue_ingest ->', r2.status_code, r2.text)
    except Exception as e:
        print('Error during enqueue test:', e)

if __name__ == '__main__':
    main()
