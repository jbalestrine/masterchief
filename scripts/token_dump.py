import tokenize
from pathlib import Path
f = open('main.py','rb')
tokens = tokenize.tokenize(f.readline)
for tok in tokens:
    if tok.type == tokenize.ENCODING:
        continue
    if 770 <= tok.start[0] <= 820:
        print(tok.start, tokenize.tok_name[tok.type], repr(tok.string))
f.close()
