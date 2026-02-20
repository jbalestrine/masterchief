from flask import request, jsonify
import json
import uuid
from datetime import datetime
from pathlib import Path
import requests


class NotificationManager:
    def __init__(self, db_path, channels_path, rules_path):
        self.db_path = Path(db_path)
        self.channels_path = Path(channels_path)
        self.rules_path = Path(rules_path)
        self._ensure_db()

    def _ensure_db(self):
        for p, default in [
            (self.db_path, {'notifications': []}),
            (self.channels_path, {'channels': [
                {'id': str(uuid.uuid4()), 'name': 'In-App', 'type': 'in_app', 'config': {}, 'enabled': True, 'created': datetime.now().isoformat()}
            ]}),
            (self.rules_path, {'rules': []})
        ]:
            p.parent.mkdir(parents=True, exist_ok=True)
            if not p.exists():
                p.write_text(json.dumps(default, indent=2), encoding='utf-8')

    def _load(self, path):
        try:
            return json.loads(Path(path).read_text(encoding='utf-8'))
        except Exception:
            return {}

    def _save(self, path, data):
        Path(path).write_text(json.dumps(data, indent=2), encoding='utf-8')

    def send(self, title, message, severity='info', source='system'):
        n = {
            'id': str(uuid.uuid4()), 'title': title, 'message': message,
            'severity': severity, 'source': source,
            'read': False, 'timestamp': datetime.now().isoformat()
        }
        d = self._load(self.db_path)
        d.setdefault('notifications', []).insert(0, n)
        if len(d['notifications']) > 500:
            d['notifications'] = d['notifications'][:500]
        self._save(self.db_path, d)
        self._dispatch(n)
        return n

    def list_notifications(self, unread_only=False, severity=None, limit=50):
        d = self._load(self.db_path)
        items = d.get('notifications', [])
        if unread_only:
            items = [i for i in items if not i.get('read')]
        if severity:
            items = [i for i in items if i.get('severity') == severity]
        return items[:limit]

    def unread_count(self):
        d = self._load(self.db_path)
        return sum(1 for n in d.get('notifications', []) if not n.get('read'))

    def mark_read(self, nid):
        d = self._load(self.db_path)
        for n in d.get('notifications', []):
            if n['id'] == nid:
                n['read'] = True
                break
        self._save(self.db_path, d)

    def mark_all_read(self):
        d = self._load(self.db_path)
        for n in d.get('notifications', []):
            n['read'] = True
        self._save(self.db_path, d)

    def delete_notification(self, nid):
        d = self._load(self.db_path)
        d['notifications'] = [n for n in d.get('notifications', []) if n['id'] != nid]
        self._save(self.db_path, d)

    def get_channels(self):
        return self._load(self.channels_path).get('channels', [])

    def add_channel(self, name, ctype, config):
        d = self._load(self.channels_path)
        ch = {'id': str(uuid.uuid4()), 'name': name, 'type': ctype, 'config': config, 'enabled': True, 'created': datetime.now().isoformat()}
        d.setdefault('channels', []).append(ch)
        self._save(self.channels_path, d)
        return ch

    def update_channel(self, cid, updates):
        d = self._load(self.channels_path)
        for ch in d.get('channels', []):
            if ch['id'] == cid:
                ch.update({k: v for k, v in updates.items() if k != 'id'})
                self._save(self.channels_path, d)
                return ch
        raise ValueError('Channel not found')

    def delete_channel(self, cid):
        d = self._load(self.channels_path)
        d['channels'] = [ch for ch in d.get('channels', []) if ch['id'] != cid]
        self._save(self.channels_path, d)

    def test_channel(self, cid):
        channels = self.get_channels()
        ch = next((c for c in channels if c['id'] == cid), None)
        if not ch:
            raise ValueError('Channel not found')
        test_n = {'title': 'Test Notification', 'message': 'This is a test from MasterChief.', 'severity': 'info'}
        return self._dispatch_to_channel(ch, test_n)

    def get_rules(self):
        return self._load(self.rules_path).get('rules', [])

    def add_rule(self, name, event_type, severity_filter, channel_id, active=True):
        d = self._load(self.rules_path)
        rule = {'id': str(uuid.uuid4()), 'name': name, 'event_type': event_type,
                'severity_filter': severity_filter, 'channel_id': channel_id,
                'active': active, 'created': datetime.now().isoformat()}
        d.setdefault('rules', []).append(rule)
        self._save(self.rules_path, d)
        return rule

    def update_rule(self, rid, updates):
        d = self._load(self.rules_path)
        for r in d.get('rules', []):
            if r['id'] == rid:
                r.update({k: v for k, v in updates.items() if k != 'id'})
                self._save(self.rules_path, d)
                return r
        raise ValueError('Rule not found')

    def delete_rule(self, rid):
        d = self._load(self.rules_path)
        d['rules'] = [r for r in d.get('rules', []) if r['id'] != rid]
        self._save(self.rules_path, d)

    def _dispatch(self, notification):
        channels = self.get_channels()
        rules = self.get_rules()
        for rule in rules:
            if not rule.get('active'):
                continue
            if rule.get('severity_filter') not in ('all', notification.get('severity')):
                continue
            ch = next((c for c in channels if c['id'] == rule.get('channel_id')), None)
            if ch and ch.get('enabled'):
                try:
                    self._dispatch_to_channel(ch, notification)
                except Exception:
                    pass

    def _dispatch_to_channel(self, ch, notification):
        ctype = ch.get('type', '')
        cfg = ch.get('config', {})
        payload_text = f"**{notification['title']}**\n{notification['message']}"
        if ctype == 'slack' and cfg.get('webhook_url'):
            requests.post(cfg['webhook_url'], json={'text': payload_text}, timeout=10)
        elif ctype == 'teams' and cfg.get('webhook_url'):
            requests.post(cfg['webhook_url'], json={'@type': 'MessageCard', 'summary': notification['title'], 'sections': [{'text': notification['message']}]}, timeout=10)
        elif ctype == 'discord' and cfg.get('webhook_url'):
            requests.post(cfg['webhook_url'], json={'content': payload_text}, timeout=10)
        elif ctype == 'email':
            try:
                import smtplib
                from email.mime.text import MIMEText
                msg = MIMEText(notification['message'])
                msg['Subject'] = notification['title']
                msg['From'] = cfg.get('from_email', '')
                msg['To'] = cfg.get('to_email', '')
                with smtplib.SMTP(cfg.get('smtp_host', 'localhost'), int(cfg.get('smtp_port', 25))) as s:
                    if cfg.get('smtp_user'):
                        s.login(cfg['smtp_user'], cfg.get('smtp_pass', ''))
                    s.send_message(msg)
            except Exception:
                pass
        return {'ok': True, 'channel': ch['name']}


def register_notification_module(app, db_path='data/notifications.json', channels_path='data/notification_channels.json', rules_path='data/notification_rules.json'):
    notification_mgr = NotificationManager(db_path, channels_path, rules_path)

    @app.route('/api/notifications', methods=['GET'])
    def api_notifications_list():
        try:
            unread = request.args.get('unread', '').lower() == 'true'
            severity = request.args.get('severity')
            return jsonify({'ok': True, 'result': notification_mgr.list_notifications(unread_only=unread, severity=severity)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/notifications/count', methods=['GET'])
    def api_notifications_count():
        try:
            return jsonify({'ok': True, 'result': notification_mgr.unread_count()})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/notifications/<nid>/read', methods=['POST'])
    def api_notifications_read(nid):
        try:
            notification_mgr.mark_read(nid)
            return jsonify({'ok': True})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/notifications/read_all', methods=['POST'])
    def api_notifications_read_all():
        try:
            notification_mgr.mark_all_read()
            return jsonify({'ok': True})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/notifications/<nid>', methods=['DELETE'])
    def api_notifications_delete(nid):
        try:
            notification_mgr.delete_notification(nid)
            return jsonify({'ok': True})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/notifications/channels', methods=['GET'])
    def api_notification_channels_list():
        try:
            return jsonify({'ok': True, 'result': notification_mgr.get_channels()})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/notifications/channels', methods=['POST'])
    def api_notification_channels_create():
        try:
            d = request.get_json(silent=True) or {}
            ch = notification_mgr.add_channel(d.get('name', ''), d.get('type', 'in_app'), d.get('config', {}))
            return jsonify({'ok': True, 'result': ch})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/notifications/channels/<cid>', methods=['PUT'])
    def api_notification_channels_update(cid):
        try:
            d = request.get_json(silent=True) or {}
            ch = notification_mgr.update_channel(cid, d)
            return jsonify({'ok': True, 'result': ch})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/notifications/channels/<cid>', methods=['DELETE'])
    def api_notification_channels_delete(cid):
        try:
            notification_mgr.delete_channel(cid)
            return jsonify({'ok': True})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/notifications/channels/<cid>/test', methods=['POST'])
    def api_notification_channels_test(cid):
        try:
            result = notification_mgr.test_channel(cid)
            return jsonify({'ok': True, 'result': result})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/notifications/rules', methods=['GET'])
    def api_notification_rules_list():
        try:
            return jsonify({'ok': True, 'result': notification_mgr.get_rules()})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/notifications/rules', methods=['POST'])
    def api_notification_rules_create():
        try:
            d = request.get_json(silent=True) or {}
            rule = notification_mgr.add_rule(d.get('name', ''), d.get('event_type', ''), d.get('severity_filter', 'all'), d.get('channel_id', ''), d.get('active', True))
            return jsonify({'ok': True, 'result': rule})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/notifications/rules/<rid>', methods=['PUT'])
    def api_notification_rules_update(rid):
        try:
            d = request.get_json(silent=True) or {}
            rule = notification_mgr.update_rule(rid, d)
            return jsonify({'ok': True, 'result': rule})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/notifications/rules/<rid>', methods=['DELETE'])
    def api_notification_rules_delete(rid):
        try:
            notification_mgr.delete_rule(rid)
            return jsonify({'ok': True})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    return notification_mgr