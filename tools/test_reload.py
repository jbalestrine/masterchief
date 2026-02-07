import json
from echo.chat_bot import get_chat_bot
bot = get_chat_bot()
res = bot.reload_model(model_name='Wizard-Vicuna-7B-Uncensored.Q5_K_M.gguf')
print(json.dumps(res, default=str, indent=2))
print('model_loaded:', bot.model_loaded)
print('model_info:', bot.model_info)
def main():
	res = bot.reload_model(model_name='Wizard-Vicuna-7B-Uncensored.Q5_K_M.gguf')
	print(json.dumps(res, default=str, indent=2))
	print('model_loaded:', bot.model_loaded)
	print('model_info:', bot.model_info)

if __name__ == '__main__':
	main()
