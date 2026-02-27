import requests, json
r = requests.get('http://localhost:8080/api/echo/youtube_search?q=bohemian+rhapsody+queen', timeout=15)
print('STATUS:', r.status_code)
print('BODY:', r.text)
