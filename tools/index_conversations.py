#!/usr/bin/env python3
"""Index all conversations using sentence-transformers and save embeddings.
Run with the project's venv python.
"""
import json
from pathlib import Path
import sys
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
except Exception as e:
    print('Missing packages:', e)
    sys.exit(2)

MODEL_NAME = 'all-MiniLM-L6-v2'
base = Path(__file__).parent.parent / 'data' / 'conversations'
out_base = Path(__file__).parent.parent / 'data' / 'conv_embeddings'
model = SentenceTransformer(MODEL_NAME)
print('Loaded model:', MODEL_NAME)
count = 0
for userdir in sorted(base.iterdir()):
    if not userdir.is_dir():
        continue
    for texts_file in sorted(userdir.glob('*.texts.json')):
        conv_id = texts_file.stem.replace('.texts','') if texts_file.name.endswith('.texts.json') else texts_file.stem
        try:
            texts = json.loads(texts_file.read_text(encoding='utf-8'))
            if not texts:
                print(f'No texts for {userdir.name}/{conv_id}, skipping')
                continue
            print(f'Encoding {userdir.name}/{conv_id} ({len(texts)} items)')
            embs = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
            save_dir = out_base / userdir.name
            save_dir.mkdir(parents=True, exist_ok=True)
            np_path = save_dir / f'{conv_id}.npy'
            meta_path = save_dir / f'{conv_id}.meta.json'
            # save numpy
            np.save(str(np_path), embs)
            meta = {'count': int(embs.shape[0])}
            meta_path.write_text(json.dumps(meta, indent=2), encoding='utf-8')
            print('Saved', np_path)
            count += 1
        except Exception as e:
            print('Failed to index', userdir.name, conv_id, e)
print('Indexed', count, 'conversations')
