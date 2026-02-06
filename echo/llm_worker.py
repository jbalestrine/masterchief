#!/usr/bin/env python3
"""
LLM Worker: runs in a separate process to isolate native GGUF/llama runtimes.
Reads prompt from stdin and prints JSON {"text": "..."} to stdout.
"""
import sys
import os
import json
import argparse
import re
from datetime import datetime
import requests

try:
    from llama_cpp import Llama
    _HAS_LLAMA = True
except Exception:
    Llama = None
    _HAS_LLAMA = False


def generate_with_llama(model_path: str, prompt: str, max_tokens: int, temperature: float):
    try:
        model = Llama(model_path=model_path)
    except Exception as e:
        return None, f"Failed to instantiate Llama: {e}"

    try:
        # Prefer streaming when supported to avoid truncation.
        if hasattr(model, 'create'):
            try:
                # Try streaming interface first
                try:
                    stream = model.create(prompt=prompt, max_tokens=int(max_tokens), temperature=float(temperature), stream=True)
                    parts = []
                    for chunk in stream:
                        # chunk may be dict-like with incremental text
                        try:
                            if isinstance(chunk, dict):
                                choices = chunk.get('choices') or []
                                if choices:
                                    delta = choices[0].get('delta') or choices[0].get('text') or choices[0].get('content')
                                    if isinstance(delta, dict):
                                        delta_text = delta.get('content') or delta.get('text')
                                    else:
                                        delta_text = delta
                                    if delta_text:
                                        parts.append(str(delta_text))
                        except Exception:
                            try:
                                parts.append(str(chunk))
                            except Exception:
                                pass
                                        prompt = sys.stdin.read()

                                        # small helper to sanitize model text before printing
                                        def _sanitize_text(t: str) -> str:
                                            try:
                                                if t is None:
                                                    return ''
                                                # ensure string
                                                s = str(t)
                                                # remove C0 control characters except newline and tab
                                                s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', s)
                                                # collapse very long runs of a single char (e.g., 'aaaa...')
                                                s = re.sub(r'(.)\1{200,}', lambda m: m.group(1) * 200 + '...[truncated]', s)
                                                # limit total length to avoid huge payloads
                                                if len(s) > 20000:
                                                    s = s[:20000] + '\n...[truncated]'
                                                return s
                                            except Exception:
                                                return ''
                    if text:
                        return text, None
                except TypeError:
                    # Stream not supported; fall back to non-streaming create
                    resp = model.create(prompt=prompt, max_tokens=int(max_tokens), temperature=float(temperature))
                                                safe = _sanitize_text(text)
                                                try:
                                                    print(json.dumps({'text': safe}))
                                                except Exception:
                                                    # fallback plain-print
                                                    print('{"text": ""}')
                                                return 0
                        choices = resp.get('choices') or []
                        if choices:
                            text = choices[0].get('text') or choices[0].get('content')
                            if text:
                                            safe = _sanitize_text(text)
                                            try:
                                                print(json.dumps({'text': safe}))
                                            except Exception:
                                                print('{"text": ""}')
                    if hasattr(resp, 'text'):
                        return str(resp.text), None
            except Exception:
                                        out = {'error': err or 'No model available'}
                                        # log error to a simple worker log for debugging
                                        try:
                                            logp = Path(__file__).resolve().parent / 'llm_worker.log'
                                            with open(logp, 'a', encoding='utf-8') as fh:
                                                fh.write(f"[{datetime.utcnow().isoformat()}] ERROR: {out}\n")
                                        except Exception:
                                            pass
                                        print(json.dumps(out))
        # Try generate() API
        if hasattr(model, 'generate'):
            try:
                gen = model.generate(prompt, max_tokens=int(max_tokens), temperature=float(temperature))
                if isinstance(gen, dict):
                    choices = gen.get('choices') or []
                    if choices:
                        text = choices[0].get('text') or choices[0].get('content')
                        if text:
                            return text, None
                if hasattr(gen, 'text'):
                    return str(gen.text), None
            except Exception:
                pass

        # Callable model interface
        if callable(model):
            try:
                out = model(prompt, max_tokens=int(max_tokens), temperature=float(temperature))
                if isinstance(out, dict):
                    choices = out.get('choices') or []
                    if choices:
                        text = choices[0].get('text') or choices[0].get('content')
                        if text:
                            return text, None
                if isinstance(out, str):
                    return out, None
            except Exception:
                pass

    finally:
        try:
            if hasattr(model, 'close'):
                model.close()
        except Exception:
            pass

    return None, 'No usable generation method on Llama binding'


def generate_with_ollama(model: str, prompt: str, max_tokens: int, temperature: float):
    try:
        ollama_url = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
        resp = requests.post(f"{ollama_url}/api/generate", json={'model': model, 'prompt': prompt, 'max_tokens': max_tokens, 'temperature': temperature}, timeout=10)
        if resp.ok:
            data = resp.json()
            text = data.get('text') or data.get('response') or (data.get('choices') and data['choices'][0].get('text'))
            return text, None
        return None, f'Ollama returned {resp.status_code}'
    except Exception as e:
        return None, f'Ollama request failed: {e}'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--model', required=True)
    p.add_argument('--max_tokens', type=int, default=16384)
    p.add_argument('--temperature', type=float, default=0.7)
    args = p.parse_args()

    # Read prompt from stdin
    prompt = sys.stdin.read()

    # Prefer local llama binding
    if _HAS_LLAMA:
        text, err = generate_with_llama(args.model, prompt, args.max_tokens, args.temperature)
        if text:
            print(json.dumps({'text': text}))
            return 0
        # fallthrough to ollama
    
    text, err = generate_with_ollama(args.model, prompt, args.max_tokens, args.temperature)
    if text:
        print(json.dumps({'text': text}))
        return 0

    # If we get here, return error
    out = {'error': err or 'No model available'}
    print(json.dumps(out))
    return 2


if __name__ == '__main__':
    try:
        rc = main()
        sys.exit(rc)
    except Exception as e:
        print(json.dumps({'error': str(e)}))
        sys.exit(3)
