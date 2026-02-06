import requests
import pathlib
import time

url = 'http://127.0.0.1:8080/feature/run/app_installer.feature_install_windows'
payload = {"app": "inspircd", "choco_package": "inspircd"}

print('POST', url)
resp = requests.post(url, json=payload, timeout=120)
print('HTTP', resp.status_code)
print(resp.text)

status_file = pathlib.Path('data/install_status/inspircd.json')
time.sleep(1)
if status_file.exists():
    print('\nSTATUS_FILE:')
    print(status_file.read_text(encoding='utf-8'))
else:
    print('\nSTATUS_FILE_NOT_FOUND')
