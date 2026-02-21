from flask import request, jsonify
import json
import uuid
from datetime import datetime
from pathlib import Path


class MemoryManager:
    def __init__(self, memories_path, index_path):
        self.memories_path = Path(memories_path)
        self.index_path = Path(index_path)
        self._ensure_db()

    def _ensure_db(self):
        self.memories_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.memories_path.exists():
            self.memories_path.touch()
        if not self.index_path.exists():
            self.index_path.write_text(json.dumps({'topics': {}, 'entities': {}, 'pinned': []}, indent=2), encoding='utf-8')

    def _load_all(self):
        memories = []
        if self.memories_path.exists():
            for line in self.memories_path.read_text(encoding='utf-8').strip().split('\n'):
                if line.strip():
                    try:
                        memories.append(json.loads(line))
                    except Exception:
                        pass
        return memories

    def _save_all(self, memories):
        self.memories_path.write_text('\n'.join(json.dumps(m) for m in memories) + '\n' if memories else '', encoding='utf-8')

    def _load_index(self):
        try:
            return json.loads(self.index_path.read_text(encoding='utf-8'))
        except Exception:
            return {'topics': {}, 'entities': {}, 'pinned': []}

    def _save_index(self, idx):
        self.index_path.write_text(json.dumps(idx, indent=2), encoding='utf-8')

    def _update_index(self, memory):
        idx = self._load_index()
        for t in memory.get('topics', []):
            idx['topics'][t] = idx['topics'].get(t, 0) + 1
        for e in memory.get('entities', []):
            idx['entities'][e] = idx['entities'].get(e, 0) + 1
        if memory.get('pinned'):
            if memory['id'] not in idx['pinned']:
                idx['pinned'].append(memory['id'])
        self._save_index(idx)

    def add_memory(self, content, topics=None, entities=None, source='manual', importance=0.5):
        memory = {
            'id': str(uuid.uuid4()), 'content': content,
            'topics': [t.strip() for t in (topics or []) if t.strip()],
            'entities': [e.strip() for e in (entities or []) if e.strip()],
            'source': source, 'importance': max(0.0, min(1.0, float(importance))),
            'created': datetime.now().isoformat(), 'accessed_count': 0,
            'pinned': False, 'decay_factor': 1.0
        }
        with open(self.memories_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(memory) + '\n')
        self._update_index(memory)
        return memory

    def get_all(self, topic=None, pinned_only=False, query=None):
        memories = self._load_all()
        if topic:
            memories = [m for m in memories if topic in m.get('topics', [])]
        if pinned_only:
            memories = [m for m in memories if m.get('pinned')]
        if query:
            q = query.lower()
            memories = [m for m in memories if q in m.get('content', '').lower() or any(q in t.lower() for t in m.get('topics', []))]
        return list(reversed(memories))

    def get_memory(self, mid):
        for m in self._load_all():
            if m['id'] == mid:
                return m
        return None

    def update_memory(self, mid, updates):
        memories = self._load_all()
        for m in memories:
            if m['id'] == mid:
                for k, v in updates.items():
                    if k not in ('id', 'created'):
                        m[k] = v
                self._save_all(memories)
                return m
        raise ValueError('Memory not found')

    def delete_memory(self, mid):
        memories = self._load_all()
        memories = [m for m in memories if m['id'] != mid]
        self._save_all(memories)

    def toggle_pin(self, mid):
        memories = self._load_all()
        for m in memories:
            if m['id'] == mid:
                m['pinned'] = not m.get('pinned', False)
                self._save_all(memories)
                return m
        raise ValueError('Memory not found')

    def search(self, query, limit=20):
        query_terms = query.lower().split()
        results = []
        for m in self._load_all():
            content_lower = m.get('content', '').lower()
            topic_text = ' '.join(m.get('topics', [])).lower()
            entity_text = ' '.join(m.get('entities', [])).lower()
            combined = content_lower + ' ' + topic_text + ' ' + entity_text
            score = sum(1 for term in query_terms if term in combined)
            if score > 0:
                score *= m.get('importance', 0.5) * m.get('decay_factor', 1.0)
                if m.get('pinned'):
                    score *= 1.5
                results.append((score, m))
        results.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in results[:limit]]

    def get_topics(self):
        idx = self._load_index()
        return idx.get('topics', {})

    def get_context_for_conversation(self, message, limit=5):
        return self.search(message, limit=limit)


def register_memory_module(app, memories_path='data/memories.ndjson', index_path='data/memory_index.json'):
    memory_mgr = MemoryManager(memories_path, index_path)

    @app.route('/api/echo/memories', methods=['GET'])
    def api_echo_memories_list():
        try:
            topic = request.args.get('topic')
            q = request.args.get('q')
            pinned = request.args.get('pinned', '').lower() == 'true'
            return jsonify({'ok': True, 'result': memory_mgr.get_all(topic=topic, pinned_only=pinned, query=q)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/echo/memories', methods=['POST'])
    def api_echo_memories_create():
        try:
            d = request.get_json(silent=True) or {}
            topics = d.get('topics', [])
            if isinstance(topics, str):
                topics = [t.strip() for t in topics.split(',') if t.strip()]
            entities = d.get('entities', [])
            if isinstance(entities, str):
                entities = [e.strip() for e in entities.split(',') if e.strip()]
            memory = memory_mgr.add_memory(
                content=d.get('content', ''),
                topics=topics, entities=entities,
                source=d.get('source', 'manual'),
                importance=d.get('importance', 0.5)
            )
            return jsonify({'ok': True, 'result': memory})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/echo/memories/<mid>', methods=['GET'])
    def api_echo_memories_get(mid):
        try:
            m = memory_mgr.get_memory(mid)
            if m:
                return jsonify({'ok': True, 'result': m})
            return jsonify({'ok': False, 'error': 'Not found'}), 404
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/echo/memories/<mid>', methods=['PUT'])
    def api_echo_memories_update(mid):
        try:
            d = request.get_json(silent=True) or {}
            m = memory_mgr.update_memory(mid, d)
            return jsonify({'ok': True, 'result': m})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/echo/memories/<mid>', methods=['DELETE'])
    def api_echo_memories_delete(mid):
        try:
            memory_mgr.delete_memory(mid)
            return jsonify({'ok': True})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/echo/memories/<mid>/pin', methods=['POST'])
    def api_echo_memories_pin(mid):
        try:
            m = memory_mgr.toggle_pin(mid)
            return jsonify({'ok': True, 'result': m})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/echo/memories/search', methods=['GET'])
    def api_echo_memories_search():
        try:
            q = request.args.get('q', '')
            return jsonify({'ok': True, 'result': memory_mgr.search(q)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/echo/memories/topics', methods=['GET'])
    def api_echo_memories_topics():
        try:
            return jsonify({'ok': True, 'result': memory_mgr.get_topics()})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/echo/memories/context', methods=['POST'])
    def api_echo_memories_context():
        try:
            d = request.get_json(silent=True) or {}
            return jsonify({'ok': True, 'result': memory_mgr.get_context_for_conversation(d.get('message', ''))})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    return memory_mgr