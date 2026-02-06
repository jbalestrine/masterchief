import requests
s=requests.Session()
base='http://127.0.0.1:8081'
# hit session/get to run auto-auth
r=s.get(base+'/api/session/get')
print('session pre:', r.status_code, r.text)
# query indexed testuser conv
r=s.post(base+'/api/rag/query', json={'conv_id':'conv_1768665425393','query':'installation','topk':3}, timeout=60)
print('QUERY', r.status_code, r.text)
