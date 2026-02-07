import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from echo.conversation_storage import get_storage

s = get_storage()
meta = s.get_session_meta('default') or {}
if 'personality' in meta:
    print('Removing personality from default session meta')
    meta.pop('personality', None)
    s.set_session_meta('default', meta)
    print('Done')
else:
    print('No personality found for default session')

print('\nNow scanning all session_meta entries and removing any embedded personality keys...')
import sqlite3, json
db = os.path.join(os.path.dirname(__file__), '..', 'data', 'echo_conversations.db')
db = os.path.abspath(db)
if not os.path.exists(db):
    print('No DB found at', db)
    sys.exit(0)
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT session_id, meta FROM session_meta")
rows = cur.fetchall()
modified = 0
for sid, meta_json in rows:
    try:
        m = json.loads(meta_json)
    except Exception:
        continue
    if 'personality' in m:
        print('Removing personality for session', sid)
        m.pop('personality', None)
        now = datetime = __import__('datetime').datetime.now().isoformat()
        cur.execute("INSERT INTO session_meta (session_id, meta, updated_at) VALUES (?, ?, ?) ON CONFLICT(session_id) DO UPDATE SET meta = excluded.meta, updated_at = excluded.updated_at", (sid, json.dumps(m), now))
        modified += 1
conn.commit()
conn.close()
print('Done. Modified', modified, 'session_meta entries.')
