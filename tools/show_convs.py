import json,glob,os
base=os.path.join(os.getcwd(),'data','conversations','testuser')
if not os.path.isdir(base):
    print('No conversation dir', base)
else:
    files=glob.glob(os.path.join(base,'*.json'))
    print('Found', len(files), 'files')
    for p in files:
        print('---',p)
        print(open(p,'r',encoding='utf-8').read())
