import requests, time
base='http://127.0.0.1:8081'
s=requests.Session()
conv='conv_1768665425393'
print('Requesting index for', conv)
r=s.post(base+'/api/rag/index', json={'conv_id':conv}, timeout=10)
print('INDEX', r.status_code, r.text)
if r.status_code==202:
    for _ in range(300):
        time.sleep(2)
        r2=s.get(base+f'/api/rag/status?conv_id={conv}', timeout=10)
        print('STATUS', r2.status_code, r2.text)
        try:
            st = r2.json().get('status')
            if st in ('done','failed','deferred'):
                break
        except Exception:
            pass
else:
    print('Index request returned:', r.text)

print('Querying...')
r=s.post(base+'/api/rag/query', json={'conv_id':conv,'query':'installation','topk':5}, timeout=30)
print('QUERY', r.status_code, r.text)
