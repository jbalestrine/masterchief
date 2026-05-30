"""Audit what data_files ships vs what main.py actually needs."""
import os, glob

# What data_files currently ships
webapp = (
    ["main.py"]
    + glob.glob("*.html")
    + ["config.yml", "api_settings.json", "cert_audit.json"]
    + ["auth_config.py", "auth_module.py", "azure_integration.py",
       "github_integration.py", "app_management.py", "image_worker.py"]
)
static_shipped = glob.glob("static/*.css") + glob.glob("static/*.js")

# Root-level .py files that main.py imports
needed_root_py = [
    "sys_diagnostics.py", "validate.py", "run.py",
    "demo_chat_bot.py", "demo_echo.py", "demo_echo_memory.py",
    "demo_echo_suite.py", "demo_scenario_bot.py", "demo_upload.py",
    "demo_code_generation.py", "show_echo.py",
    "train_echo_full_history.py", "train_echo_history.py",
    "train_echo_masterchief_session.py", "irc_echo_bridge.py",
]

shipped_set = set(webapp)
missing_py = [f for f in needed_root_py if f not in shipped_set and os.path.exists(f)]

print("=== DATA_FILES AUDIT ===")
print(f"Shipped .py:   {len([x for x in webapp if x.endswith('.py')])}")
print(f"Shipped .html: {len([x for x in webapp if x.endswith('.html')])}")
print(f"Shipped other: {len([x for x in webapp if not x.endswith('.py') and not x.endswith('.html')])}")
print(f"Shipped static: {len(static_shipped)}")
print()

# All root .py files
all_root_py = sorted(glob.glob("*.py"))
print(f"All root .py files: {len(all_root_py)}")
not_shipped_py = [f for f in all_root_py if f not in shipped_set]
print(f"Not shipped root .py: {len(not_shipped_py)}")
for f in not_shipped_py:
    print(f"  MISS  {f}  ({os.path.getsize(f)//1024} KB)")

# All root .html
all_root_html = sorted(glob.glob("*.html"))
print(f"\nAll root .html files: {len(all_root_html)}")
not_shipped_html = [f for f in all_root_html if f not in shipped_set]
print(f"Not shipped root .html: {len(not_shipped_html)}")
for f in not_shipped_html:
    print(f"  MISS  {f}  ({os.path.getsize(f)//1024} KB)")

# Static files
all_static = sorted(glob.glob("static/*"))
not_shipped_static = [f for f in all_static if f not in set(static_shipped)]
print(f"\nAll static/ files: {len(all_static)}")
print(f"Not shipped static: {len(not_shipped_static)}")
for f in not_shipped_static:
    print(f"  MISS  {f}  ({os.path.getsize(f)//1024} KB)")
