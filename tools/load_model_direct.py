#!/usr/bin/env python3
"""
Direct model loader script — calls EchoChatBot.reload_model() in-process
so we can bypass the web UI polling and observe load results synchronously.
"""
import json
import time
from pathlib import Path

import sys
# No dummy injection here — use the real environment packages if available.

from echo.chat_bot import get_chat_bot

MODEL_NAME = 'qwen2.5-7b-instruct-q4_k_m.gguf'

if __name__ == '__main__':
    print(f"Reloading model: {MODEL_NAME}")
    bot = get_chat_bot()
    # tune generation params for a cleaner short response
    bot.set_generation_params(max_tokens=128, temperature=0.2)
    start = time.time()
    result = bot.reload_model(model_name=MODEL_NAME)
    elapsed = time.time() - start
    print(f"Reload finished in {elapsed:.2f}s")
    print(json.dumps(result, indent=2))

    # Print tail of load log
    logs = Path(__file__).parent.parent / 'logs' / 'gguf_load.log'
    print('\nLast gguf_load.log lines:')
    try:
        with open(logs, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-200:]
            print(''.join(lines))
    except Exception as e:
        print('Could not read gguf_load.log:', e)

    # Try a quick chat if the model loaded
    if result.get('model_loaded'):
        try:
            clean_prompt = 'Please summarize deploying a containerized app in three concise steps.'
            resp = bot.chat(clean_prompt)
            print('\nQuick chat response:')
            print(json.dumps(resp, indent=2))
        except Exception as e:
            print('Chat failed:', e)
    else:
        print('Model not loaded; skipping quick chat.')
