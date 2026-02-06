import requests, json
base='http://127.0.0.1:8081'
print('GET /api/echo/model_status')
try:
    r=requests.get(base+'/api/echo/model_status', timeout=10)
    print(r.status_code)
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print('ERROR', e)

print('\nGET /api/echo/available_models')
try:
    r=requests.get(base+'/api/echo/available_models', timeout=10)
    print(r.status_code)
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print('ERROR', e)

print('\nGET /api/echo/gguf_log')
try:
    r=requests.get(base+'/api/echo/gguf_log', timeout=10)
    print(r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text[:400])
except Exception as e:
    print('ERROR', e)

print('\nPOST /api/echo/reload_model (no model_name)')
try:
    r=requests.post(base+'/api/echo/reload_model', timeout=30)
    print(r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text[:400])
except Exception as e:
    print('ERROR', e)
