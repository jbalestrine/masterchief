import sys
import traceback
from pathlib import Path

MODEL = Path(r"c:\Users\Echo\masterchief\models\qwen2.5-7b-instruct-q4_k_m.gguf")

def main():
    try:
        print('FORCE_LOAD_SCRIPT: starting')
        if not MODEL.exists():
            print('FORCE_LOAD_SCRIPT: model not found:', MODEL)
            return 2
        from echo.runtime import model_runtime
        print('FORCE_LOAD_SCRIPT: loading ->', MODEL)
        model_runtime.load_model(str(MODEL), force=True)
        print('FORCE_LOAD_SCRIPT: MODEL_LOADED')
        return 0
    except Exception:
        traceback.print_exc()
        return 3

if __name__ == '__main__':
    sys.exit(main())
