#!/usr/bin/env python3
"""
qwen_inspircd/run.py

Load a local GGUF Qwen model via llama-cpp-python and post generated text
to an IRC channel using the MasterChief bridge endpoint. Supports streaming
token-by-token postings to avoid long single messages.

Usage:
  python run.py --session <session> --channel <#chan> [--bridge-token <token>] [--model <path>] [--prompt "..."]

Environment:
  MC_SERVER_URL - optional base URL for the MasterChief server (defaults to http://127.0.0.1:8080)
"""

import argparse
import json
import os
import sys
import time

MODEL_DEFAULT = r"C:\Users\Echo\masterchief\models\Qwen-7b\qwen2.5-7b-instruct-q4_k_m.gguf"
SERVER_URL = os.environ.get('MC_SERVER_URL', 'http://127.0.0.1:8080')

try:
    import requests
except Exception:
    print('[ERROR] missing dependency: requests (pip install requests)')
    sys.exit(2)


def post_message(server, session, channel, message, bridge_token=None):
    url = server.rstrip('/') + '/irc/bridge_send'
    headers = {'Content-Type': 'application/json'}
    if bridge_token:
        headers['X-BRIDGE-TOKEN'] = bridge_token
    payload = {'session': session, 'channel': channel, 'message': message}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        try:
            j = r.json()
        except Exception:
            j = None
        return r.status_code, j
    except Exception as e:
        return None, {'error': str(e)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--session', required=True)
    p.add_argument('--channel', required=True)
    p.add_argument('--bridge-token', default=None)
    p.add_argument('--model', default=MODEL_DEFAULT)
    p.add_argument('--server', default=SERVER_URL)
    p.add_argument('--max-tokens', type=int, default=256)
    p.add_argument('--prompt', default=None, help='Optional prompt to use instead of the default')
    p.add_argument('--no-stream', dest='stream', action='store_false', help='Disable streaming output')
    p.add_argument('--stream', dest='stream', action='store_true', help='Enable streaming output (default)')
    p.set_defaults(stream=True)
    args = p.parse_args()

    model_path = args.model
    if not os.path.exists(model_path):
        print(f"[ERROR] model not found at: {model_path}")
        print("Please check the path or pass --model <path>")
        sys.exit(3)

    try:
        from llama_cpp import Llama
    except Exception as e:
        print('[ERROR] llama_cpp (llama-cpp-python) not available: {}'.format(e))
        print('Install with: pip install llama-cpp-python and ensure llama.cpp backend is built and accessible')
        sys.exit(4)

    print('[INFO] loading model: {}'.format(model_path))
    try:
        llm = Llama(model_path=model_path)
    except Exception as e:
        print('[ERROR] failed to load model: {}'.format(e))
        sys.exit(5)

    print('[INFO] model loaded')

    if args.prompt:
        prompt = args.prompt
    else:
        prompt = (
            "You are a helpful IRC assistant in a channel. Provide a short, friendly reply to the user's message.\n"
            "Keep it concise and suitable for posting to an IRC channel."
        )

    print('[INFO] generating reply...')

    # Determine bridge token: prefer CLI arg, then environment variables for convenience
    bridge_token = args.bridge_token or os.environ.get('MC_BRIDGE_TOKEN') or os.environ.get('BRIDGE_TOKEN')
    if bridge_token:
        print(f"[INFO] using bridge token from {'--bridge-token' if args.bridge_token else 'env'}")

    # streaming generation
    if args.stream:
        try:
            # Use llama_cpp's callable interface which supports streaming via `stream=True`.
            gen = llm(prompt, max_tokens=args.max_tokens, temperature=0.7, stream=True)
        except Exception as e:
            print('[ERROR] streaming API not available: {}'.format(e))
            sys.exit(6)

        pending = ''
        last_send = time.time()
        try:
            for chunk in gen:
                token = ''
                if isinstance(chunk, dict):
                    choices = chunk.get('choices') if isinstance(chunk.get('choices', None), list) else None
                    if choices:
                        c0 = choices[0]
                        if isinstance(c0, dict):
                            token = c0.get('delta') or c0.get('text') or c0.get('content') or ''
                            if isinstance(token, dict):
                                token = token.get('content') or ''
                        else:
                            token = str(c0)
                    else:
                        token = chunk.get('token') or chunk.get('text') or chunk.get('content') or ''
                elif isinstance(chunk, str):
                    token = chunk
                else:
                    token = str(chunk)

                if not token:
                    continue

                # print to stdout for server logs/stream
                print(token, end='', flush=True)

                pending += token
                now = time.time()
                if len(pending) >= 160 or (now - last_send) > 1.0:
                    try:
                        status, j = post_message(args.server, args.session, args.channel, pending, bridge_token)
                        print('\n[INFO] bridge partial status={} resp={}'.format(status, json.dumps(j) if j else j))
                    except Exception as e:
                        print('\n[ERROR] bridge partial failed: {}'.format(e))
                    pending = ''
                    last_send = now

            if pending:
                try:
                    status, j = post_message(args.server, args.session, args.channel, pending, bridge_token)
                    print('\n[INFO] bridge partial status={} resp={}'.format(status, json.dumps(j) if j else j))
                except Exception as e:
                    print('\n[ERROR] bridge final failed: {}'.format(e))

        except Exception as e:
            print('\n[ERROR] streaming generation failed: {}'.format(e))
            sys.exit(6)

        print('\n[INFO] streaming generation complete')

    else:
        try:
            resp = llm(prompt, max_tokens=args.max_tokens, temperature=0.7)
            text = ''
            if isinstance(resp, dict):
                # Newer llama_cpp returns a dict with 'choices' like OpenAI-style responses
                choices = resp.get('choices') or []
                if choices and isinstance(choices, list):
                    # choice may contain 'text' or 'content'
                    text = choices[0].get('text') or choices[0].get('content') or ''
                else:
                    text = str(resp)
            else:
                text = str(resp)
        except Exception as e:
            print('[ERROR] generation failed: {}'.format(e))
            sys.exit(6)

        text = (text or '').strip()
        if not text:
            print('[ERROR] model returned no text')
            sys.exit(7)

        for line in text.splitlines():
            print(line)
            sys.stdout.flush()
            time.sleep(0.02)

        status, j = post_message(args.server, args.session, args.channel, text, args.bridge_token)
        print('[INFO] bridge_post status={} response={}'.format(status, json.dumps(j) if j else j))

    print('[DONE]')


if __name__ == '__main__':
    main()
