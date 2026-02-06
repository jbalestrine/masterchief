#!/usr/bin/env python3
"""
Dataset helpers to convert uploaded resource files into JSONL training examples.
This is intended to help create simple prompt/completion pairs for teaching the
model about file contents, Terraform modules, ARM templates, etc.

Example transformation strategy (simple):
- For a file `module/main.tf`, create an example where the prompt asks for the
  contents of the file and the completion is the file text. This teaches the
  model to reproduce and explain examples.

For better results, curate positive examples with instruction-style prompts.
"""
import json
from pathlib import Path
import argparse

p = argparse.ArgumentParser()
p.add_argument('--resource', required=True, help='Path to resource file to convert')
p.add_argument('--out', required=True, help='Output JSONL path')
args = p.parse_args()

res = Path(args.resource)
out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)

if not res.exists():
    print('Resource file not found:', res)
    raise SystemExit(2)

text = res.read_text(encoding='utf-8', errors='ignore')

# Create a simple instruction-style example
prompt = f"You are an assistant that knows how to write infrastructure code.\nUser: Provide the full contents of the file named {res.name}.\nAssistant:" 
completion = '\n' + text.strip() + '\n'

example = {'prompt': prompt, 'completion': completion}
with open(out, 'w', encoding='utf-8') as f:
    f.write(json.dumps(example) + '\n')

print('Wrote', out)
