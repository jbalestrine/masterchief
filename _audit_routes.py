"""Audit: extract all routes, send_file calls, blueprints, and local imports from main.py."""
import re, sys
from pathlib import Path

src = Path("main.py").read_text(encoding="utf-8")
lines = src.splitlines()

# --- Routes ---
print("=" * 80)
print("ALL @app.route() ROUTES")
print("=" * 80)
route_count = 0
for i, line in enumerate(lines):
    m = re.search(r'@app\.route\([\x27\x22]([^\x27\x22]+)', line)
    if m:
        path = m.group(1)
        func = ""
        for j in range(i + 1, min(i + 5, len(lines))):
            fm = re.match(r'\s*def\s+(\w+)', lines[j])
            if fm:
                func = fm.group(1)
                break
        print(f"  L{i+1:5d}  {path:50s}  -> {func}")
        route_count += 1
print(f"\n  Total routes: {route_count}\n")

# --- send_file() ---
print("=" * 80)
print("ALL send_file() CALLS")
print("=" * 80)
for i, line in enumerate(lines):
    m = re.search(r'send_file\([\x27\x22]([^\x27\x22]+)', line)
    if m:
        print(f'  L{i+1:5d}  send_file({m.group(1)!r})')
    elif "send_file(" in line and "send_file(str(" not in line and "send_file(buf" not in line:
        snippet = line.strip()[:80]
        print(f"  L{i+1:5d}  {snippet}")

# --- Blueprints ---
print("\n" + "=" * 80)
print("BLUEPRINT REGISTRATIONS")
print("=" * 80)
for i, line in enumerate(lines):
    if "register_blueprint" in line:
        print(f"  L{i+1:5d}  {line.strip()}")

# --- Local imports (non-stdlib, non-third-party) ---
print("\n" + "=" * 80)
print("LOCAL/PROJECT IMPORTS")
print("=" * 80)
stdlib = {"os","sys","re","json","io","time","datetime","hashlib","secrets","subprocess",
          "pathlib","shutil","socket","threading","traceback","uuid","base64","random",
          "copy","functools","math","string","textwrap","importlib","runpy","logging",
          "tempfile","zipfile","glob","collections","urllib","http","argparse","html",
          "csv","mimetypes","contextlib","signal","inspect","struct","binascii","ast",
          "typing","enum","abc","dataclasses","asyncio","concurrent","multiprocessing",
          "platform","operator","itertools","weakref","warnings","bisect"}
third = {"flask","werkzeug","jinja2","click","yaml","dotenv","jwt","authlib","bcrypt",
         "jose","pydantic","jsonschema","requests","httpx","psutil","git","PIL","pillow",
         "sqlalchemy","apscheduler","prometheus_client","irc","gunicorn","rich",
         "socketio","engineio","cryptography","cffi","docker","kubernetes","paramiko",
         "boto3","azure","hvac","ansible","gitlab","github"}

seen = set()
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith("import ") or stripped.startswith("from "):
        # Extract the top-level module
        if stripped.startswith("from "):
            m = re.match(r"from\s+(\S+)", stripped)
        else:
            m = re.match(r"import\s+(\S+)", stripped)
        if m:
            mod = m.group(1).split(".")[0]
            if mod not in stdlib and mod not in third and mod not in ("__future__",):
                key = f"{mod}|{stripped}"
                if key not in seen:
                    seen.add(key)
                    print(f"  L{i+1:5d}  {stripped[:100]}")

# --- render_template_string ---
print("\n" + "=" * 80)
print("render_template_string / DIAGNOSTICS_TEMPLATE CALLS")
print("=" * 80)
for i, line in enumerate(lines):
    if "render_template_string" in line or "DIAGNOSTICS_TEMPLATE" in line:
        print(f"  L{i+1:5d}  {line.strip()[:100]}")

print("\nDone.")
