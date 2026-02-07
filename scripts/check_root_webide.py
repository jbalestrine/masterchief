import urllib.request
u='http://127.0.0.1:8080'
with urllib.request.urlopen(u,timeout=10) as r:
    body=r.read().decode()
    print('/web_ide' in body)
    print(r.status)
