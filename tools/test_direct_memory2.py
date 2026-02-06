import time
import importlib.util
import os

# Load main.py as a module without executing the server run
spec = importlib.util.spec_from_file_location('main_mod', os.path.join(os.getcwd(), 'main.py'))
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)

sid = 'testsession2'
mem = main.get_session_memory(sid)
print('Initial facts:', mem.get('facts'))
new = main.extract_facts_from_text('my name is joe')
print('Extracted facts:', new)
main.merge_facts(mem.get('facts', {}), new)
mem['recent_messages'].append({'role':'user','text':'my name is joe','ts': int(time.time())})
ans = main.answer_from_session_memory(sid, "what's my name?")
print('Answer:', ans)
print('Final mem facts:', mem.get('facts'))
