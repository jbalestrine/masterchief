import requests
import json

url = 'http://127.0.0.1:8080/api/echo/chat'
prompt = (
    "You're a senior DevOps engineer. Provide a concise, actionable guide to deploy "
    "a Docker Compose application to Kubernetes. Include:")
prompt += (
    "\n\n1) A minimal `Deployment` and `Service` YAML manifest for a web app (one file),"
    "\n2) The `kubectl` commands to apply the manifest, create a namespace, and expose the app,"
    "\n3) A short explanation of how to convert `docker-compose.yml` to Kubernetes manifests,"
    "\n4) Example `kubectl` commands to monitor rollout status and fetch logs."
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
