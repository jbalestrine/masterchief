import requests
import json

base='http://127.0.0.1:8081'
s=requests.Session()
# no explicit login; server auto-auth should set session cookie
conv='conv_1768665425393'
print('Indexing', conv)
r=s.post(base+'/api/rag/index', json={'conv_id':conv}, timeout=300)
print('INDEX', r.status_code, r.text)
print('\nQuerying for "installation"')
r=s.post(base+'/api/rag/query', json={'conv_id':conv,'query':'installation','topk':5}, timeout=60)
print('QUERY', r.status_code, r.text)

# Also show reload attempt
print('\nReloading registry')
r=s.post(base+'/api/rag/reload', timeout=30)
print('RELOAD', r.status_code, r.text)
