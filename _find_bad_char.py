import re, sys

src = open('main.py', 'r', encoding='utf-8-sig').read()

# Find the ECHO_CHAT_TEMPLATE string
m = re.search(r'ECHO_CHAT_TEMPLATE\s*=\s*["\']{{3}}(.*?)["\']{{3}}', src, re.DOTALL)
# Triple-quote search - try literal
start = src.find('ECHO_CHAT_TEMPLATE')
if start == -1:
    print('ECHO_CHAT_TEMPLATE not found'); sys.exit(1)

# Find the triple-quoted value
tq_start = src.find('"""', start)
if tq_start == -1:
    tq_start = src.find("'''", start)
    tq_end = src.find("'''", tq_start + 3)
else:
    tq_end = src.find('"""', tq_start + 3)

if tq_end == -1:
    print('Could not find end of template string'); sys.exit(1)

template = src[tq_start+3:tq_end]
print(f'Template: {len(template)} chars ({tq_start}-{tq_end} in file)')

# UTF-8 encode test
try:
    template.encode('utf-8')
    print('Template encodes OK')
except UnicodeEncodeError as e:
    pos = e.start
    print(f'BAD CHAR at pos {pos}: U+{ord(template[pos]):04X}')
    ctx = template[max(0, pos-100):pos+100]
    print(f'Context:\n{repr(ctx)}')

# Also check entire source
try:
    src.encode('utf-8')
    print('Full file encodes OK')
except UnicodeEncodeError as e:
    pos = e.start
    line = src[:pos].count('\n') + 1
    print(f'Full file BAD CHAR at pos {pos} (line {line}): U+{ord(src[pos]):04X}')
    print(f'Context: {repr(src[max(0,pos-80):pos+80])}')
