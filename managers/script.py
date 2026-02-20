import json
import time
import os
import shutil
from pathlib import Path
from datetime import datetime
import subprocess
import sys
from werkzeug.utils import secure_filename
from flask import request, jsonify, render_template_string, flash
import base64


def _interpreter_cmd_for_path(p: Path, requested_shell=None):
    try:
        if requested_shell:
            rs = str(requested_shell).lower()
            if rs in ('python','py','python3'):
                return [sys.executable, str(p)]
            if rs in ('powershell','ps1','pwsh'):
                return ['powershell','-ExecutionPolicy','Bypass','-File', str(p)]
            if rs in ('bash','sh'):
                # honor explicit request for bash/sh only if available on PATH
                if shutil.which('bash'):
                    return ['bash', str(p)]
                if shutil.which('wsl'):
                    return ['wsl', str(p)]
                return None
        # common suffixes
        if p.suffix == '.py':
            return [sys.executable, str(p)]
        if p.suffix == '.ps1':
            return ['powershell','-ExecutionPolicy','Bypass','-File', str(p)]
        # On Windows, avoid implicitly selecting WSL/bash for unknown types.
        # Prefer explicit shells (python/powershell) to prevent invoking missing WSL binaries.
        if sys.platform.startswith('win'):
            return None
        # on unix-like platforms run the file directly
        return [str(p)]
    except Exception:
        return None


class ScriptManager:
    def __init__(self, scripts_folder):
        self.scripts_folder = Path(scripts_folder)

    def list_scripts(self, include_repo_paths: bool = True, use_cache: bool = True):
        """Return scripts organized by category with a simple on-disk cache.

        Returns a list of category dicts: [{'category':'name','scripts':[...]}]
        """
        cache_file = Path(__file__).resolve().parent / 'data' / 'script_index.json'
        cache_age = None
        if cache_file.exists():
            try:
                cache_age = time.time() - cache_file.stat().st_mtime
                if use_cache and cache_age is not None and cache_age < 30:
                    with open(cache_file,'r',encoding='utf-8') as f:
                        return json.load(f)
            except Exception:
                # If reading the cache fails, ignore and do a fresh scan
                pass

        scripts=[]
        searched=set()
        # Primary scripts folder
        for ext in ['*.sh','*.ps1','*.py','*.bash']:
            for script_file in self.scripts_folder.glob(ext):
                if script_file.exists():
                    key=str(script_file.resolve())
                    if key in searched:
                        continue
                    searched.add(key)
                    scripts.append({'name':script_file.name,'path':str(script_file.resolve()),'size':script_file.stat().st_size,'modified':datetime.fromtimestamp(script_file.stat().st_mtime).isoformat(),'type':script_file.suffix[1:],'source':'scripts_folder'})

        if include_repo_paths:
            # Also scan repo root and parent directories for scripts (limited depth/glob)
            try:
                repo_root=Path(__file__).resolve().parents[0]
                search_dirs=[repo_root, repo_root.parent]
                for sd in search_dirs:
                    if not sd.exists():
                        continue
                    for ext in ['**/*.sh','**/*.ps1','**/*.py','**/*.bash']:
                        for script_file in sd.glob(ext):
                            if script_file.is_file():
                                key=str(script_file.resolve())
                                if key in searched:
                                    continue
                                searched.add(key)
                                scripts.append({'name':script_file.name,'path':str(script_file.resolve()),'size':script_file.stat().st_size,'modified':datetime.fromtimestamp(script_file.stat().st_mtime).isoformat(),'type':script_file.suffix[1:],'source':'repo'})
            except Exception:
                pass

        # Categorize scripts by heuristics (folder names, filename keywords)
        categories_map = {}
        def add_to_category(cat, item):
            if cat not in categories_map:
                categories_map[cat]=[]
            categories_map[cat].append(item)

        keywords = {
            'deploy':['deploy','deploy.sh','deploy.py','k8s','kubernetes','helm','ansible'],
            'backup':['backup','restore','snapshot'],
            'build':['build','compile','make','pack'],
            'test':['test','pytest','unittest','ci','integration'],
            'install':['install','setup','bootstrap','install.ps1'],
            'db':['db','migrate','schema','dump','restore'],
            'tools':['tool','script','util','utility'],
            'images':['image','docker','container'],
        }

        for s in scripts:
            p = Path(s['path'])
            name = p.name.lower()
            placed = False
            # heuristic: folder names
            parts = [part.lower() for part in p.parts]
            for cat, kws in keywords.items():
                if any(k in name for k in kws) or any(k in part for part in parts for k in kws):
                    add_to_category(cat, s)
                    placed = True
                    break
            if not placed:
                # fallback by top-level folder
                top = parts[0] if parts else ''
                add_to_category(top or 'other', s)

        # Build result list sorted by category name, with scripts sorted
        result = []
        for cat in sorted(categories_map.keys()):
            items = sorted(categories_map[cat], key=lambda x: x['name'])
            result.append({'category':cat,'scripts':items})

        # Cache index to disk for short period
        try:
            cache_file.parent.mkdir(parents=True,exist_ok=True)
            with open(cache_file,'w',encoding='utf-8') as f:
                json.dump(result,f)
        except Exception:
            pass

        return result

    def add_script(self,filename,content):
        # Allow subdirectories but prevent path traversal
        try:
            # normalize and join
            target = Path(self.scripts_folder) / Path(filename)
            resolved = target.resolve()
            base = Path(self.scripts_folder).resolve()
            if not str(resolved).startswith(str(base)):
                return False
            resolved.parent.mkdir(parents=True, exist_ok=True)
            with open(resolved, 'w', encoding='utf-8') as f:
                f.write(content)
            # make executable where appropriate
            try:
                os.chmod(resolved, 0o755)
            except Exception:
                pass
            return True
        except Exception:
            return False

    def delete_script(self,filename):
        try:
            target = Path(self.scripts_folder) / Path(filename)
            resolved = target.resolve()
            base = Path(self.scripts_folder).resolve()
            if not str(resolved).startswith(str(base)):
                return False
            if resolved.exists():
                resolved.unlink()
                # cleanup empty parents
                try:
                    p = resolved.parent
                    while p != base and not any(p.iterdir()):
                        p.rmdir()
                        p = p.parent
                except Exception:
                    pass
                return True
            return False
        except Exception:
            return False

    def execute_script(self,filename,args=''):
        script_path=self.scripts_folder/secure_filename(filename)
        if not script_path.exists():
            return {'success':False,'error':'Script not found'}
        try:
            # Choose an interpreter-aware command where possible
            cmd = _interpreter_cmd_for_path(script_path)
            if not cmd:
                # Fall back to attempting to execute directly; if this fails on Windows
                # the caller will receive a helpful error
                cmd = [str(script_path)]
            if args:
                cmd.extend(args.split())
            result=subprocess.run(cmd,capture_output=True,text=True,timeout=300)
            return {'success':result.returncode==0,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
        except subprocess.TimeoutExpired:
            return {'success':False,'error':'Script execution timed out'}
        except Exception as e:
            return {'success':False,'error':str(e)}

    def get_script_content(self,filename):
        try:
            target = Path(self.scripts_folder) / Path(filename)
            resolved = target.resolve()
            base = Path(self.scripts_folder).resolve()
            if not str(resolved).startswith(str(base)):
                return None
            if resolved.exists():
                with open(resolved,'r', encoding='utf-8') as f:
                    return f.read()
            return None
        except Exception:
            return None


def register_script_module(app, scripts_folder='scripts'):
    script_mgr = ScriptManager(scripts_folder)
    
    @app.route('/scripts')
    def scripts_list():
        res = script_mgr.list_scripts(include_repo_paths=True)
        
        # Backwards-compatible: if list_scripts returns categories, flatten for templates that expect a flat list
        if res and isinstance(res, list) and isinstance(res[0], dict) and 'category' in res[0]:
            categories = res
            flat = []
            for c in categories:
                flat.extend(c.get('scripts',[]))
            scripts = flat
        else:
            categories = [{'category':'all','scripts':res}]
            scripts = res
        
        from templates.pages import SCRIPTS_TEMPLATE
        from templates.base import HTML_TEMPLATE
        from flask import request, get_flashed_messages
        return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',SCRIPTS_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),scripts=scripts,categories=categories,request=request,get_flashed_messages=get_flashed_messages)
    def refresh_index():
        # Admin token protection disabled for local development.
        # This endpoint is intentionally left open in dev to simplify testing.
        cache_file = Path(app.root_path) / 'data' / 'script_index.json'
        try:
            if cache_file.exists():
                cache_file.unlink()
            return jsonify({'ok':True,'message':'index invalidated'})
        except Exception as e:
            return jsonify({'ok':False,'error':str(e)}),500
    
    @app.route('/scripts/add',methods=['POST'])
    def scripts_add():
        filename=request.form.get('filename')
        content=request.form.get('content')
        if script_mgr.add_script(filename,content):
            flash('Script added successfully!','success')
        else:
            flash('Failed to add script','error')
        from flask import redirect, url_for
        return redirect(url_for('scripts_list'))
    
    @app.route('/api/ide/scripts')
    def api_ide_scripts():
        files = []
        try:
            scripts_dir = script_mgr.scripts_folder
            for p in sorted(scripts_dir.glob('*')):
                if p.is_file():
                    files.append({'name': p.name, 'size': p.stat().st_size, 'modified': datetime.fromtimestamp(p.stat().st_mtime).isoformat()})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500
        
        return jsonify({'ok': True, 'files': files})
    
    @app.route('/scripts/execute/<filename>')
    def scripts_execute(filename):
        from templates.pages import SCRIPT_EXECUTE_TEMPLATE
        from templates.base import HTML_TEMPLATE
        from flask import request, get_flashed_messages
        return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',SCRIPT_EXECUTE_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),filename=filename,result=None,request=request,get_flashed_messages=get_flashed_messages)
    
    @app.route('/scripts/run/<filename>',methods=['POST'])
    def scripts_run(filename):
        args=request.form.get('args','')
        result=script_mgr.execute_script(filename,args)
        from templates.pages import SCRIPT_EXECUTE_TEMPLATE
        from templates.base import HTML_TEMPLATE
        from flask import request, get_flashed_messages
        return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',SCRIPT_EXECUTE_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),filename=filename,result=result,request=request,get_flashed_messages=get_flashed_messages)
    
    return script_mgr