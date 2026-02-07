import sys
import json
import subprocess
from pathlib import Path

MODEL = Path(r"c:\Users\Echo\masterchief\models\qwen2.5-7b-instruct-q4_k_m.gguf")
WORKER = Path(r"c:\Users\Echo\masterchief\echo\llm_worker.py")

prompt = (
    "Explain how to create a Kubernetes Deployment and Service for a simple web "
    "application, and include the exact `kubectl` commands to apply and check the rollout."
)


def try_runtime_model(p):
    try:
        from echo.runtime import model_runtime
        model = model_runtime.get_model()
        if model is None:
            print('RUNTIME: no model loaded in runtime loader')
            return False
        # Try `create` interface
        if hasattr(model, 'create'):
            try:
                resp = model.create(prompt=p, max_tokens=512, temperature=0.2)
                if isinstance(resp, dict):
                    choices = resp.get('choices') or []
                    if choices:
                        text = choices[0].get('text') or choices[0].get('content') or ''
                        print('RUNTIME_GENERATION:\n', text)
                        return True
                if hasattr(resp, 'text'):
                    print('RUNTIME_GENERATION:\n', str(resp.text))
                    return True
            except Exception as e:
                print('RUNTIME: create failed:', e)
        # Try callable interface
        try:
            if callable(model):
                out = model(p, max_tokens=512, temperature=0.2)
                if isinstance(out, dict):
                    choices = out.get('choices') or []
                    if choices:
                        print('RUNTIME_GENERATION:\n', choices[0].get('text') or choices[0].get('content'))
                        return True
                if isinstance(out, str):
                    print('RUNTIME_GENERATION:\n', out)
                    return True
        except Exception as e:
            print('RUNTIME: callable generation failed:', e)
        # Try other common methods
        for meth in ('generate', 'chat'):
            if hasattr(model, meth):
                try:
                    fn = getattr(model, meth)
                    try:
                        resp = fn(prompt=p, max_tokens=512, temperature=0.2)
                    except TypeError:
                        resp = fn(p, 512, 0.2)
                    if isinstance(resp, dict):
                        choices = resp.get('choices') or []
                        if choices:
                            print('RUNTIME_GENERATION:\n', choices[0].get('text') or choices[0].get('content'))
                            return True
                    if isinstance(resp, str):
                        print('RUNTIME_GENERATION:\n', resp)
                        return True
                except Exception as e:
                    print(f'RUNTIME: {meth} failed: {e}')
        print('RUNTIME: no usable generation method found on model')
        return False
    except Exception as e:
        print('RUNTIME: import/model access failed:', e)
        return False


if try_runtime_model(prompt):
    sys.exit(0)

# Fallback to worker subprocess if runtime model not available
if not WORKER.exists():
    print('worker script not found:', WORKER)
    sys.exit(2)
if not MODEL.exists():
    print('model not found:', MODEL)
    sys.exit(2)

cmd = [sys.executable, str(WORKER), '--model', str(MODEL), '--max_tokens', '512', '--temperature', '0.2']
try:
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate(prompt, timeout=120)
    print('RET', proc.returncode)
    print('STDERR:\n', err[:2000])
    print('STDOUT:\n', out[:8000])
    try:
        j = json.loads(out)
        print('PARSED TEXT:\n', j.get('text'))
    except Exception:
        print('RAW OUTPUT:\n', out)
except subprocess.TimeoutExpired:
    try:
        proc.kill()
    except Exception:
        pass
    print('timeout')
