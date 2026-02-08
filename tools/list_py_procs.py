import psutil
for p in psutil.process_iter(['pid','name','cmdline']):
    try:
        info=p.info
        if info['name'] and 'python' in info['name'].lower():
            print(info)
    except Exception:
        pass
