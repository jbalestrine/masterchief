#!/usr/bin/env python3
import sys
import json
import traceback
from pathlib import Path


def _load_llama(model_path):
    try:
        from llama_cpp import Llama
        try:
            llm = Llama(model_path=model_path)
        except TypeError:
            llm = Llama(model=model_path)
        return llm, None
    except Exception as e:
        return None, str(e)


def _generate_from_llm(llm, prompt, max_tokens=256, temperature=0.7):
    resp = None
    for meth in ('create', 'generate', '__call__', 'chat'):
        if hasattr(llm, meth):
            try:
                fn = getattr(llm, meth)
                try:
                    resp = fn(prompt=prompt, max_tokens=max_tokens, temperature=temperature)
                except TypeError:
                    try:
                        resp = fn(prompt, max_tokens, temperature)
                    except Exception:
                        continue
                break
            except Exception:
                continue
    # extract text
    text = ''
    try:
        if isinstance(resp, dict):
            choices = resp.get('choices') or []
            if choices:
                first = choices[0]
                text = (first.get('message') or {}).get('content') or first.get('text') or ''
        elif hasattr(resp, 'choices'):
            first = resp.choices[0]
            if hasattr(first, 'message') and getattr(first.message, 'content', None):
                text = str(first.message.content)
            elif hasattr(first, 'text'):
                text = str(first.text)
        elif isinstance(resp, str):
            text = resp
        else:
            text = str(resp)
    except Exception:
        text = ''
    return (text or '').strip()


def main():
    llm = None
    current_model = None
    # run as a simple line-oriented JSON server on stdin/stdout
    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except Exception as e:
            out = {'error': f'failed to parse JSON: {e}'}
            print(json.dumps(out), flush=True)
            continue
        # special commands
        cmd = data.get('cmd')
        if cmd == 'shutdown':
            try:
                if llm is not None and hasattr(llm, 'close'):
                    try:
                        llm.close()
                    except Exception:
                        pass
            except Exception:
                pass
            print(json.dumps({'status': 'shutdown'}), flush=True)
            break
        model_path = data.get('model_path')
        prompt = data.get('prompt')
        max_tokens = int(data.get('max_tokens', 256))
        temperature = float(data.get('temperature', 0.7))
        if model_path and (current_model is None or str(model_path) != str(current_model)):
            llm, err = _load_llama(model_path)
            if llm is None:
                print(json.dumps({'error': f'failed to load model: {err}'}), flush=True)
                current_model = None
                continue
            current_model = model_path
        if llm is None:
            print(json.dumps({'error': 'no model loaded'}), flush=True)
            continue
        if not prompt:
            print(json.dumps({'error': 'prompt required'}), flush=True)
            continue
        try:
            text = _generate_from_llm(llm, prompt, max_tokens=max_tokens, temperature=temperature)
            print(json.dumps({'text': text}), flush=True)
        except Exception as e:
            tb = traceback.format_exc()
            print(json.dumps({'error': str(e), 'traceback': tb}), flush=True)


if __name__ == '__main__':
    main()
