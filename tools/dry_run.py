import json,shlex
# sample saved modified template (dry-run)
doc = {"parameters":{
    "client_id":{"type":"string","defaultValue":"CLIENT_ID_ABC"},
    "tenant_id":{"type":"string","defaultValue":"TENANT_ID_123"},
    "client_secret":{"type":"secureString","defaultValue":"CLIENT_SECRET_XYZ"},
    "env":{"defaultValue":"dev"},
    "param1":{"defaultValue":"val1"}
}}
# extract defaults
values={}
for k,v in doc.get('parameters',{}).items():
    if isinstance(v,dict) and 'defaultValue' in v:
        values[k]=v['defaultValue']
    elif not isinstance(v,dict):
        values[k]=v
# apply overrides (example)
overrides={'param1':'override1','extra_param':'extra'}
values.update(overrides)
# build az command (dry)
pid=123
org='https://dev.azure.com/example'
cmd=['az','pipelines','run','--id',str(pid)]
if org:
    cmd += ['--org', org]
for k,v in values.items():
    cmd += ['--variables', f"{k}={v}"]
print('EXTRACTED VALUES:')
print(json.dumps(values,indent=2))
print('\nAZ COMMAND (dry):')
print(' '.join(shlex.quote(x) for x in cmd))
