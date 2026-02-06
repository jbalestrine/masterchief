import requests, json, sys
try:
    r = requests.post('http://127.0.0.1:8080/irc/recreate_from_container', json={'container':'inspircd'}, timeout=120)
    print('STATUS', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
except Exception as e:
    print('ERROR', repr(e))
    sys.exit(2)
