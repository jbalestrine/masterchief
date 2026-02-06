import requests, json, time
base='http://127.0.0.1:8081'
model_path = r"C:\users\Echo\masterchief\models\llama-7b\Wizard-Vicuna-7B-Uncensored.Q5_K_M.gguf"
print('Requesting reload for model:', model_path)
try:
    r = requests.post(base + '/api/echo/reload_model', json={'model_name': model_path}, timeout=600)
    print('Reload response:', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
except Exception as e:
    print('Reload request failed:', e)

# Wait a bit then check status and log
for i in range(6):
    time.sleep(2)
    try:
        r = requests.get(base + '/api/echo/model_status', timeout=10)
        print('\nmodel_status:', r.status_code, r.text)
    except Exception as e:
        print('model_status check failed:', e)
    try:
        r2 = requests.get(base + '/api/echo/gguf_log', timeout=10)
        print('\ngguf_log status', r2.status_code)
        try:
            print(json.dumps(r2.json(), indent=2))
        except Exception:
            print(r2.text[:1000])
    except Exception as e:
        print('gguf_log check failed:', e)
