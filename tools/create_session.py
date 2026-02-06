import urllib.request, json
url = 'http://127.0.0.1:8080/irc/connect'
data = json.dumps({"host":"127.0.0.1","port":6667,"nick":"testbot_stream"}).encode()
req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json"})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    body = resp.read().decode()
    print('STATUS', resp.status)
    print(body)
    print('JSON:', json.loads(body))
except Exception as e:
    print('ERR', e)
