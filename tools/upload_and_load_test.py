#!/usr/bin/env python3
import requests, json, tempfile, os, sys, time

BASE='http://127.0.0.1:8080'

def main():
    fname = 'test-upload-{}.txt'.format(int(time.time()))
    with open(fname, 'w', encoding='utf-8') as f:
        f.write('This is a test upload for training and ingestion.\nVerify ingest content for bot knowledge')
    try:
        files={'file': open(fname,'rb')}
        data={'category':'reference','for_training':'on','for_ingestion':'on'}
        r = requests.post(BASE+'/api/resources/upload', files=files, data=data, timeout=10)
        print('upload:', r.status_code, r.text)
        if r.status_code!=200:
            return
        res = r.json().get('resource')
        rid = res.get('id')
        # load into session and request immediate ingest
        payload={'id': rid, 'session_id': 'test_upload_session', 'for_training': True, 'for_ingestion': True}
        r2 = requests.post(BASE+'/api/resources/load', json=payload, timeout=10)
        print('load:', r2.status_code, r2.text)
        # Check training examples file
        te_path = os.path.join('data','echo_training','training_examples.jsonl')
        if os.path.exists(te_path):
            print('training_examples last line:')
            with open(te_path,'r',encoding='utf-8') as f:
                lines=[l for l in f.readlines() if l.strip()]
                if lines:
                    print(lines[-1].strip())
                else:
                    print('(empty)')
        else:
            print('training_examples missing')
        # list knowledge files
        ks_dir = os.path.join('data','knowledge')
        if os.path.exists(ks_dir):
            print('knowledge files:', os.listdir(ks_dir))
        else:
            print('knowledge dir missing')
    except Exception as e:
        print('error', e)
    finally:
        try:
            os.remove(fname)
        except Exception:
            pass

if __name__=='__main__':
    main()
