import subprocess
import sys
from pathlib import Path

model = sys.argv[1] if len(sys.argv) > 1 else 'models/Phi-3-mini-4k-instruct-q4.gguf'
prompt = sys.argv[2] if len(sys.argv) > 2 else 'Explain docker deployment in a few sentences.'

worker = Path(__file__).resolve().parent.parent / 'echo' / 'llm_worker.py'
if not worker.exists():
    print('WORKER MISSING:', worker)
    sys.exit(2)

cmd = [sys.executable, str(worker), '--model', str(model), '--max_tokens', '128', '--temperature', '0.2']
print('Running:', cmd)
try:
    proc = subprocess.run(cmd, input=prompt, text=True, capture_output=True, timeout=120)
    print('RETURN CODE:', proc.returncode)
    print('--- STDOUT ---')
    print(proc.stdout)
    print('--- STDERR ---')
    print(proc.stderr)
except Exception as e:
    print('ERROR', e)
    sys.exit(3)
