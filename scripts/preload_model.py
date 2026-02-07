import urllib.request, json, sys
model='models/qwen2.5-7b-instruct-q4_k_m.gguf'
print('Selecting model:', model)
req = urllib.request.Request('http://127.0.0.1:8080/api/echo/select_model', data=json.dumps({'model': model}).encode(), headers={'Content-Type':'application/json'})
try:
    with urllib.request.urlopen(req, timeout=120) as r:
        print('select_model HTTP', r.status)
        print(r.read().decode())
except Exception as e:
    print('select_model failed:', e)

print('\nCalling preload_model...')
req2 = urllib.request.Request('http://127.0.0.1:8080/api/echo/preload_model', data=b'{}', headers={'Content-Type':'application/json'})
try:
    with urllib.request.urlopen(req2, timeout=120) as r:
        print('preload_model HTTP', r.status)
        print(r.read().decode())
except Exception as e:
    print('preload_model failed:', e)
