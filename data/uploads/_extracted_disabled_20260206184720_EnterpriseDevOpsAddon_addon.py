import importlib.util
import os


def _load_module_from(relative_path, name):
    base = os.path.dirname(__file__)
    p = os.path.join(base, *relative_path.split('/'))
    if not os.path.exists(p):
        return None, f'file not found: {p}'
    spec = importlib.util.spec_from_file_location(name, p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, None


def feature_load_enterprise_arm():
    mod, err = _load_module_from('EnterpriseDevOpsAddon/arm/load_enterprise_arm_addon.py', 'enterprise_loader')
    if err:
        return {'success': False, 'error': err}
    try:
        if hasattr(mod, 'main'):
            return {'success': True, 'result': mod.main()}
        if hasattr(mod, 'run'):
            return {'success': True, 'result': mod.run()}
        return {'success': True, 'result': 'module loaded'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def feature_setup_enterprise_arm():
    mod, err = _load_module_from('EnterpriseDevOpsAddon/arm/setup_enterprise_arm_addon.py', 'enterprise_setup')
    if err:
        return {'success': False, 'error': err}
    try:
        if hasattr(mod, 'main'):
            return {'success': True, 'result': mod.main()}
        return {'success': True, 'result': 'setup module loaded'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
