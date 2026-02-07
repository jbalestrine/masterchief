import sys
import traceback
from pathlib import Path

MODEL = Path(r"c:\Users\Echo\masterchief\models\qwen2.5-7b-instruct-q4_k_m.gguf")

PROMPT = (
    "Provide a concise Kubernetes Deployment and Service YAML for a simple web app, "
    "and list the kubectl commands to apply it and check rollout status."
)

def main():
    try:
        print('FORCE_LOAD_AND_GEN: starting')
        if not MODEL.exists():
            print('MODEL not found:', MODEL)
            return 2
        from echo.runtime import model_runtime
        print('FORCE_LOAD_AND_GEN: loading model')
        model_runtime.load_model(str(MODEL), force=True)
        print('FORCE_LOAD_AND_GEN: getting model')
        m = model_runtime.get_model()
        if m is None:
            print('Model not available after load')
            return 3
        # Try create
        try:
            if hasattr(m, 'create'):
                print('Using create()')
                r = m.create(prompt=PROMPT, max_tokens=512, temperature=0.2)
                print('RESPONSE (create):', r)
                return 0
        except Exception as e:
            print('create() failed:', e)
        # Try callable
        try:
            if callable(m):
                print('Using callable model')
                out = m(PROMPT, max_tokens=512, temperature=0.2)
                print('RESPONSE (callable):', out)
                return 0
        except Exception as e:
            print('callable failed:', e)
        # Try generate/chat
        for meth in ('generate','chat'):
            if hasattr(m, meth):
                try:
                    fn = getattr(m, meth)
                    try:
                        resp = fn(prompt=PROMPT, max_tokens=512, temperature=0.2)
                    except TypeError:
                        resp = fn(PROMPT, 512, 0.2)
                    print(f'Response ({meth}):', resp)
                    return 0
                except Exception as e:
                    print(f'{meth} failed:', e)
        print('No generation method produced output')
        return 4
    except Exception:
        traceback.print_exc()
        return 5

if __name__ == '__main__':
    sys.exit(main())
