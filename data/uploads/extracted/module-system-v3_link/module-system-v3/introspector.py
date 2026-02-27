"""
Package Introspector — walks installed packages and returns callable API surface.
"""
import inspect
import importlib
import sys
from typing import Any, Dict, List

API_SEEDS = {
    'kubernetes': [
        'kubernetes.client.CoreV1Api',
        'kubernetes.client.AppsV1Api',
        'kubernetes.client.BatchV1Api',
        'kubernetes.client.NetworkingV1Api',
        'kubernetes.client.RbacAuthorizationV1Api',
        'kubernetes.client.StorageV1Api',
        'kubernetes.config',
    ],
    'boto3':   ['boto3.client', 'boto3.resource', 'boto3.session.Session'],
    'psutil':  ['psutil'],
    'docker':  ['docker.DockerClient'],
    'paramiko':['paramiko.SSHClient', 'paramiko.SFTPClient'],
    'redis':   ['redis.Redis'],
    'celery':  ['celery.Celery'],
}

MAX_FEATURES = 300


def introspect_package(pkg: str) -> Dict:
    features, errors = [], []

    for seed in API_SEEDS.get(pkg, []):
        try:
            parts = seed.rsplit('.', 1)
            if len(parts) == 2:
                mod = importlib.import_module(parts[0])
                obj = getattr(mod, parts[1], None)
                if obj:
                    features.extend(_from_obj(obj, seed))
        except Exception as e:
            errors.append(str(e))

    try:
        mod = importlib.import_module(pkg)
        features.extend(_walk(mod, pkg, 0))
    except Exception as e:
        errors.append(str(e))

    seen, unique = set(), []
    for f in features:
        if f['name'] not in seen:
            seen.add(f['name'])
            unique.append(f)

    unique.sort(key=lambda f: (0 if f['type']=='class' else 1 if f['type']=='function' else 2, f['name']))

    return {
        'package':  pkg,
        'features': unique[:MAX_FEATURES],
        'count':    len(unique),
        'capped':   len(unique) > MAX_FEATURES,
        'errors':   errors[:3],
    }


def _walk(mod, prefix, depth):
    features = []
    if depth > 2:
        return features
    try:
        members = inspect.getmembers(mod)
    except Exception:
        return features
    for name, obj in members:
        if name.startswith('_'):
            continue
        full = f'{prefix}.{name}'
        if inspect.isfunction(obj) or inspect.isbuiltin(obj):
            features.append(_feat(full, obj, 'function'))
        elif inspect.isclass(obj):
            features.append(_feat(full, obj, 'class'))
            features.extend(_from_obj(obj, full, methods_only=True))
        elif inspect.ismodule(obj) and depth < 1:
            mod_name = getattr(obj, '__name__', '')
            if mod_name.startswith(prefix.split('.')[0]):
                features.extend(_walk(obj, full, depth+1))
    return features


def _from_obj(obj, prefix, methods_only=False):
    features = []
    try:
        for name, member in inspect.getmembers(obj):
            if name.startswith('_'):
                continue
            full = f'{prefix}.{name}'
            if inspect.isfunction(member) or inspect.ismethod(member):
                features.append(_feat(full, member, 'method'))
            elif not methods_only and inspect.isclass(member):
                features.append(_feat(full, member, 'class'))
    except Exception:
        pass
    return features


def _feat(name, obj, obj_type):
    doc = inspect.getdoc(obj) or ''
    label = doc.split('\n')[0][:80] if doc else ''
    sig = ''
    try:
        sig = str(inspect.signature(obj))[:100]
    except Exception:
        pass
    return {'name': name, 'label': label, 'type': obj_type, 'signature': sig}
