import re
with open('main.py', encoding='utf-8') as f:
    text = f.read()
# Find TEAMS_TEMPLATE by looking for the <script> block within it
# Find the template start
start = text.find('TEAMS_TEMPLATE = """')
if start == -1:
    start = text.find("TEAMS_TEMPLATE = '''")
print('Template starts at char:', start)
# Find <script> after TEAMS_TEMPLATE
js_start = text.find('<script>', start)
js_end = text.find('</script>', js_start)
js = text[js_start+8:js_end]
with open('_teams_check.js', 'w', encoding='utf-8') as out:
    out.write(js)
print('JS extracted, length:', len(js))
# Check for key identifiers
for needle in ['tmSetMode', '_teamsUpn', 'teamsConnect', 'teamsDisconnect', 'teamsLoadRange', '_tmMode', 'use_me']:
    print(f'  {"OK" if needle in js else "MISSING"}: {needle}')
