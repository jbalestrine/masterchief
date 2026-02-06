import importlib.util, traceback
try:
    spec = importlib.util.spec_from_file_location('m','main.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    print('imported ok')
except Exception:
    traceback.print_exc()
