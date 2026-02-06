import importlib
modules = ['numpy','sentence_transformers','faiss']
for m in modules:
    try:
        importlib.import_module(m)
        print(m + ' OK')
    except Exception as e:
        print(m + ' ERR: ' + str(type(e).__name__) + ' ' + str(e))
