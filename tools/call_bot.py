import traceback
from echo.chat_bot import get_chat_bot
try:
    b=get_chat_bot()
    r=b.chat('hello from direct call', session_id='direct_debug')
    print('RESULT:',r)
except Exception as e:
    traceback.print_exc()
    print('ERROR:',e)
