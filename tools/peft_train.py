#!/usr/bin/env python3
"""
PEFT/LoRA training wrapper (minimal). This script attempts to run a LoRA training
recipe using Hugging Face `transformers` + `peft` + `datasets`.

Usage (example):
python tools/peft_train.py --model facebook/opt-125m --data data/echo_training/mydata.jsonl --output data/models_output/run1 --epochs 1 --batch_size 8

This script requires:
- transformers
- datasets
- accelerate
- peft
- (optional) bitsandbytes for 8-bit training

The implementation below is intentionally minimal to act as a template. For
large-scale training or QLoRA, adapt the recipe to your infra and GPU setup.
"""
import argparse
import sys
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--model', required=True)
    p.add_argument('--data', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--epochs', type=int, default=1)
    p.add_argument('--batch_size', type=int, default=8)
    p.add_argument('--lr', type=float, default=1e-4)
    p.add_argument('--local_rank', type=int, default=-1)
    args = p.parse_args()

    # Dependency check
    try:
        import torch
        from datasets import load_dataset
        from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
        from peft import get_peft_model, LoraConfig, TaskType
    except Exception as e:
        print('Missing dependencies for PEFT training:', e, file=sys.stderr)
        print('Install with: pip install transformers datasets accelerate peft bitsandbytes', file=sys.stderr)
        sys.exit(2)

    outdir = Path(args.output)
    outdir.mkdir(parents=True, exist_ok=True)

    print('Loading dataset...', file=sys.stderr)
    # assume jsonl with fields `prompt` and `completion` or plain text
    if Path(args.data).suffix in ('.jsonl', '.json'):
        ds = load_dataset('json', data_files=str(args.data), split='train')
    else:
        # fallback: load as text file and wrap lines
        ds = load_dataset('text', data_files=str(args.data), split='train')

    # Build prompts/completions convenience
    if 'prompt' in ds.column_names and 'completion' in ds.column_names:
        def _map_example(ex):
            return {'input_text': ex['prompt'], 'target_text': ex['completion']}
        ds = ds.map(_map_example)
    else:
        # treat each row as a completion and create a simple prompt
        def _map_example2(ex):
            text = ex.get('text') or ex.get(list(ex.keys())[0])
            return {'input_text': 'Provide the requested file content or code.', 'target_text': text}
        ds = ds.map(_map_example2)

    print('Loading tokenizer and model...', file=sys.stderr)
    tokenizer = AutoTokenizer.from_pretrained(args.model, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(args.model)

    # Configure LoRA
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=8,
        lora_alpha=32,
        lora_dropout=0.1
    )
    model = get_peft_model(model, peft_config)

    # Tokenize
    max_length = 1024

    def tokenize(example):
        inputs = tokenizer(example['input_text'], truncation=True, max_length=max_length)
        targets = tokenizer(example['target_text'], truncation=True, max_length=max_length)
        inputs['labels'] = targets['input_ids']
        return inputs

    print('Tokenizing dataset...', file=sys.stderr)
    tok_ds = ds.map(tokenize, batched=True, remove_columns=ds.column_names)

    training_args = TrainingArguments(
        output_dir=str(outdir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        learning_rate=args.lr,
        logging_steps=10,
        save_strategy='epoch',
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tok_ds,
        tokenizer=tokenizer,
    )

    print('Starting training...', file=sys.stderr)
    trainer.train()

    print('Saving model...', file=sys.stderr)
    model.save_pretrained(str(outdir / 'finetuned'))
    print('Done')


if __name__ == '__main__':
    main()
