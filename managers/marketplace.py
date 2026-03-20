from flask import request, jsonify
import json
import uuid
from datetime import datetime
from pathlib import Path


class MarketplaceManager:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self._ensure_db()

    def _ensure_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            self._save({
                'plugins': [
                    {'id': 'terraform-iac', 'name': 'Terraform IaC', 'version': '1.2.0', 'author': 'MasterChief Team', 'category': 'DevOps', 'description': 'Infrastructure as Code automation with Terraform.', 'installed': True, 'rating': 4.5, 'review_count': 12, 'config': {'default_provider': 'azure', 'state_backend': 'local'}, 'dependencies': []},
                    {'id': 'ansible-config', 'name': 'Ansible Config Management', 'version': '2.0.1', 'author': 'MasterChief Team', 'category': 'Automation', 'description': 'Server configuration management with Ansible playbooks.', 'installed': True, 'rating': 4.2, 'review_count': 8, 'config': {'inventory_path': '/etc/ansible/hosts'}, 'dependencies': []},
                    {'id': 'k8s-deploy', 'name': 'Kubernetes Deployer', 'version': '3.1.0', 'author': 'MasterChief Team', 'category': 'DevOps', 'description': 'Kubernetes deployment automation with Helm charts.', 'installed': True, 'rating': 4.8, 'review_count': 25, 'config': {'default_namespace': 'default', 'context': 'minikube'}, 'dependencies': ['terraform-iac']},
                    {'id': 'prometheus-monitor', 'name': 'Prometheus Monitoring', 'version': '1.5.0', 'author': 'MasterChief Team', 'category': 'Monitoring', 'description': 'Full metrics pipeline with Prometheus and Grafana.', 'installed': False, 'rating': 4.6, 'review_count': 18, 'config': {}, 'dependencies': []},
                    {'id': 'vault-secrets', 'name': 'HashiCorp Vault', 'version': '0.9.0', 'author': 'Community', 'category': 'Security', 'description': 'Integration with HashiCorp Vault for secret management.', 'installed': False, 'rating': 4.0, 'review_count': 6, 'config': {}, 'dependencies': []},
                    {'id': 'jenkins-ci', 'name': 'Jenkins CI Bridge', 'version': '1.0.0', 'author': 'Community', 'category': 'Integration', 'description': 'Bridge MasterChief pipelines with Jenkins CI/CD.', 'installed': False, 'rating': 3.8, 'review_count': 4, 'config': {}, 'dependencies': []},
                    {'id': 'github-actions', 'name': 'GitHub Actions Sync', 'version': '2.1.0', 'author': 'Community', 'category': 'Integration', 'description': 'Sync GitHub Actions workflows with MasterChief pipelines.', 'installed': False, 'rating': 4.3, 'review_count': 14, 'config': {}, 'dependencies': []},
                    {'id': 'sonarqube-scan', 'name': 'SonarQube Scanner', 'version': '1.3.0', 'author': 'Community', 'category': 'Security', 'description': 'Code quality and security scanning with SonarQube.', 'installed': False, 'rating': 4.1, 'review_count': 9, 'config': {}, 'dependencies': []},
                    {'id': 'elk-logging', 'name': 'ELK Stack Logging', 'version': '2.0.0', 'author': 'MasterChief Team', 'category': 'Monitoring', 'description': 'Centralized logging with Elasticsearch, Logstash, and Kibana.', 'installed': False, 'rating': 4.4, 'review_count': 11, 'config': {}, 'dependencies': []},
                    {'id': 'cost-optimizer', 'name': 'Cloud Cost Optimizer', 'version': '1.1.0', 'author': 'Community', 'category': 'DevOps', 'description': 'Analyze and optimize cloud spending.', 'installed': False, 'rating': 3.9, 'review_count': 7, 'config': {}, 'dependencies': []},
                    {'id': 'postgres-manager', 'name': 'PostgreSQL Manager', 'version': '1.0.0', 'author': 'Community', 'category': 'Database', 'description': 'PostgreSQL database management with backups and monitoring.', 'installed': False, 'rating': 4.2, 'review_count': 5, 'config': {}, 'dependencies': []},
                    {'id': 'nginx-proxy', 'name': 'Nginx Proxy Manager', 'version': '1.4.0', 'author': 'Community', 'category': 'Networking', 'description': 'Nginx reverse proxy management with SSL automation.', 'installed': False, 'rating': 4.5, 'review_count': 16, 'config': {}, 'dependencies': []},
                ],
                'reviews': []
            })

    def _load(self):
        try:
            return json.loads(self.db_path.read_text(encoding='utf-8'))
        except Exception:
            return {'plugins': [], 'reviews': []}

    def _save(self, data):
        self.db_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def list_plugins(self, query=None, category=None, installed_only=False):
        d = self._load()
        plugins = d.get('plugins', [])
        if query:
            q = query.lower()
            plugins = [p for p in plugins if q in p.get('name', '').lower() or q in p.get('description', '').lower()]
        if category and category != 'All':
            plugins = [p for p in plugins if p.get('category') == category]
        if installed_only:
            plugins = [p for p in plugins if p.get('installed')]
        return plugins

    def get_plugin(self, pid):
        for p in self._load().get('plugins', []):
            if p['id'] == pid:
                return p
        raise ValueError('Plugin not found')

    def install_plugin(self, pid):
        d = self._load()
        for p in d.get('plugins', []):
            if p['id'] == pid:
                deps = p.get('dependencies', [])
                for dep in deps:
                    dep_plugin = next((x for x in d['plugins'] if x['id'] == dep), None)
                    if dep_plugin and not dep_plugin.get('installed'):
                        raise ValueError(f'Dependency {dep} must be installed first')
                p['installed'] = True
                self._save(d)
                return p
        raise ValueError('Plugin not found')

    def uninstall_plugin(self, pid):
        d = self._load()
        for p in d.get('plugins', []):
            if p['id'] == pid:
                dependents = [x['name'] for x in d['plugins'] if pid in x.get('dependencies', []) and x.get('installed')]
                if dependents:
                    raise ValueError(f'Cannot uninstall: {", ".join(dependents)} depend on this plugin')
                p['installed'] = False
                p['config'] = {}
                self._save(d)
                return p
        raise ValueError('Plugin not found')

    def get_config(self, pid):
        p = self.get_plugin(pid)
        return p.get('config', {})

    def update_config(self, pid, config):
        d = self._load()
        for p in d.get('plugins', []):
            if p['id'] == pid:
                p['config'] = config
                self._save(d)
                return p
        raise ValueError('Plugin not found')

    def get_reviews(self, pid):
        d = self._load()
        return [r for r in d.get('reviews', []) if r.get('plugin_id') == pid]

    def add_review(self, pid, rating, text, author='Anonymous'):
        d = self._load()
        review = {
            'id': str(uuid.uuid4()), 'plugin_id': pid,
            'rating': max(1, min(5, int(rating))), 'text': text,
            'author': author, 'created': datetime.now().isoformat()
        }
        d.setdefault('reviews', []).append(review)
        plugin_reviews = [r for r in d['reviews'] if r.get('plugin_id') == pid]
        for p in d.get('plugins', []):
            if p['id'] == pid:
                p['review_count'] = len(plugin_reviews)
                p['rating'] = round(sum(r['rating'] for r in plugin_reviews) / len(plugin_reviews), 1)
                break
        self._save(d)
        return review


def register_marketplace_module(app, db_path='data/marketplace.json'):
    marketplace_mgr = MarketplaceManager(db_path)

    @app.route('/api/marketplace/plugins', methods=['GET'])
    def api_marketplace_plugins_list():
        try:
            q = request.args.get('q')
            category = request.args.get('category')
            installed = request.args.get('installed', '').lower() == 'true'
            return jsonify({'ok': True, 'result': marketplace_mgr.list_plugins(query=q, category=category, installed_only=installed)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/marketplace/plugins/<pid>', methods=['GET'])
    def api_marketplace_plugins_get(pid):
        try:
            return jsonify({'ok': True, 'result': marketplace_mgr.get_plugin(pid)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 404

    @app.route('/api/marketplace/plugins/<pid>/install', methods=['POST'])
    def api_marketplace_plugins_install(pid):
        try:
            return jsonify({'ok': True, 'result': marketplace_mgr.install_plugin(pid)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/marketplace/plugins/<pid>/uninstall', methods=['POST'])
    def api_marketplace_plugins_uninstall(pid):
        try:
            return jsonify({'ok': True, 'result': marketplace_mgr.uninstall_plugin(pid)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/marketplace/plugins/<pid>/update', methods=['POST'])
    def api_marketplace_plugins_update(pid):
        try:
            return jsonify({'ok': True, 'result': marketplace_mgr.get_plugin(pid)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/marketplace/plugins/<pid>/config', methods=['GET'])
    def api_marketplace_plugins_config_get(pid):
        try:
            return jsonify({'ok': True, 'result': marketplace_mgr.get_config(pid)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 404

    @app.route('/api/marketplace/plugins/<pid>/config', methods=['PUT'])
    def api_marketplace_plugins_config_update(pid):
        try:
            d = request.get_json(silent=True) or {}
            return jsonify({'ok': True, 'result': marketplace_mgr.update_config(pid, d)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/marketplace/plugins/<pid>/reviews', methods=['GET'])
    def api_marketplace_plugins_reviews_list(pid):
        try:
            return jsonify({'ok': True, 'result': marketplace_mgr.get_reviews(pid)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/marketplace/plugins/<pid>/reviews', methods=['POST'])
    def api_marketplace_plugins_reviews_create(pid):
        try:
            d = request.get_json(silent=True) or {}
            review = marketplace_mgr.add_review(pid, d.get('rating', 5), d.get('text', ''), d.get('author', 'Anonymous'))
            return jsonify({'ok': True, 'result': review})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/marketplace/installed', methods=['GET'])
    def api_marketplace_installed():
        try:
            return jsonify({'ok': True, 'result': marketplace_mgr.list_plugins(installed_only=True)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/marketplace/refresh', methods=['POST'])
    def api_marketplace_refresh():
        try:
            return jsonify({'ok': True, 'result': marketplace_mgr.list_plugins()})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    return marketplace_mgr