from flask import request, jsonify
import json
import uuid
from datetime import datetime
from pathlib import Path


class CloudProvider:
    def list_resources(self, credentials):
        return []
    def get_resource(self, credentials, resource_id):
        return None
    def start_vm(self, credentials, vm_id):
        return {'ok': True}
    def stop_vm(self, credentials, vm_id):
        return {'ok': True}

class AzureProvider(CloudProvider):
    def list_resources(self, credentials):
        return [
            {'id': 'azure-vm-1', 'name': 'prod-web-01', 'type': 'vm', 'provider': 'azure', 'status': 'running', 'region': 'eastus', 'size': 'Standard_D2s_v3', 'cost_monthly': 70.08, 'created': '2024-01-15'},
            {'id': 'azure-vm-2', 'name': 'prod-api-01', 'type': 'vm', 'provider': 'azure', 'status': 'running', 'region': 'eastus', 'size': 'Standard_D4s_v3', 'cost_monthly': 140.16, 'created': '2024-01-15'},
            {'id': 'azure-stor-1', 'name': 'prodstorage01', 'type': 'storage', 'provider': 'azure', 'status': 'running', 'region': 'eastus', 'size': 'Standard_LRS', 'cost_monthly': 21.84, 'created': '2024-02-01'},
            {'id': 'azure-db-1', 'name': 'prod-sql-01', 'type': 'database', 'provider': 'azure', 'status': 'running', 'region': 'eastus', 'size': 'GP_Gen5_2', 'cost_monthly': 295.20, 'created': '2024-01-20'},
            {'id': 'azure-net-1', 'name': 'prod-vnet', 'type': 'network', 'provider': 'azure', 'status': 'running', 'region': 'eastus', 'size': '10.0.0.0/16', 'cost_monthly': 0, 'created': '2024-01-10'},
        ]

class AWSProvider(CloudProvider):
    def list_resources(self, credentials):
        return [
            {'id': 'aws-vm-1', 'name': 'staging-web', 'type': 'vm', 'provider': 'aws', 'status': 'running', 'region': 'us-east-1', 'size': 't3.medium', 'cost_monthly': 30.37, 'created': '2024-03-01'},
            {'id': 'aws-vm-2', 'name': 'staging-worker', 'type': 'vm', 'provider': 'aws', 'status': 'stopped', 'region': 'us-east-1', 'size': 't3.large', 'cost_monthly': 0, 'created': '2024-03-01'},
            {'id': 'aws-stor-1', 'name': 'staging-s3-data', 'type': 'storage', 'provider': 'aws', 'status': 'running', 'region': 'us-east-1', 'size': 'S3 Standard', 'cost_monthly': 15.50, 'created': '2024-03-05'},
            {'id': 'aws-db-1', 'name': 'staging-rds', 'type': 'database', 'provider': 'aws', 'status': 'running', 'region': 'us-east-1', 'size': 'db.t3.medium', 'cost_monthly': 52.56, 'created': '2024-03-10'},
        ]

class GCPProvider(CloudProvider):
    def list_resources(self, credentials):
        return [
            {'id': 'gcp-vm-1', 'name': 'dev-instance-1', 'type': 'vm', 'provider': 'gcp', 'status': 'running', 'region': 'us-central1', 'size': 'e2-medium', 'cost_monthly': 24.27, 'created': '2024-04-01'},
            {'id': 'gcp-stor-1', 'name': 'dev-bucket', 'type': 'storage', 'provider': 'gcp', 'status': 'running', 'region': 'us-central1', 'size': 'Standard', 'cost_monthly': 8.50, 'created': '2024-04-05'},
            {'id': 'gcp-db-1', 'name': 'dev-cloudsql', 'type': 'database', 'provider': 'gcp', 'status': 'stopped', 'region': 'us-central1', 'size': 'db-f1-micro', 'cost_monthly': 0, 'created': '2024-04-10'},
        ]

class CloudDashboardManager:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self._providers = {'azure': AzureProvider(), 'aws': AWSProvider(), 'gcp': GCPProvider()}
        self._resource_cache = {}
        self._ensure_db()

    def _ensure_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            self._save({'accounts': [
                {'id': str(uuid.uuid4()), 'name': 'Azure Production', 'provider': 'azure', 'credential_secret_id': '', 'region': 'eastus', 'created': datetime.now().isoformat()},
                {'id': str(uuid.uuid4()), 'name': 'AWS Staging', 'provider': 'aws', 'credential_secret_id': '', 'region': 'us-east-1', 'created': datetime.now().isoformat()},
                {'id': str(uuid.uuid4()), 'name': 'GCP Development', 'provider': 'gcp', 'credential_secret_id': '', 'region': 'us-central1', 'created': datetime.now().isoformat()},
            ]})
        self.refresh()

    def _load(self):
        try:
            return json.loads(self.db_path.read_text(encoding='utf-8'))
        except Exception:
            return {'accounts': []}

    def _save(self, data):
        self.db_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def get_accounts(self):
        return self._load().get('accounts', [])

    def add_account(self, name, provider, credential_secret_id='', region='', subscription_id=None):
        d = self._load()
        acct = {'id': str(uuid.uuid4()), 'name': name, 'provider': provider,
                'credential_secret_id': credential_secret_id, 'region': region,
                'subscription_id': subscription_id or None,
                'created': datetime.now().isoformat()}
        d.setdefault('accounts', []).append(acct)
        self._save(d)
        self.refresh()
        return acct

    def remove_account(self, aid):
        d = self._load()
        d['accounts'] = [a for a in d.get('accounts', []) if a['id'] != aid]
        self._save(d)
        self._resource_cache.pop(aid, None)

    def refresh(self):
        self._resource_cache = {}
        for acct in self.get_accounts():
            provider = self._providers.get(acct['provider'])
            if provider:
                try:
                    self._resource_cache[acct['id']] = provider.list_resources(acct.get('credential_secret_id'))
                except Exception:
                    self._resource_cache[acct['id']] = []

    def get_resources(self, provider=None, rtype=None, status=None):
        all_res = []
        for acct_id, resources in self._resource_cache.items():
            all_res.extend(resources)
        if provider:
            all_res = [r for r in all_res if r.get('provider') == provider]
        if rtype:
            all_res = [r for r in all_res if r.get('type') == rtype]
        if status:
            all_res = [r for r in all_res if r.get('status') == status]
        return all_res

    def get_resource(self, rid):
        for resources in self._resource_cache.values():
            for r in resources:
                if r['id'] == rid:
                    return r
        raise ValueError('Resource not found')

    def start_resource(self, rid):
        for resources in self._resource_cache.values():
            for r in resources:
                if r['id'] == rid:
                    r['status'] = 'running'
                    return r
        raise ValueError('Resource not found')

    def stop_resource(self, rid):
        for resources in self._resource_cache.values():
            for r in resources:
                if r['id'] == rid:
                    r['status'] = 'stopped'
                    r['cost_monthly'] = 0
                    return r
        raise ValueError('Resource not found')

    def get_costs(self):
        costs = {'azure': 0, 'aws': 0, 'gcp': 0, 'total': 0}
        for r in self.get_resources():
            p = r.get('provider', 'other')
            c = r.get('cost_monthly', 0)
            costs[p] = costs.get(p, 0) + c
            costs['total'] += c
        return costs


def register_cloud_module(app, db_path='data/cloud.json'):
    cloud_mgr = CloudDashboardManager(db_path)

    @app.route('/api/cloud/accounts', methods=['GET'])
    def api_cloud_accounts_list():
        try:
            return jsonify({'ok': True, 'result': cloud_mgr.get_accounts()})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/cloud/accounts', methods=['POST'])
    def api_cloud_accounts_create():
        try:
            d = request.get_json(silent=True) or {}
            acct = cloud_mgr.add_account(
                d.get('name', ''),
                d.get('provider', 'azure'),
                d.get('credential_secret_id', ''),
                d.get('region', ''),
                subscription_id=d.get('subscription_id') or None
            )
            return jsonify({'ok': True, 'result': acct})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/cloud/accounts/<aid>', methods=['DELETE'])
    def api_cloud_accounts_delete(aid):
        try:
            cloud_mgr.remove_account(aid)
            return jsonify({'ok': True})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/cloud/resources', methods=['GET'])
    def api_cloud_resources_list():
        try:
            provider = request.args.get('provider')
            rtype = request.args.get('type')
            status = request.args.get('status')
            return jsonify({'ok': True, 'result': cloud_mgr.get_resources(provider=provider, rtype=rtype, status=status)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/cloud/resources/<rid>', methods=['GET'])
    def api_cloud_resources_get(rid):
        try:
            return jsonify({'ok': True, 'result': cloud_mgr.get_resource(rid)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 404

    @app.route('/api/cloud/resources/<rid>/start', methods=['POST'])
    def api_cloud_resources_start(rid):
        try:
            return jsonify({'ok': True, 'result': cloud_mgr.start_resource(rid)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/cloud/resources/<rid>/stop', methods=['POST'])
    def api_cloud_resources_stop(rid):
        try:
            return jsonify({'ok': True, 'result': cloud_mgr.stop_resource(rid)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/cloud/costs', methods=['GET'])
    def api_cloud_costs():
        try:
            return jsonify({'ok': True, 'result': cloud_mgr.get_costs()})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/cloud/refresh', methods=['POST'])
    def api_cloud_refresh():
        try:
            cloud_mgr.refresh()
            return jsonify({'ok': True})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    return cloud_mgr