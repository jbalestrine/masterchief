#!/usr/bin/env python3
import requests, time, json
url = 'http://127.0.0.1:8090/api/echo/generate_image_async'
payload = {'prompt':'A small testing image — minimal','size':'512x512','session_id':'test'}
try:
    r = requests.post(url, json=payload, timeout=10)
    print('ENQUEUE RESPONSE:', r.status_code, r.text)
    if r.status_code==200:
        j = r.json()
        job_id = j.get('job_id')
        if job_id:
            print('Polling status for job:', job_id)
            for i in range(60):
                s = requests.get('http://127.0.0.1:8090/api/echo/image_status', params={'job_id': job_id}, timeout=10)
                print(i, s.status_code, s.text)
                if s.status_code==200:
                    sj = s.json()
                    if sj.get('status') in ('done','error'):
                        break
                time.sleep(2)
except Exception as e:
    print('Test failed:', e)
    import traceback
    traceback.print_exc()
