import importlib.util, os, json
spec = importlib.util.spec_from_file_location('main_mod', os.path.join(os.getcwd(), 'main.py'))
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)
app = getattr(main, 'app')

with app.test_client() as c:
    r = c.post('/api/echo/chat', json={'message':'hello test from test_client','session_id':'test_restore'})
    print('STATUS', r.status_code)
    try:
        print(json.dumps(r.get_json(), indent=2))
    except Exception:
        print(r.data.decode('utf-8'))
