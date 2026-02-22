import os
def feature_list_files():
    root = os.path.dirname(__file__)
    out = []
    for r,d,f in os.walk(root):
        for fn in f:
            out.append(os.path.relpath(os.path.join(r,fn), root))
    return {'files': out}

def feature_readme():
    root = os.path.dirname(__file__)
    for name in ('README.md','README','readme.md'):
        p = os.path.join(root,name)
        if os.path.exists(p):
            try:
                with open(p,'r',encoding='utf-8') as fh: return {'readme': fh.read()}
            except Exception as e:
                return {'error': str(e)}
    return {'readme': None}