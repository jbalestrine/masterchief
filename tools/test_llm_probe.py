from echo.chat_bot import get_chat_bot
import json

bot = get_chat_bot()
print('Local model path:', getattr(bot, '_local_model_path', None))
# Use a DevOps-related prompt to force the LLM path (bypasses trivial greetings)
res = bot.chat('How do I deploy a docker container using docker compose?', session_id='probe')
print('Chat response:')
print(json.dumps(res, indent=2))
print('\nLLM debug info:')
try:
    dbg = getattr(bot, '_last_llm_debug', None)
    print(json.dumps(dbg, indent=2))
except Exception as e:
    print('Failed to dump debug:', e)
