"""
Module Manager — Flask App
Routes:
  GET  /                       → Module marketplace
  GET  /generate               → Generate new module page
  POST /api/introspect         → Install + introspect package → feature list
  POST /api/generate           → Generate scaffold from selected features → zip
  GET  /api/download/<slug>    → Download generated zip
  POST /api/upload             → Upload + install a zip module
  GET  /api/modules            → List installed modules
  DELETE /api/modules/<slug>   → Uninstall a module
"""
import json
import os
import shutil
from pathlib import Path
from flask import (
    Flask, render_template, request, jsonify,
    send_file, redirect, url_for
)
from introspector import install_package, introspect_package
from generator import generate_module
from installer import install_from_zip
import tempfile
import werkzeug

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max upload

BASE_DIR = Path(__file__).parent
PROXY_BASE = f"/addons/modules/{BASE_DIR.name}/app"

@app.context_processor
def inject_base():
    return {"base_url": PROXY_BASE}

PLUGINS_DIR = BASE_DIR / "plugins"
GENERATED_DIR = BASE_DIR / "generated_modules"
UPLOAD_DIR = BASE_DIR / "uploads"

for d in [PLUGINS_DIR, GENERATED_DIR, UPLOAD_DIR]:
    d.mkdir(exist_ok=True)

# ─── Pre-defined module catalog ───────────────────────────────────────────────
CATALOG = [
    {
        "pip_name": "kubernetes",
        "label": "Kubernetes",
        "icon": "☸️",
        "color": "#326ce5",
        "description": "Manage pods, deployments, services, namespaces and cluster resources",
        "tags": ["orchestration", "containers", "cloud"],
    },
    {
        "pip_name": "hvac",
        "label": "HashiCorp Vault",
        "icon": "🔐",
        "color": "#ffd814",
        "description": "Secrets management, authentication, and policy enforcement",
        "tags": ["security", "secrets", "auth"],
    },
    {
        "pip_name": "boto3",
        "label": "AWS (boto3)",
        "icon": "☁️",
        "color": "#ff9900",
        "description": "Full AWS cloud management — EC2, S3, Lambda, RDS, and more",
        "tags": ["cloud", "aws", "infrastructure"],
    },
    {
        "pip_name": "docker",
        "label": "Docker",
        "icon": "🐳",
        "color": "#2496ed",
        "description": "Container lifecycle management, images, volumes, and networks",
        "tags": ["containers", "devops"],
    },
    {
        "pip_name": "psutil",
        "label": "System Monitor",
        "icon": "📊",
        "color": "#00ff88",
        "description": "CPU, memory, disk, network, and process monitoring",
        "tags": ["monitoring", "system"],
    },
    {
        "pip_name": "paramiko",
        "label": "SSH Manager",
        "icon": "🔑",
        "color": "#a78bfa",
        "description": "SSH connections, remote command execution, and SFTP",
        "tags": ["ssh", "automation", "remote"],
    },
    {
        "pip_name": "gitpython",
        "label": "Git Tools",
        "icon": "🌿",
        "color": "#f05033",
        "description": "Git repo management, branch control, commit history",
        "tags": ["git", "vcs", "devops"],
    },
    {
        "pip_name": "apscheduler",
        "label": "Task Scheduler",
        "icon": "⏱️",
        "color": "#ec4899",
        "description": "Job scheduling, cron tasks, interval and date triggers",
        "tags": ["scheduling", "automation"],
    },
    {
        "pip_name": "prometheus-client",
        "label": "Prometheus",
        "icon": "🔥",
        "color": "#e6522c",
        "description": "Expose and collect metrics, counters, gauges, histograms",
        "tags": ["monitoring", "metrics", "observability"],
    },
    {
        "pip_name": "netmiko",
        "label": "Network Devices",
        "icon": "🌐",
        "color": "#06b6d4",
        "description": "SSH into routers, switches, firewalls across vendors",
        "tags": ["networking", "ssh", "automation"],
    },
    {
        "pip_name": "python-gitlab",
        "label": "GitLab",
        "icon": "🦊",
        "color": "#fc6d26",
        "description": "GitLab repos, pipelines, MRs, issues, and users",
        "tags": ["git", "ci/cd", "devops"],
    },
    {
        "pip_name": "PyGithub",
        "label": "GitHub",
        "icon": "🐙",
        "color": "#6e40c9",
        "description": "GitHub repos, pull requests, actions, and team management",
        "tags": ["git", "ci/cd", "devops"],
    },
]

def get_installed_slugs():
    return {f.stem for f in PLUGINS_DIR.glob("*.py") if not f.name.startswith("_")}


# ─── ROUTES ───────────────────────────────────────────────────────────────────

@app.route("/")
def marketplace():
    installed = get_installed_slugs()
    return render_template(
        "marketplace.html",
        catalog=CATALOG,
        installed=installed,
    )


@app.route("/generate/<pip_name>")
def generate_page(pip_name):
    catalog_entry = next((c for c in CATALOG if c["pip_name"] == pip_name), {
        "pip_name": pip_name,
        "label": pip_name.title(),
        "icon": "🔧",
        "color": "#58a6ff",
        "description": "",
    })
    return render_template("generate.html", entry=catalog_entry)


@app.route("/upload")
def upload_page():
    return render_template("upload.html")


# ─── API ──────────────────────────────────────────────────────────────────────

@app.route("/api/introspect")
def api_introspect():
    pip_name = request.args.get("pip_name", "").strip()
    if not pip_name:
        return jsonify({"error": "pip_name required"}), 400

    install_result = install_package(pip_name)
    if not install_result["success"]:
        return jsonify({"error": install_result["message"]}), 400

    result = introspect_package(pip_name)
    if "error" in result:
        return jsonify({"error": result["error"]}), 400

    return jsonify(result)


@app.route("/api/generate")
def api_generate():
    import json as _json
    pip_name = request.args.get("pip_name", "").strip()
    selected_ids = _json.loads(request.args.get("selected_features", "[]"))
    meta = _json.loads(request.args.get("meta", "{}"))

    if not pip_name or not selected_ids:
        return jsonify({"error": "pip_name and selected_features required"}), 400

    result = generate_module(pip_name, selected_ids, meta, GENERATED_DIR)
    if not result["success"]:
        return jsonify({"error": result.get("error")}), 500

    return jsonify(result)


@app.route("/api/download/<slug>")
def api_download(slug):
    zip_path = GENERATED_DIR / f"{slug}.zip"
    if not zip_path.exists():
        return jsonify({"error": "File not found"}), 404
    return send_file(zip_path, as_attachment=True, download_name=f"{slug}.zip")


@app.route("/api/upload", methods=["GET", "POST"])
def api_upload():
    if request.method == "GET":
        return jsonify({"error": "Upload requires POST with file"}), 405
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    f = request.files["file"]
    if not f.filename.endswith(".zip"):
        return jsonify({"error": "Only .zip files accepted"}), 400

    tmp = UPLOAD_DIR / werkzeug.utils.secure_filename(f.filename)
    f.save(tmp)

    result = install_from_zip(tmp, PLUGINS_DIR)
    return jsonify(result)


@app.route("/api/modules")
def api_modules():
    installed = get_installed_slugs()
    result = []
    for slug in installed:
        plugin_file = PLUGINS_DIR / f"{slug}.py"
        try:
            content = plugin_file.read_text()
            # Parse PLUGIN_META label naively
            label = slug.replace("_", " ").title()
            for line in content.splitlines():
                if '"label"' in line and ":" in line:
                    label = line.split(":")[1].strip().strip('",')
                    break
        except Exception:
            label = slug
        result.append({"slug": slug, "label": label})
    return jsonify(result)


@app.route("/api/modules/<slug>", methods=["DELETE"])
def api_delete_module(slug):
    plugin_file = PLUGINS_DIR / f"{slug}.py"
    template_file = BASE_DIR / "templates" / "modules" / f"{slug}.html"
    module_dir = PLUGINS_DIR / slug

    removed = []
    if plugin_file.exists():
        plugin_file.unlink()
        removed.append(str(plugin_file))
    if template_file.exists():
        template_file.unlink()
        removed.append(str(template_file))
    if module_dir.exists():
        shutil.rmtree(module_dir)
        removed.append(str(module_dir))

    if not removed:
        return jsonify({"error": "Module not found"}), 404

    return jsonify({"success": True, "removed": removed})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
