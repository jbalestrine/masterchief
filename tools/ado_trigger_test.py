#!/usr/bin/env python3
"""Dry-run test harness for Azure DevOps trigger paths.
- Exercises `sdk_ado_trigger_pipeline` by monkeypatching `_ado_connection` with a fake connection
  so we exercise the SDK code path without network or credentials.
- Builds the equivalent `az pipelines run` CLI invocation (dry) without executing it.
"""
import json
import shlex
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import main

SAMPLE_PARAMS = {
    "client_id": "CLIENT_ID_ABC",
    "tenant_id": "TENANT_ID_123",
    "client_secret": "CLIENT_SECRET_XYZ",
    "env": "dev",
    "param1": "override1",
}

class FakeRun:
    def __init__(self, rid=999, status='completed'):
        self.id = rid
        self.status = status

class FakePipelinesClient:
    def run_pipeline(self, pipeline_id, project=None, **kwargs):
        print(f"[fake pipelines_client] run_pipeline called -> pipeline_id={pipeline_id}, project={project}, kwargs={list(kwargs.keys())}")
        return FakeRun(rid=12345, status='queued')

class FakeBuildClient:
    def queue_build(self, body, project=None):
        print(f"[fake build_client] queue_build called -> body_keys={list(body.keys())}, project={project}")
        return FakeRun(rid=54321, status='queued')

class FakeClients:
    def get_pipelines_client(self):
        return FakePipelinesClient()
    def get_build_client(self):
        return FakeBuildClient()

class FakeConnection:
    def __init__(self):
        self.clients = FakeClients()


def test_sdk_path():
    print('\n=== SDK Path Dry-Run ===')
    # monkeypatch _ado_connection to return our fake connection
    orig = getattr(main, '_ado_connection', None)
    try:
        main._ado_connection = lambda organization=None, pat=None: FakeConnection()
        res = main.sdk_ado_trigger_pipeline(pipeline_id=123, organization='https://dev.azure.com/example', project='demo', parameters=SAMPLE_PARAMS)
        print('sdk_ado_trigger_pipeline (fake) returned:', res)
    except Exception as e:
        print('sdk path raised:', str(e))
    finally:
        if orig is not None:
            main._ado_connection = orig


def test_cli_build():
    print('\n=== CLI Command Build (dry) ===')
    pid = 123
    org = 'https://dev.azure.com/example'
    values = SAMPLE_PARAMS.copy()
    cmd = ['az', 'pipelines', 'run', '--id', str(pid)]
    if org:
        cmd += ['--org', org]
    for k, v in values.items():
        cmd += ['--variables', f"{k}={v}"]
    print('EXTRACTED VALUES:')
    print(json.dumps(values, indent=2))
    print('\nAZ COMMAND (dry):')
    print(' '.join(shlex.quote(x) for x in cmd))


if __name__ == '__main__':
    test_sdk_path()
    test_cli_build()
