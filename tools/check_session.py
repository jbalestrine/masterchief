import requests
s = requests.Session()
print(s.get('http://127.0.0.1:8081/api/session/get').text)
