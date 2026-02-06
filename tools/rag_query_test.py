import requests,sys
s=requests.Session()
base='http://127.0.0.1:8081'
user='tmpagent'
passw='agentpass'
# try login
r=s.post(base+'/login', data={'username':user,'password':passw}, timeout=30)
print('LOGIN', r.status_code)
# Use tmpagent's conv
conv='conv_1768666785586'
# Ensure texts exist then index
r=s.post(base+'/api/rag/index', json={'conv_id':conv}, timeout=120)
print('INDEX', r.status_code, r.text)
# Query
r=s.post(base+'/api/rag/query', json={'conv_id':conv,'query':'installation','topk':5}, timeout=60)
print('QUERY', r.status_code, r.text)
