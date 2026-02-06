import shutil, subprocess, os
print('which az ->', shutil.which('az'))
try:
    p = subprocess.run(['az','--version'], capture_output=True, text=True, timeout=15)
    print('az --version exit', p.returncode)
    out = p.stdout or p.stderr
    print(out.splitlines()[0] if out else '<no output>')
except Exception as e:
    print('az run error', repr(e))
print('\nPATH (truncated):')
print(os.environ.get('PATH')[:2000])
