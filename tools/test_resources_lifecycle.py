import json, urllib.request, urllib.parse, pathlib, time


def main():
    root = pathlib.Path(__file__).resolve().parents[1]
    # Upload a file
    upload_url = 'http://127.0.0.1:8080/api/resources/upload'
    file_path = root / 'data' / 'resources' / 'test-lifecycle.txt'
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text('Lifecycle test content', encoding='utf-8')

    # build multipart
    import mimetypes, uuid
    boundary = uuid.uuid4().hex
    lines = []
    fields = {'category': 'examples', 'for_ingestion': 'on', 'for_training': 'on'}
    for k, v in fields.items():
        lines.append('--' + boundary)
        lines.append(f'Content-Disposition: form-data; name="{k}"')
        lines.append('')
        lines.append(v)
    with open(file_path, 'rb') as f:
        data = f.read()
    lines.append('--' + boundary)
    lines.append(f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"')
    ctype = mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
    lines.append(f'Content-Type: {ctype}')
    lines.append('')
    lines_bytes = b"\r\n".join([l if isinstance(l, bytes) else l.encode('utf-8') for l in lines]) + b"\r\n" + data + b"\r\n--" + boundary.encode('utf-8') + b"--\r\n"
    req = urllib.request.Request(upload_url, data=lines_bytes, headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.loads(r.read().decode('utf-8'))
        print('upload response', resp)
        rid = resp['resource']['id']
    except Exception as e:
        # if duplicate, derive rid from category and filename
        print('upload error', e)
        rid = 'examples:' + file_path.name
        print('using existing rid', rid)

    # Enqueue ingest
    enqueue_url = 'http://127.0.0.1:8080/api/resources/enqueue_ingest'
    req = urllib.request.Request(enqueue_url, data=json.dumps({'id': rid, 'session_id': 'test_lifecycle_session'}).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        er = json.loads(r.read().decode('utf-8'))
    print('enqueue', er)
    tid = er.get('task_id')

    # Poll status
    status_url = 'http://127.0.0.1:8080/api/resources/ingest_status?task_id=' + urllib.parse.quote(tid)
    for i in range(30):
        with urllib.request.urlopen(status_url, timeout=30) as r:
            s = json.loads(r.read().decode('utf-8'))
        print('status', s.get('status'))
        if s.get('status') == 'done':
            break
        time.sleep(1)

    # Check session meta
    meta_file = root / 'data' / 'sessions_meta.json'
    meta = json.loads(meta_file.read_text(encoding='utf-8'))
    print('session meta keys:', list(meta.get('test_lifecycle_session', {}).get('ingestions', {}).keys()))

    # cleanup
    try:
        # delete resource
        del_url = 'http://127.0.0.1:8080/api/resources/delete'
        req = urllib.request.Request(del_url, data=json.dumps({'id': rid}).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as r:
            print('deleted', json.loads(r.read().decode('utf-8')))
    except Exception as e:
        print('cleanup failed', e)


if __name__ == '__main__':
    main()
