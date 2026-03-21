"""Dataset helper — convert various file formats to JSONL for Echo training."""

import csv
import json
from pathlib import Path


def convert_file_to_jsonl(src_path: str, dst_path: str) -> int:
    """Convert a source file (JSON, CSV, TXT, YAML) to JSONL format.

    Returns the number of records written.
    """
    src = Path(src_path)
    dst = Path(dst_path)
    dst.parent.mkdir(parents=True, exist_ok=True)

    ext = src.suffix.lower()
    records: list[dict] = []

    if ext == '.jsonl':
        # Already JSONL — just copy
        dst.write_bytes(src.read_bytes())
        return sum(1 for _ in src.open(encoding='utf-8'))

    elif ext == '.json':
        data = json.loads(src.read_text(encoding='utf-8'))
        if isinstance(data, list):
            for item in data:
                records.append(item if isinstance(item, dict) else {'text': str(item)})
        elif isinstance(data, dict):
            records.append(data)
        else:
            records.append({'text': str(data)})

    elif ext == '.csv':
        with src.open(newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(dict(row))

    elif ext in ('.yaml', '.yml'):
        try:
            import yaml
            data = yaml.safe_load(src.read_text(encoding='utf-8'))
            if isinstance(data, list):
                for item in data:
                    records.append(item if isinstance(item, dict) else {'text': str(item)})
            elif isinstance(data, dict):
                records.append(data)
        except ImportError:
            raise RuntimeError('PyYAML is required to convert YAML files')

    elif ext in ('.txt', '.md', '.log'):
        for line in src.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line:
                records.append({'text': line})

    else:
        raise ValueError(f'Unsupported file format: {ext}')

    # Write JSONL
    with dst.open('w', encoding='utf-8') as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')

    return len(records)
