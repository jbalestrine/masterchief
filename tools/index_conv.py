import sys
import json
import traceback
from pathlib import Path

# Minimal wrapper to run a single conversation indexing job in a separate process.
# Usage: python tools/index_conv.py <username> <conv_id>

if __name__ == '__main__':
    try:
        username = sys.argv[1]
        conv_id = sys.argv[2]
    except Exception:
        print('Usage: index_conv.py <username> <conv_id>')
        sys.exit(2)

    base = Path(__file__).parent.parent / 'data' / 'conversations'
    texts_file = base / username / f'{conv_id}.texts.json'
    if not texts_file.exists():
        print('texts file not found:', texts_file)
        sys.exit(3)

    try:
        # Import application context lazily to avoid heavy imports at interpreter startup
        from main import embed_mgr, app
        texts = json.loads(texts_file.read_text(encoding='utf-8'))
        embed_mgr.index_conversation(username, conv_id, texts)
        print('indexed', username, conv_id)
    except Exception as e:
        print('indexing failed:', e)
        traceback.print_exc()
        sys.exit(1)
    sys.exit(0)
