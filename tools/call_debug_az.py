import requests
s = requests.Session()
# login
s.post('http://127.0.0.1:8080/web_ide/login', data={'username':'ide','password':'x'})
try:
    r = s.get('http://127.0.0.1:8080/api/debug/az_info', timeout=5)
    print(r.status_code)
    print(r.text)
except Exception as e:
    print('ERR', e)
