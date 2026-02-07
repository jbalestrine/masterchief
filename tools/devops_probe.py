import requests
import json

url = 'http://127.0.0.1:8080/api/echo/chat'
prompt = (
    "You're a senior DevOps engineer. Explain, step-by-step, how to deploy a simple "
    "Docker Compose application to a Kubernetes cluster. Include the key kubectl "
    "commands and a minimal example manifest for a Deployment and Service. Keep it "
    "concise but actionable."
)
payload = {'message': prompt}
try:
    r = requests.post(url, json=payload, timeout=120)
    print('STATUS', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
except Exception as e:
    print('ERROR', e)
