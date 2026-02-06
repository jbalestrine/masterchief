import psutil
for p in psutil.process_iter(['pid','name','cmdline']):
    try:
        cmd = p.info.get('cmdline') or []
        if any('main.py' in str(c) for c in cmd):
            print(p.info)
    except Exception:
        pass
