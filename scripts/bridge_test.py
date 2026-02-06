import importlib.util, sys, json
spec = importlib.util.spec_from_file_location('irc_ui_app', r'c:\\Users\\Echo\\masterchief\\irc_flask_superapp_final\\app.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
app = mod.app

client = app.test_client()
# Build payload to simulate web UI
payload = {'lines': ['NICK webui_bot', 'USER webui_bot 0 * :Web UI Bot', 'JOIN #masterchief', 'PRIVMSG #masterchief :hello from webui']}
resp = client.post('/irc/send', data=json.dumps(payload), content_type='application/json')
print('send ->', resp.status_code, resp.get_json())
resp2 = client.get('/irc/notices')
print('notices ->', resp2.status_code, resp2.get_json())

# Now try registered flow
payload2 = {'nick': 'webui_reg', 'user': 'webui_reg 0 * :WebUI Registered', 'lines': ['JOIN #masterchief', 'PRIVMSG #masterchief :hello from registered webui']}
resp3 = client.post('/irc/send_registered', data=json.dumps(payload2), content_type='application/json')
print('send_registered ->', resp3.status_code, resp3.get_json())
resp4 = client.get('/irc/notices')
print('notices2 ->', resp4.status_code, resp4.get_json())
