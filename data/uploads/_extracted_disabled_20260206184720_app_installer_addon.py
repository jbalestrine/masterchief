import os
import json
import subprocess
import threading
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[4]
STATUS_DIR = ROOT / 'data' / 'install_status'
STATUS_DIR.mkdir(parents=True, exist_ok=True)
OLD_STATUS_DIR = ROOT / 'data' / 'data' / 'install_status'

METADATA_DIR = STATUS_DIR

def _meta_file(app):
    return METADATA_DIR / f"{app}.meta.json"

def _status_file(app):
    return STATUS_DIR / f"{app}.json"

def _run_background(cmd, app):
    sf = _status_file(app)
    def target():
        try:
            with open(sf, 'w', encoding='utf-8') as f:
                json.dump({'app': app, 'state': 'running', 'cmd': cmd}, f)
            logf = STATUS_DIR / f"{app}.log"
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, text=True)
            out, err = p.communicate()
            rc = p.returncode
            # write a human-readable log file
            try:
                with open(logf, 'w', encoding='utf-8') as lf:
                    lf.write('COMMAND: ' + ' '.join(map(str, cmd)) + '\n\n')
                    lf.write('--- STDOUT ---\n')
                    lf.write(out or '')
                    lf.write('\n--- STDERR ---\n')
                    lf.write(err or '')
            except Exception:
                pass
            # write status JSON including a small preview of output and a link to the full log
            status = {'app': app, 'state': 'finished', 'returncode': rc, 'log_file': str(logf)}
            try:
                status['stdout_preview'] = (out or '')[:2000]
            except Exception:
                status['stdout_preview'] = ''
            try:
                status['stderr_preview'] = (err or '')[:2000]
            except Exception:
                status['stderr_preview'] = ''
            with open(sf, 'w', encoding='utf-8') as f:
                json.dump(status, f)
        except Exception as e:
            with open(sf, 'w', encoding='utf-8') as f:
                json.dump({'app': app, 'state': 'failed', 'error': str(e)}, f)
    t = threading.Thread(target=target, daemon=True)
    t.start()
    return {'started': True, 'status_file': str(sf)}

def feature_install_windows(params: dict):
    app = params.get('app')
    if not app:
        return {'error': 'missing app'}
    choco = params.get('choco_package', '')
    zipurl = params.get('zip_url', '')
    installdir = params.get('install_dir', '')
    script = str(ROOT / 'tools' / 'installers' / 'install_app_windows.ps1')
    cmd = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', script, '-AppName', app]
    if choco:
        cmd += ['-ChocoPackage', choco]
    if zipurl:
        cmd += ['-ZipUrl', zipurl]
    if installdir:
        cmd += ['-InstallDir', installdir]
    return _run_background(cmd, app)

def feature_install_ubuntu(params: dict):
    app = params.get('app')
    if not app:
        return {'error': 'missing app'}
    apt = params.get('apt_package', '')
    tar = params.get('tar_url', '')
    installdir = params.get('install_dir', '')
    script = str(ROOT / 'tools' / 'installers' / 'install_app_ubuntu.sh')
    cmd = ['bash', script, '--app', app]
    if apt:
        cmd += ['--apt', apt]
    if tar:
        cmd += ['--tar', tar]
    if installdir:
        cmd += ['--install-dir', installdir]
    return _run_background(cmd, app)

def feature_install_docker(params: dict):
    """Install/run an application using Docker. Params:
    - app: logical name (used for container name)
    - docker_image: image name (default: inspircd/inspircd:latest)
    - ports: string or list of port mappings like '6667:6667' or ['6667:6667','6697:6697']
    """
    app = params.get('app')
    if not app:
        return {'error': 'missing app'}
    image = params.get('docker_image', 'inspircd/inspircd:latest')
    ports = params.get('ports', ['6667:6667'])
    # normalize ports to list
    if isinstance(ports, str):
        ports_list = [ports]
    else:
        try:
            ports_list = list(ports)
        except Exception:
            ports_list = ['6667:6667']

    port_args = ' '.join(f"-p {p}" for p in ports_list)
    # Use platform-appropriate shell wrapper: prefer PowerShell on Windows, bash on Unix
    if os.name == 'nt':
        # chain pull + stop/remove existing + run; redirect stderr to $null to avoid PowerShell parameter issues
        cmd_str = f"docker pull {image}; docker stop {app} 2>$null; docker rm {app} 2>$null; docker run -d --name {app} {port_args} {image}"
        cmd = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', cmd_str]
    else:
        cmd_str = f"docker pull {image} && docker stop {app} || true && docker rm {app} || true && docker run -d --name {app} {port_args} {image}"
        cmd = ['bash', '-c', cmd_str]

    # persist metadata for this installed app so start/stop can reuse the same args
    try:
        meta = {'app': app, 'image': image, 'ports': ports_list, 'created_at': datetime.utcnow().isoformat()}
        _meta_file(app).write_text(json.dumps(meta), encoding='utf-8')
    except Exception:
        pass
    return _run_background(cmd, app)

def feature_docker_start(params: dict):
    """Start (or run) the named container. Params: app, docker_image(optional), ports(optional)"""
    app = params.get('app')
    if not app:
        return {'error': 'missing app'}
    image = params.get('docker_image')
    ports = params.get('ports')
    # if not provided, try metadata
    try:
        if not image or not ports:
            mf = _meta_file(app)
            if mf.exists():
                m = json.loads(mf.read_text(encoding='utf-8'))
                image = image or m.get('image')
                ports = ports or m.get('ports')
    except Exception:
        pass
    if not image:
        image = 'inspircd/inspircd:latest'
    if not ports:
        ports = ['6667:6667']
    if isinstance(ports, str):
        ports_list = [ports]
    else:
        try:
            ports_list = list(ports)
        except Exception:
            ports_list = ['6667:6667']
    port_args = ' '.join(f"-p {p}" for p in ports_list)
    if os.name == 'nt':
        cmd_str = f"docker pull {image}; docker stop {app} 2>$null; docker rm {app} 2>$null; docker run -d --name {app} {port_args} {image}"
        cmd = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', cmd_str]
    else:
        cmd_str = f"docker pull {image} && docker stop {app} || true && docker rm {app} || true && docker run -d --name {app} {port_args} {image}"
        cmd = ['bash', '-c', cmd_str]
    # update metadata with last action
    try:
        meta = {'app': app, 'image': image, 'ports': ports, 'last_action': 'start', 'updated_at': datetime.utcnow().isoformat()}
        _meta_file(app).write_text(json.dumps(meta), encoding='utf-8')
    except Exception:
        pass
    return _run_background(cmd, app)

def feature_docker_stop(params: dict):
    """Stop and remove the named container. Params: app"""
    app = params.get('app')
    if not app:
        return {'error': 'missing app'}
    if os.name == 'nt':
        cmd_str = f"docker stop {app} 2>$null; docker rm {app} 2>$null"
        cmd = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', cmd_str]
    else:
        cmd_str = f"docker stop {app} || true && docker rm {app} || true"
        cmd = ['bash', '-c', cmd_str]
    try:
        meta = {'app': app, 'last_action': 'stop', 'updated_at': datetime.utcnow().isoformat()}
        _meta_file(app).write_text(json.dumps(meta), encoding='utf-8')
    except Exception:
        pass
    return _run_background(cmd, app)

def feature_docker_status(params: dict):
    """Return container status synchronously. Params: app"""
    app = params.get('app')
    if not app:
        return {'error': 'missing app'}
    try:
        # check if container is running
        proc = subprocess.run(['docker', 'ps', '--filter', f'name={app}', '--format', '{{.Names}}|{{.Status}}'], capture_output=True, text=True, timeout=10)
        out = proc.stdout.strip()
        running = False
        info = out
        if out:
            # if any line present, consider it running/exists
            running = True
        outp = {'app': app, 'running': running, 'info': info, 'returncode': proc.returncode}
        # include persisted metadata if available
        try:
            mf = _meta_file(app)
            if mf.exists():
                outp['meta'] = json.loads(mf.read_text(encoding='utf-8'))
        except Exception:
            pass
        return outp
    except Exception as e:
        return {'app': app, 'error': str(e)}


def feature_docker_log(params: dict):
    """Return a tail/preview of the app log file."""
    app = params.get('app')
    if not app:
        return {'error': 'missing app'}
    logf = STATUS_DIR / f"{app}.log"
    if not logf.exists():
        return {'app': app, 'error': 'log_not_found'}
    try:
        txt = logf.read_text(encoding='utf-8')
        # return last ~10000 chars for UI
        return {'app': app, 'log_preview': txt[-10000:], 'log_file': str(logf)}
    except Exception as e:
        return {'app': app, 'error': str(e)}


def feature_docker_daemon_status(params: dict = None):
    """Check whether Docker daemon is available by running `docker info`."""
    try:
        proc = subprocess.run(['docker', 'info'], capture_output=True, text=True, timeout=6)
        running = proc.returncode == 0
        info = (proc.stdout or '') + '\n' + (proc.stderr or '')
        return {'running': running, 'info': info, 'returncode': proc.returncode}
    except Exception as e:
        return {'running': False, 'error': str(e)}


def feature_docker_daemon_start(params: dict = None):
    """Attempt to start the Docker daemon/service. Best-effort; may require privileges.
    On Windows tries to start the com.docker.service or launch Docker Desktop.
    On Linux tries systemctl/service start (may require sudo).
    """
    try:
        if os.name == 'nt':
            # try to start the Docker Windows service
            cmd = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', 'Start-Service -Name com.docker.service']
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            if proc.returncode == 0:
                return {'started': True, 'stdout': proc.stdout, 'stderr': proc.stderr}
            # fallback: try launching Docker Desktop executable (best-effort)
            possible = [
                r'C:\Program Files\Docker\Docker\Docker Desktop.exe',
                r'C:\Program Files\Docker\Docker\DockerDesktop.exe'
            ]
            for p in possible:
                try:
                    if Path(p).exists():
                        subprocess.Popen([p], shell=False)
                        return {'started': True, 'launched': p}
                except Exception:
                    continue
            return {'started': False, 'stdout': proc.stdout, 'stderr': proc.stderr, 'note': 'service_start_failed'}
        else:
            # try systemctl or service (may need sudo)
            cmd = ['sh', '-c', 'sudo systemctl start docker || sudo service docker start']
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            return {'started': proc.returncode == 0, 'stdout': proc.stdout, 'stderr': proc.stderr, 'returncode': proc.returncode}
    except Exception as e:
        return {'started': False, 'error': str(e)}

def feature_docker_list(params: dict = None):
    """Return list of docker containers with name, image, status, and ports."""
    try:
        proc = subprocess.run(['docker', 'ps', '-a', '--format', '{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}'], capture_output=True, text=True, timeout=10)
        lines = [l for l in proc.stdout.splitlines() if l.strip()]
        items = []
        for ln in lines:
            parts = ln.split('|')
            name = parts[0] if len(parts) > 0 else ''
            image = parts[1] if len(parts) > 1 else ''
            status = parts[2] if len(parts) > 2 else ''
            ports = parts[3] if len(parts) > 3 else ''
            items.append({'name': name, 'image': image, 'status': status, 'ports': ports})
        return {'containers': items, 'returncode': proc.returncode}
    except Exception as e:
        return {'error': str(e)}

def feature_install_status(params: dict):
    app = params.get('app')
    if not app:
        return {'error': 'missing app'}
    sf = _status_file(app)
    if not sf.exists():
        # tolerate older path where code previously used data/data/install_status
        old_sf = OLD_STATUS_DIR / f"{app}.json"
        if old_sf.exists():
            sf = old_sf
        else:
            return {'app': app, 'state': 'not_found'}
    try:
        return json.loads(sf.read_text(encoding='utf-8'))
    except Exception as e:
        return {'app': app, 'state': 'error', 'error': str(e)}

def feature_list_files(params: dict = None):
    root = Path(__file__).resolve().parents[4]
    files = [str(p.relative_to(root)) for p in (root / 'data').rglob('*') if p.is_file()]
    return {'files': files[:500]}
