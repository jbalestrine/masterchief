from flask import request, jsonify
import json
import uuid
import threading
import subprocess
from datetime import datetime
from pathlib import Path


PIPELINE_RUNS = {}

class PipelineManager:
    def __init__(self, db_path, runs_path):
        self.db_path = Path(db_path)
        self.runs_path = Path(runs_path)
        self._ensure_db()

    def _ensure_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        for p, default in [(self.db_path, {'pipelines': []}), (self.runs_path, {'runs': []})]:
            if not p.exists():
                p.write_text(json.dumps(default, indent=2), encoding='utf-8')

    def _load(self):
        try:
            return json.loads(self.db_path.read_text(encoding='utf-8'))
        except Exception:
            return {'pipelines': []}

    def _save(self, data):
        self.db_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def _load_runs(self):
        try:
            return json.loads(self.runs_path.read_text(encoding='utf-8'))
        except Exception:
            return {'runs': []}

    def _save_runs(self, data):
        self.runs_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def list_pipelines(self):
        return self._load().get('pipelines', [])

    def get_pipeline(self, pid):
        for p in self._load().get('pipelines', []):
            if p['id'] == pid:
                return p
        raise ValueError('Pipeline not found')

    def create_pipeline(self, name, description=''):
        d = self._load()
        pipeline = {
            'id': str(uuid.uuid4()), 'name': name, 'description': description,
            'stages': [], 'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat()
        }
        d.setdefault('pipelines', []).append(pipeline)
        self._save(d)
        return pipeline

    def update_pipeline(self, pid, updates):
        d = self._load()
        for p in d.get('pipelines', []):
            if p['id'] == pid:
                for k, v in updates.items():
                    if k not in ('id', 'created'):
                        p[k] = v
                p['updated'] = datetime.now().isoformat()
                self._save(d)
                return p
        raise ValueError('Pipeline not found')

    def delete_pipeline(self, pid):
        d = self._load()
        d['pipelines'] = [p for p in d.get('pipelines', []) if p['id'] != pid]
        self._save(d)

    def execute_pipeline(self, pid):
        pipeline = self.get_pipeline(pid)
        run = {
            'id': str(uuid.uuid4()), 'pipeline_id': pid,
            'pipeline_name': pipeline['name'], 'status': 'running',
            'started': datetime.now().isoformat(), 'finished': None,
            'stages': [], 'log': []
        }
        PIPELINE_RUNS[run['id']] = run
        t = threading.Thread(target=self._run_pipeline, args=(run, pipeline), daemon=True)
        t.start()
        return run

    def _run_pipeline(self, run, pipeline):
        try:
            for stage in sorted(pipeline.get('stages', []), key=lambda s: s.get('order', 0)):
                stage_run = {
                    'stage_id': stage['id'], 'name': stage.get('name', 'Stage'),
                    'status': 'running', 'started': datetime.now().isoformat(),
                    'finished': None, 'steps': []
                }
                run['stages'].append(stage_run)
                run['log'].append(f"[{datetime.now().isoformat()}] Starting stage: {stage.get('name')}")
                for step in stage.get('steps', []):
                    step_run = self._execute_step(step, run)
                    stage_run['steps'].append(step_run)
                    if step_run['status'] == 'failed':
                        stage_run['status'] = 'failed'
                        stage_run['finished'] = datetime.now().isoformat()
                        run['status'] = 'failed'
                        run['finished'] = datetime.now().isoformat()
                        run['log'].append(f"[{datetime.now().isoformat()}] Pipeline FAILED at stage: {stage.get('name')}")
                        self._persist_run(run)
                        return
                stage_run['status'] = 'completed'
                stage_run['finished'] = datetime.now().isoformat()
            run['status'] = 'completed'
            run['finished'] = datetime.now().isoformat()
            run['log'].append(f"[{datetime.now().isoformat()}] Pipeline completed successfully")
        except Exception as e:
            run['status'] = 'failed'
            run['finished'] = datetime.now().isoformat()
            run['log'].append(f"[{datetime.now().isoformat()}] Pipeline error: {str(e)}")
        self._persist_run(run)

    def _execute_step(self, step, run):
        step_run = {
            'step_id': step.get('id', str(uuid.uuid4())),
            'name': step.get('name', 'Step'), 'type': step.get('type', 'custom_command'),
            'status': 'running', 'started': datetime.now().isoformat(),
            'output': '', 'finished': None
        }
        run['log'].append(f"[{datetime.now().isoformat()}] Running step: {step.get('name')} (type={step.get('type')})")
        try:
            cfg = step.get('config', {})
            cmd = None
            cwd = cfg.get('working_dir') or None
            if step.get('type') == 'script':
                cmd = f"{cfg.get('script_path', '')} {cfg.get('args', '')}".strip()
            elif step.get('type') == 'docker_build':
                cmd = f"docker build -t {cfg.get('image_tag', 'latest')} -f {cfg.get('dockerfile_path', 'Dockerfile')} {cfg.get('context_dir', '.')}"
            elif step.get('type') in ('terraform_apply', 'terraform_plan'):
                action = 'apply -auto-approve' if step['type'] == 'terraform_apply' else 'plan'
                var_file = f"-var-file={cfg['var_file']}" if cfg.get('var_file') else ''
                cmd = f"terraform {action} {var_file}".strip()
            elif step.get('type') == 'test_run':
                cmd = cfg.get('test_command', 'echo No test command')
            elif step.get('type') == 'deploy':
                cmd = f"echo Deploying to {cfg.get('target', 'unknown')} with strategy {cfg.get('strategy', 'rolling')}"
            elif step.get('type') == 'custom_command':
                cmd = cfg.get('command', 'echo hello')
            else:
                cmd = f"echo Unknown step type: {step.get('type')}"
            if cmd:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True,
                    timeout=int(cfg.get('timeout', 300)), cwd=cwd
                )
                step_run['output'] = result.stdout + result.stderr
                step_run['status'] = 'completed' if result.returncode == 0 else 'failed'
            else:
                step_run['status'] = 'completed'
                step_run['output'] = 'No command to run'
        except subprocess.TimeoutExpired:
            step_run['status'] = 'failed'
            step_run['output'] = 'Step timed out'
        except Exception as e:
            step_run['status'] = 'failed'
            step_run['output'] = str(e)
        step_run['finished'] = datetime.now().isoformat()
        return step_run

    def _persist_run(self, run):
        d = self._load_runs()
        d.setdefault('runs', []).insert(0, run)
        if len(d['runs']) > 100:
            d['runs'] = d['runs'][:100]
        self._save_runs(d)

    def get_run(self, rid):
        if rid in PIPELINE_RUNS:
            return PIPELINE_RUNS[rid]
        d = self._load_runs()
        for r in d.get('runs', []):
            if r['id'] == rid:
                return r
        raise ValueError('Run not found')

    def get_runs(self, pipeline_id=None, limit=50):
        runs = list(PIPELINE_RUNS.values())
        d = self._load_runs()
        for r in d.get('runs', []):
            if r['id'] not in PIPELINE_RUNS:
                runs.append(r)
        if pipeline_id:
            runs = [r for r in runs if r.get('pipeline_id') == pipeline_id]
        runs.sort(key=lambda r: r.get('started', ''), reverse=True)
        return runs[:limit]

    def cancel_run(self, rid):
        if rid in PIPELINE_RUNS:
            PIPELINE_RUNS[rid]['status'] = 'cancelled'
            PIPELINE_RUNS[rid]['finished'] = datetime.now().isoformat()
            return PIPELINE_RUNS[rid]
        raise ValueError('Run not found or already finished')


def register_pipeline_module(app, db_path='data/pipelines.json', runs_path='data/pipeline_runs.json'):
    pipeline_mgr = PipelineManager(db_path, runs_path)

    @app.route('/api/pipelines', methods=['GET'])
    def api_pipelines_list():
        try:
            return jsonify({'ok': True, 'result': pipeline_mgr.list_pipelines()})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/pipelines', methods=['POST'])
    def api_pipelines_create():
        try:
            d = request.get_json(silent=True) or {}
            pipeline = pipeline_mgr.create_pipeline(d.get('name', 'New Pipeline'), d.get('description', ''))
            return jsonify({'ok': True, 'result': pipeline})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/pipelines/<pid>', methods=['GET'])
    def api_pipelines_get(pid):
        try:
            return jsonify({'ok': True, 'result': pipeline_mgr.get_pipeline(pid)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 404

    @app.route('/api/pipelines/<pid>', methods=['PUT'])
    def api_pipelines_update(pid):
        try:
            d = request.get_json(silent=True) or {}
            pipeline = pipeline_mgr.update_pipeline(pid, d)
            return jsonify({'ok': True, 'result': pipeline})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/pipelines/<pid>', methods=['DELETE'])
    def api_pipelines_delete(pid):
        try:
            pipeline_mgr.delete_pipeline(pid)
            return jsonify({'ok': True})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/pipelines/<pid>/execute', methods=['POST'])
    def api_pipelines_execute(pid):
        try:
            run = pipeline_mgr.execute_pipeline(pid)
            return jsonify({'ok': True, 'result': run})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/pipelines/runs', methods=['GET'])
    def api_pipeline_runs_list():
        try:
            pid = request.args.get('pipeline_id')
            return jsonify({'ok': True, 'result': pipeline_mgr.get_runs(pipeline_id=pid)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/api/pipelines/runs/<rid>', methods=['GET'])
    def api_pipeline_runs_get(rid):
        try:
            return jsonify({'ok': True, 'result': pipeline_mgr.get_run(rid)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 404

    @app.route('/api/pipelines/runs/<rid>/cancel', methods=['POST'])
    def api_pipeline_runs_cancel(rid):
        try:
            run = pipeline_mgr.cancel_run(rid)
            return jsonify({'ok': True, 'result': run})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/pipelines/import', methods=['POST'])
    def api_pipelines_import():
        try:
            d = request.get_json(silent=True) or {}
            d.pop('id', None)
            d['id'] = str(uuid.uuid4())
            d['created'] = datetime.now().isoformat()
            d['updated'] = datetime.now().isoformat()
            data = pipeline_mgr._load()
            data.setdefault('pipelines', []).append(d)
            pipeline_mgr._save(data)
            return jsonify({'ok': True, 'result': d})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400

    @app.route('/api/pipelines/<pid>/export', methods=['GET'])
    def api_pipelines_export(pid):
        try:
            return jsonify({'ok': True, 'result': pipeline_mgr.get_pipeline(pid)})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 404

    return pipeline_mgr