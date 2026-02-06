import py_compile, traceback, sys
try:
    py_compile.compile('main.py', doraise=True)
    print('OK')
except Exception:
    traceback.print_exc()
    sys.exit(1)
