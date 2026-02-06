import urllib.request, sys
print(urllib.request.urlopen('http://127.0.0.1:8080/api/resources/list', timeout=5).read().decode())
