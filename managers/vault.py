import json
import uuid
import base64
from datetime import datetime
from pathlib import Path
import hashlib
from flask import request, jsonify

try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None


class VaultManager:
    def __init__(self, db_path, key_path, audit_path):
        self.db_path = Path(db_path)
        self.key_path = Path(key_path)
        self.audit_path = Path(audit_path)
        self._fernet = self._init_encryption()
        self._ensure_db()

    def _init_encryption(self):
        if Fernet is None:
            return None
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        if self.key_path.exists():
            key = self.key_path.read_bytes()
        else:
            key = Fernet.generate_key()
            self.key_path.write_bytes(key)
        return Fernet(key)

    def _encrypt(self, plaintext):
        if self._fernet:
            return self._fernet.encrypt(plaintext.encode()).decode()
        return base64.b64encode(plaintext.encode()).decode()

    def _decrypt(self, ciphertext):
        if self._fernet:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        return base64.b64decode(ciphertext.encode()).decode()

    def _ensure_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            self._save_db({'secrets': []})
        if not self.audit_path.exists():
            self.audit_path.write_text(json.dumps({'entries': []}, indent=2), encoding='utf-8')

    def _load_db(self):
        if Fernet is None:
            return None
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        if self.key_path.exists():
            key = self.key_path.read_bytes()
        else:
            key = Fernet.generate_key()
            self.key_path.write_bytes(key)
        return Fernet(key)

    def _encrypt(self, plaintext):
        if self._fernet:
            return self._fernet.encrypt(plaintext.encode()).decode()
        return base64.b64encode(plaintext.encode()).decode()

    def _decrypt(self, ciphertext):
        if self._fernet:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        return base64.b64decode(ciphertext.encode()).decode()

    def _ensure_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            self._save_db({'secrets': []})
        if not self.audit_path.exists():
            self.audit_path.write_text(json.dumps({'entries': []}, indent=2), encoding='utf-8')

    def _load_db(self):
        try:
            return json.loads(self.db_path.read_text(encoding='utf-8'))
        except Exception:
            return {'secrets': []}

    def _save_db(self, data):
        self.db_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def _audit(self, user, action, secret_name, details=''):
        try:
            d = json.loads(self.audit_path.read_text(encoding='utf-8')) if self.audit_path.exists() else {'entries': []}
        except Exception:
            d = {'entries': []}
        d['entries'].append({
            'id': str(uuid.uuid4()), 'timestamp': datetime.now().isoformat(),
            'user': user, 'action': action, 'secret_name': secret_name, 'details': details
        })
        if len(d['entries']) > 2000:
            d['entries'] = d['entries'][-2000:]
        self.audit_path.write_text(json.dumps(d, indent=2), encoding='utf-8')

    def list_secrets(self):
        d = self._load_db()
        return [{k: v for k, v in s.items() if k != 'encrypted_value' and k != 'versions'} for s in d.get('secrets', [])]

    def create_secret(self, name, value, secret_type='other', rotation_days=0):
        d = self._load_db()
        if any(s['name'] == name for s in d.get('secrets', [])):
            raise ValueError(f'Secret {name} already exists')
        secret = {
            'id': str(uuid.uuid4()), 'name': name, 'type': secret_type,
            'encrypted_value': self._encrypt(value),
            'rotation_days': rotation_days,
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat(),
            'last_accessed': None,
            'versions': [{'version': 1, 'timestamp': datetime.now().isoformat(), 'encrypted_value': self._encrypt(value)}]
        }
        d.setdefault('secrets', []).append(secret)
        self._save_db(d)
        self._audit('system', 'created', name, f'Secret {name} created (type={secret_type})')
        return {k: v for k, v in secret.items() if k != 'encrypted_value' and k != 'versions'}

    def get_secret(self, sid, user='system'):
        d = self._load_db()
        for s in d.get('secrets', []):
            if s['id'] == sid:
                s['last_accessed'] = datetime.now().isoformat()
                self._save_db(d)
                self._audit(user, 'accessed', s['name'])
                return {
                    'id': s['id'], 'name': s['name'], 'type': s['type'],
                    'value': self._decrypt(s['encrypted_value']),
                    'rotation_days': s.get('rotation_days', 0),
                    'created': s['created'], 'updated': s['updated'],
                    'last_accessed': s['last_accessed']
                }
        raise ValueError('Secret not found')

    def update_secret(self, sid, value=None, rotation_days=None):
        d = self._load_db()
        for s in d.get('secrets', []):
            if s['id'] == sid:
                if value is not None:
                    ver = len(s.get('versions', [])) + 1
                    s.setdefault('versions', []).append({
                        'version': ver, 'timestamp': datetime.now().isoformat(),
                        'encrypted_value': self._encrypt(value)
                    })
                    s['encrypted_value'] = self._encrypt(value)
                    s['updated'] = datetime.now().isoformat()
                if rotation_days is not None:
                    s['rotation_days'] = rotation_days
                self._save_db(d)
                self._audit('system', 'updated', s['name'])
                return {k: v for k, v in s.items() if k != 'encrypted_value' and k != 'versions'}
        raise ValueError('Secret not found')

    def delete_secret(self, sid):
        d = self._load_db()
        name = next((s['name'] for s in d.get('secrets', []) if s['id'] == sid), 'unknown')
        d['secrets'] = [s for s in d.get('secrets', []) if s['id'] != sid]
        self._save_db(d)
        self._audit('system', 'deleted', name)

    def get_versions(self, sid):
        d = self._load_db()
        for s in d.get('secrets', []):
            if s['id'] == sid:
                return [{'version': v['version'], 'timestamp': v['timestamp']} for v in s.get('versions', [])]
        return []

    def get_audit_log(self, limit=100):
        try:
            d = json.loads(self.audit_path.read_text(encoding='utf-8'))
        except Exception:
            d = {'entries': []}
        return list(reversed(d.get('entries', [])))[:limit]

    def check_rotation(self):
        d = self._load_db()
        due = []
        now = datetime.now()
        for s in d.get('secrets', []):
            rd = s.get('rotation_days', 0)
            if rd > 0:
                updated = datetime.fromisoformat(s['updated'])
                days_since = (now - updated).days
                status = 'overdue' if days_since > rd else ('due_soon' if days_since > rd * 0.8 else 'ok')
                due.append({'id': s['id'], 'name': s['name'], 'rotation_days': rd, 'days_since_update': days_since, 'status': status})
        return due


def register_vault_module(app, db_path='data/vault.json', key_path='data/vault.key', audit_path='data/vault_audit.json'):
    print(f"DEBUG: Registering vault module with db_path={db_path}")
    vault_mgr = VaultManager(db_path, key_path, audit_path)
    
    @app.route('/api/vault/secrets', methods=['GET'])
    def api_vault_list():
        try:
            return jsonify({'ok': True, 'result': vault_mgr.list_secrets()})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/vault/secrets', methods=['POST'])
    def api_vault_create():
        try:
            d = request.get_json(silent=True) or {}
            secret = vault_mgr.create_secret(d.get('name', ''), d.get('value', ''), d.get('type', 'other'), d.get('rotation_days', 0))
            return jsonify({'ok': True, 'result': secret})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/vault/secrets/<sid>', methods=['GET'])
    def api_vault_get(sid):
        try:
            return jsonify({'ok': True, 'result': vault_mgr.get_secret(sid)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 404

    @app.route('/api/vault/secrets/<sid>', methods=['PUT'])
    def api_vault_update(sid):
        try:
            d = request.get_json(silent=True) or {}
            secret = vault_mgr.update_secret(sid, value=d.get('value'), rotation_days=d.get('rotation_days'))
            return jsonify({'ok': True, 'result': secret})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/vault/secrets/<sid>', methods=['DELETE'])
    def api_vault_delete(sid):
        try:
            vault_mgr.delete_secret(sid)
            return jsonify({'ok': True})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/vault/secrets/<sid>/versions', methods=['GET'])
    def api_vault_versions(sid):
        try:
            return jsonify({'ok': True, 'result': vault_mgr.get_versions(sid)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/vault/audit', methods=['GET'])
    def api_vault_audit():
        try:
            limit = request.args.get('limit', 100, type=int)
            return jsonify({'ok': True, 'result': vault_mgr.get_audit_log(limit)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/vault/rotation', methods=['GET'])
    def api_vault_rotation():
        try:
            return jsonify({'ok': True, 'result': vault_mgr.check_rotation()})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500
    
    return vault_mgr