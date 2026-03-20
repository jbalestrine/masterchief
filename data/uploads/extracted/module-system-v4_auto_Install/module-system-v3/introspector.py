"""
Package Introspector
Walks an installed package and returns its callable API surface.
Handles submodule recursion for packages like kubernetes, boto3, azure.
"""
import inspect
import importlib
import sys
from typing import Any, Dict, List, Optional

# Known packages that hide API under submodules
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
    'boto3': [
        'boto3.client',
        'boto3.resource',
        'boto3.session.Session',
    ],
    'azure.mgmt.compute': [
        'azure.mgmt.compute.ComputeManagementClient',
    ],
    'psutil': ['psutil'],
    'docker': ['docker.DockerClient', 'docker.from_env'],
    'paramiko': ['paramiko.SSHClient', 'paramiko.SFTPClient'],
    'redis': ['redis.Redis', 'redis.StrictRedis'],
    'celery': ['celery.Celery'],
    'sqlalchemy': ['sqlalchemy.create_engine', 'sqlalchemy.orm.Session'],
}

MAX_FEATURES = 300


def introspect_package(package_name: str) -> Dict:
    """
    Introspect an installed package and return its callable features.
    Returns: {features: [{name, label, type, module}], count, package, error?}
    """
    features = []
    errors   = []

    # Try seeded entry points first
    seeds = API_SEEDS.get(package_name, [])
    if seeds:
        for seed in seeds:
            try:
                parts = seed.rsplit('.', 1)
                if len(parts) == 2:
                    mod_path, attr = parts
                    mod = importlib.import_module(mod_path)
                    obj = getattr(mod, attr, None)
                    if obj:
                        features.extend(_extract_from_object(obj, seed))
            except Exception as e:
                errors.append(str(e))

    # Always try direct import
    try:
        mod = importlib.import_module(package_name)
        features.extend(_walk_module(mod, package_name, depth=0))
    except Exception as e:
        errors.append(f'Direct import failed: {e}')

    # Deduplicate by name
    seen = set()
    unique = []
    for f in features:
        key = f['name']
        if key not in seen:
            seen.add(key)
            unique.append(f)

    # Sort: classes first, then functions, then the rest
    unique.sort(key=lambda f: (
        0 if f['type'] == 'class' else
        1 if f['type'] == 'function' else 2,
        f['name']
    ))

    return {
        'package':  package_name,
        'features': unique[:MAX_FEATURES],
        'count':    len(unique),
        'capped':   len(unique) > MAX_FEATURES,
        'errors':   errors[:5],
    }


def _walk_module(mod: Any, prefix: str, depth: int = 0) -> List[Dict]:
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
        full_name = f'{prefix}.{name}' if prefix else name

        if inspect.isfunction(obj) or inspect.isbuiltin(obj):
            features.append(_make_feature(full_name, obj, 'function'))

        elif inspect.isclass(obj):
            features.append(_make_feature(full_name, obj, 'class'))
            # Also walk class methods
            features.extend(_extract_from_object(obj, full_name, methods_only=True))

        elif inspect.ismodule(obj) and depth < 1:
            # Only recurse one level into submodules to avoid explosion
            mod_name = getattr(obj, '__name__', '')
            if mod_name.startswith(prefix.split('.')[0]):
                features.extend(_walk_module(obj, full_name, depth + 1))

    return features


def _extract_from_object(obj: Any, prefix: str, methods_only: bool = False) -> List[Dict]:
    features = []
    try:
        for name, member in inspect.getmembers(obj):
            if name.startswith('_'):
                continue
            full_name = f'{prefix}.{name}'
            if inspect.isfunction(member) or inspect.ismethod(member):
                features.append(_make_feature(full_name, member, 'method'))
            elif not methods_only and inspect.isclass(member):
                features.append(_make_feature(full_name, member, 'class'))
    except Exception:
        pass
    return features


def _make_feature(name: str, obj: Any, obj_type: str) -> Dict:
    # Get docstring first line as label
    doc = inspect.getdoc(obj) or ''
    label = doc.split('\n')[0][:80] if doc else ''

    # Try to get signature
    sig = ''
    try:
        sig = str(inspect.signature(obj))
        if len(sig) > 100:
            sig = sig[:97] + '…'
    except (ValueError, TypeError):
        pass

    return {
        'name':      name,
        'label':     label,
        'type':      obj_type,
        'signature': sig,
    }
