"""platform — MasterChief platform modules (chat, data, etc.).

This package shadows the stdlib ``platform`` module.  We eagerly load the
real stdlib module by file path and copy its public attributes into this
namespace so ``platform.python_version()`` etc. keep working.
"""

import importlib.util as _ilu
import sys as _sys
import pathlib as _pathlib

# Locate the real stdlib platform.py by walking sys.path
_stdlib_mod = None
_this_dir = str(_pathlib.Path(__file__).resolve().parent)
for _sp in _sys.path:
    _candidate = _pathlib.Path(_sp) / 'platform.py'
    if _candidate.is_file() and str(_candidate.resolve().parent) != _this_dir:
        _spec = _ilu.spec_from_file_location('_stdlib_platform', str(_candidate))
        if _spec and _spec.loader:
            _stdlib_mod = _ilu.module_from_spec(_spec)
            _spec.loader.exec_module(_stdlib_mod)
            break

if _stdlib_mod is not None:
    for _name in dir(_stdlib_mod):
        if not _name.startswith('_'):
            globals()[_name] = getattr(_stdlib_mod, _name)

del _ilu, _pathlib, _this_dir, _sp, _candidate, _spec, _stdlib_mod, _name


