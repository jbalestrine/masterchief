import time
import sys

# simple demo script emitting lines for SSE testing
for i in range(1,21):
    print(f"demo line {i}")
    sys.stdout.flush()
    time.sleep(0.8)

print('done')
