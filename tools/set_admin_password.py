import secrets, hashlib, json, sys
from pathlib import Path
p = Path(__file__).parent.parent / 'data' / 'echo_admin.json'
p.parent.mkdir(parents=True, exist_ok=True)
# generate a 20-character urlsafe token then trim to 20
pwd = secrets.token_urlsafe(16)
ph = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
obj = {'password_hash': ph, 'admins': []}
with open(p, 'w', encoding='utf-8') as f:
    json.dump(obj, f, indent=2)
print(pwd)
