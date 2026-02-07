#!/usr/bin/env python3
import requests, time
prompts = [
  "Hello!",
  "Tell me a short Dockerfile for a Python app.",
  "List three steps to deploy a container.",
  "Explain in one sentence: CI/CD.",
  'Generate a one-line JSON: {"ok":true}',
  "What's the weather?",
  "Write a concise 1-sentence summary of a deployment pipeline."
]
for p in prompts:
    try:
        r = requests.post('http://127.0.0.1:8080/api/echo/chat', json={'message':p,'debug':True}, timeout=30)
        j = r.json()
        print('PROMPT:', p)
        print('RESPONSE:', j.get('response'))
        if j.get('_llm_debug'):
            print('LLM_DEBUG:', j.get('_llm_debug'))
        print('---')
        time.sleep(0.4)
    except Exception as e:
        print('PROMPT:', p)
        print('ERROR:', e)
        print('---')
