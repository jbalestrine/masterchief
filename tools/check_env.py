from echo.chat_bot import get_chat_bot
b=get_chat_bot()
print('session dir exists?', b._session_dir.exists())
print('list sessions', b.list_sessions()[:10])
print('find gguf', b._find_gguf_model())
