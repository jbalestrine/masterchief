import sys
sys.path.append('.')
from managers.script import ScriptManager

mgr = ScriptManager('scripts')
print('Testing script execution...')
result = mgr.execute_script('date.ps1')
print(f'Result: {result}')