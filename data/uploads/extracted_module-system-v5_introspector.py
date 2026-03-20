"""
Package Introspector
Installs a pip package and extracts its API as a feature checklist.
"""
import subprocess, sys, inspect, importlib

IMPORT_MAP = {
    "kubernetes": "kubernetes",
    "hvac": "hvac",
    "boto3": "boto3",
    "docker": "docker",
    "psutil": "psutil",
    "gitpython": "git",
    "paramiko": "paramiko",
    "apscheduler": "apscheduler",
    "prometheus-client": "prometheus_client",
    "netmiko": "netmiko",
    "python-gitlab": "gitlab",
    "pygithub": "github",
    "celery": "celery",
    "httpx": "httpx",
    "fabric": "fabric",
}

# For packages whose useful API lives in specific classes, seed directly
# rather than relying on top-level scan
API_SEEDS = {
    "kubernetes": [
        "kubernetes.client.CoreV1Api",
        "kubernetes.client.AppsV1Api",
        "kubernetes.client.BatchV1Api",
        "kubernetes.client.NetworkingV1Api",
        "kubernetes.client.RbacAuthorizationV1Api",
        "kubernetes.client.StorageV1Api",
        "kubernetes.client.AutoscalingV1Api",
    ],
    "docker": [
        "docker.models.containers.ContainerCollection",
        "docker.models.images.ImageCollection",
        "docker.models.volumes.VolumeCollection",
        "docker.models.networks.NetworkCollection",
    ],
}

CATEGORY_HINTS = {
    "list":    "📋 List / Query",
    "get":     "📋 List / Query",
    "read":    "📋 List / Query",
    "fetch":   "📋 List / Query",
    "create":  "✏️ Create / Write",
    "add":     "✏️ Create / Write",
    "put":     "✏️ Create / Write",
    "update":  "✏️ Create / Write",
    "patch":   "✏️ Create / Write",
    "replace": "✏️ Create / Write",
    "delete":  "🗑️ Delete / Remove",
    "remove":  "🗑️ Delete / Remove",
    "destroy": "🗑️ Delete / Remove",
    "status":  "📊 Status / Metrics",
    "health":  "📊 Status / Metrics",
    "metrics": "📊 Status / Metrics",
    "info":    "📊 Status / Metrics",
    "log":     "📋 Logs / Events",
    "event":   "📋 Logs / Events",
    "watch":   "📋 Logs / Events",
}

def _guess_category(name):
    nl = name.lower()
    for k, v in CATEGORY_HINTS.items():
        if k in nl:
            return v
    return "⚙️ Other"

def _infer_data_type(name):
    n = name.lower()
    if any(k in n for k in ["list", "all", "items", "pods", "nodes"]): return "table"
    if any(k in n for k in ["status", "health", "info", "metrics"]): return "stats"
    if any(k in n for k in ["log", "event", "history"]): return "log"
    if any(k in n for k in ["create", "add", "update", "delete", "patch", "replace"]): return "action"
    return "raw"

def install_package(pip_name):
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", pip_name, "--quiet"],
            capture_output=True, text=True, timeout=120
        )
        if r.returncode != 0:
            return {"success": False, "message": r.stderr.strip()}
        return {"success": True, "message": f"{pip_name} installed"}
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "Installation timed out"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def get_import_name(pip_name):
    return IMPORT_MAP.get(pip_name.lower(), pip_name.replace("-", "_"))

def _add_feature(features, seen, name, full_path):
    fid = full_path.replace(".", "_").replace("-", "_")
    if fid in seen:
        return
    seen.add(fid)
    # Skip internal/http_info methods
    if any(x in name for x in ["with_http_info", "without_preload"]):
        return
    try:
        sig = "()"
        doc = ""
    except Exception:
        pass
    features.append({
        "id": fid,
        "label": name.replace("_", " ").title(),
        "method_path": full_path,
        "category": _guess_category(name),
        "description": f"{full_path}()",
        "data_type": _infer_data_type(name),
        "signature": "()",
    })

def introspect_package(pip_name):
    import_name = get_import_name(pip_name)
    try:
        mod = importlib.import_module(import_name)
    except ImportError as e:
        return {"error": f"Could not import '{import_name}': {e}"}

    features = []
    seen = set()

    # --- Seed scan for known packages ---
    seeds = API_SEEDS.get(pip_name.lower(), [])
    for dotted_path in seeds:
        parts = dotted_path.rsplit(".", 1)
        if len(parts) != 2:
            continue
        try:
            seed_mod = importlib.import_module(parts[0])
            cls = getattr(seed_mod, parts[1], None)
            if cls is None:
                continue
            for name, member in inspect.getmembers(cls):
                if name.startswith("_"):
                    continue
                if inspect.isfunction(member) or callable(member):
                    _add_feature(features, seen, name, f"{parts[1]}.{name}")
        except Exception:
            continue

    # --- Generic scan (for everything else) ---
    def scan(obj, path, depth):
        if depth > 3:
            return
        try:
            members = inspect.getmembers(obj)
        except Exception:
            return
        for name, member in members:
            if name.startswith("_"):
                continue
            full_path = f"{path}.{name}" if path else name
            if inspect.isfunction(member) or inspect.ismethod(member):
                _add_feature(features, seen, name, full_path)
            elif inspect.isclass(member) and depth < 2:
                scan(member, full_path, depth + 1)
            elif inspect.ismodule(member) and depth < 1:
                pkg = getattr(member, "__package__", "") or ""
                if pkg.startswith(import_name):
                    scan(member, full_path, depth + 1)

    scan(mod, import_name, 0)

    # Group by category, filter to 300
    cats = {}
    for f in features[:300]:
        cats.setdefault(f["category"], []).append(f)

    return {
        "package": pip_name,
        "import_name": import_name,
        "total_features": len(features),
        "categories": cats,
        "features": features[:300],
    }
