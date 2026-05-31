"""Full audit: what main.py needs vs what the wheel ships."""
import zipfile
import re
from pathlib import Path

WHEEL = "dist/masterchief-2.2.6-py3-none-any.whl"
MAIN = Path("main.py").read_text(encoding="utf-8")

z = zipfile.ZipFile(WHEEL)
wheel_files = set(z.namelist())

# --- 1. HTML files served via send_file() ---
print("=" * 80)
print("1. HTML FILES (send_file calls)")
print("=" * 80)
html_refs = re.findall(r"send_file\(['\"]([^'\"]+\.html)", MAIN)
for h in sorted(set(html_refs)):
    in_data = any(h in f for f in wheel_files if ".data/" in f)
    in_pkg = any(h in f for f in wheel_files if ".data/" not in f)
    status = "OK (data)" if in_data else ("OK (pkg)" if in_pkg else "MISSING")
    print(f"  {status:15s}  {h}")

# All root HTML files on disk
print("\n  --- All root .html files on disk ---")
for hp in sorted(Path(".").glob("*.html")):
    in_data = any(hp.name in f for f in wheel_files if ".data/" in f)
    status = "SHIPPED" if in_data else "NOT SHIPPED"
    print(f"  {status:15s}  {hp.name:40s}  ({hp.stat().st_size // 1024} KB)")

# --- 2. Static files ---
print("\n" + "=" * 80)
print("2. STATIC FILES")
print("=" * 80)
for sp in sorted(Path("static").rglob("*")):
    if sp.is_file():
        in_wheel = any(str(sp).replace("\\", "/") in f for f in wheel_files)
        in_data = any(sp.name in f for f in wheel_files if ".data/" in f and "static" in f)
        status = "OK" if (in_wheel or in_data) else "MISSING"
        print(f"  {status:10s}  {sp}")

# --- 3. Python modules imported at runtime ---
print("\n" + "=" * 80)
print("3. PYTHON IMPORTS (local modules)")
print("=" * 80)
local_imports = {}
for i, line in enumerate(MAIN.splitlines()):
    s = line.strip()
    if s.startswith("from ") or s.startswith("import "):
        m = re.match(r"(?:from|import)\s+([\w.]+)", s)
        if m:
            mod = m.group(1)
            top = mod.split(".")[0]
            # skip stdlib and known 3rd party
            stdlib = {"os","sys","re","json","io","time","datetime","hashlib","secrets",
                      "subprocess","pathlib","shutil","socket","threading","traceback",
                      "uuid","base64","random","copy","functools","math","string",
                      "textwrap","importlib","runpy","logging","tempfile","zipfile",
                      "glob","collections","urllib","http","argparse","html","csv",
                      "mimetypes","contextlib","signal","inspect","struct","binascii",
                      "ast","typing","enum","abc","dataclasses","asyncio","concurrent",
                      "multiprocessing","platform","operator","itertools","weakref",
                      "warnings","bisect","sqlite3","difflib","ssl","builtins"}
            third = {"flask","werkzeug","jinja2","click","yaml","dotenv","jwt","authlib",
                     "bcrypt","jose","pydantic","jsonschema","requests","httpx","psutil",
                     "git","PIL","pillow","sqlalchemy","apscheduler","prometheus_client",
                     "irc","gunicorn","rich","socketio","engineio","cryptography","cffi",
                     "docker","kubernetes","paramiko","boto3","azure","hvac","ansible",
                     "gitlab","github","flask_cors","flask_login","flask_socketio",
                     "torch","diffusers","transformers","peft","akamai"}
            if top not in stdlib and top not in third and top != "__future__":
                if mod not in local_imports:
                    local_imports[mod] = i + 1

for mod, line_no in sorted(local_imports.items()):
    top = mod.split(".")[0]
    # Check if it's in wheel as a package
    pkg_path = mod.replace(".", "/")
    in_pkg = any(f.startswith(pkg_path + "/") or f.startswith(pkg_path + ".py") or
                 f == pkg_path + "/__init__.py" for f in wheel_files)
    # Check py_modules (top-level .py in wheel root)
    in_pymod = f"{top}.py" in wheel_files
    # Check data_files
    in_data = any(f"{top}.py" in f for f in wheel_files if ".data/" in f)
    if in_pkg or in_pymod:
        status = "OK"
    elif in_data:
        status = "DATA ONLY"
    else:
        status = "MISSING"
    print(f"  {status:12s}  L{line_no:5d}  {mod}")

# --- 4. Key features verification ---
print("\n" + "=" * 80)
print("4. KEY FEATURES - FILES IN WHEEL")
print("=" * 80)
features = {
    "templates/base": "templates/__init__.py",
    "templates/pages": "templates/pages.py",
    "templates/diagnostics": "templates/diagnostics.py",
    "templates/scm": "templates/scm.py",
    "blueprints/ide": "blueprints/__init__.py",
    "blueprints/terraform": "blueprints/__init__.py",
    "echo/chat_bot": "echo/chat_bot.py",
    "echo/identity": "echo/identity.py",
    "echo/conversation_storage": "echo/conversation_storage.py",
    "echo/runtime": "echo/runtime/__init__.py",
    "features/manager": "features/manager.py",
    "renderers": "renderers/__init__.py",
    "managers": "managers/__init__.py",
    "auth_module": "auth_module.py",
    "auth_config": "auth_config.py",
    "sys_diagnostics (data)": "masterchief-2.2.6.data/data/share/masterchief/sys_diagnostics.py",
    "masterchief_entry": "masterchief_entry.py",
    "tf_wizard/generator": "tf_wizard/generator.py",
    "tf_wizard/app": "tf_wizard/app.py",
    "setup_wizard": "setup_wizard/__init__.py",
    "tools/dataset_helper": "tools/dataset_helper.py",
    "core/echo/identity": "core/echo/identity.py",
}
for name, path in features.items():
    found = path in wheel_files
    print(f"  {'OK' if found else 'MISSING':8s}  {name:35s}  ({path})")

# --- 5. Summary stats ---
print("\n" + "=" * 80)
print("5. WHEEL SUMMARY")
print("=" * 80)
total_files = len(wheel_files)
py_files = [f for f in wheel_files if f.endswith(".py")]
html_files = [f for f in wheel_files if f.endswith(".html")]
data_sect = [f for f in wheel_files if ".data/" in f]
total_size = sum(i.file_size for i in z.infolist())
comp_size = sum(i.compress_size for i in z.infolist())
print(f"  Total files:      {total_files}")
print(f"  .py files:        {len(py_files)}")
print(f"  .html files:      {len(html_files)}")
print(f"  data_files:       {len(data_sect)}")
print(f"  Uncompressed:     {total_size/1024/1024:.1f} MB")
print(f"  Compressed:       {comp_size/1024/1024:.1f} MB")

# Top-level packages in wheel
tops = set()
for f in wheel_files:
    if "/" in f and not f.startswith("masterchief-"):
        tops.add(f.split("/")[0])
print(f"  Top-level dirs:   {len(tops)}")
for t in sorted(tops):
    count = len([f for f in wheel_files if f.startswith(t + "/")])
    print(f"    {t:30s}  {count:4d} files")

print("\nDone.")
