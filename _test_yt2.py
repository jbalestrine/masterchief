import requests, json, sys
try:
    r = requests.get('http://localhost:8080/api/echo/youtube_search?q=bohemian+rhapsody+queen', timeout=15)
    with open('_yt_result.txt', 'w') as f:
        f.write(f'STATUS: {r.status_code}\n')
        f.write(f'BODY: {r.text}\n')
except Exception as e:
    with open('_yt_result.txt', 'w') as f:
        f.write(f'ERROR: {e}\n')
