import urllib.request, json, sys

def get(url):
    req = urllib.request.Request(url, headers={'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def post(url, data):
    b = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=b, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)

def main():
    base = 'http://127.0.0.1:8080'
    try:
        # fetch available models and training files
        models = get(base + '/api/echo/models')
        print('---MODELS---')
        print(json.dumps(models, indent=2))
        tf = get(base + '/api/echo/training_files')
    except Exception as e:
        print('GET /api/echo/training_files failed:', e)
        sys.exit(1)
    print('---TRAINING_FILES---')
    print(json.dumps(tf, indent=2))
    files = tf.get('files') or []
    if not files:
        print('No training files found')
        return
    file = files[0]['name']
    print('---SELECTED_FILE---', file)
    models_list = models.get('models') or []
    if not models_list:
        print('No models discovered under models/; aborting start')
        return
    model_path = models_list[0]
    print('---SELECTED_MODEL---', model_path)
    body = {'model': model_path, 'training_file': file, 'output_name': 'test_output', 'epochs': 1, 'batch_size': 8, 'lr': '1e-4'}
    print('---REQUEST_BODY---')
    print(json.dumps(body))
    try:
        resp = post(base + '/api/echo/train_model', body)
    except Exception as e:
        print('POST /api/echo/train_model failed:', e)
        sys.exit(1)
    print('---POST_RESPONSE---')
    print(json.dumps(resp, indent=2))

if __name__ == '__main__':
    main()
