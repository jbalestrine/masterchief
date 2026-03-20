import os
import subprocess
from threading import Thread

# =========================
# CONFIGURATION
#
#How to Use in Your Web IDE#
#
#Place this script anywhere your IDE can access.
#
#Run it once:
#
#python setup_enterprise_arm_addon.py
#
#
#The backend will start in the background.
#
#The console will print the Web UI path, which you can click to open immediately.
#
#Logs are automatically created in addons/EnterpriseARMAddon/logs/.
# =========================
ADDONS_DIR = "./addons"
ADDON_NAME = "EnterpriseARMAddon"
WEBUI_REL_PATH = "webui/index.html"
BACKEND_REL_PATH = "backend/deploy.py"
BACKEND_PORT = 8080

# =========================
# HELPERS
# =========================

def addon_path(addon_name):
    return os.path.join(ADDONS_DIR, addon_name)

def webui_path(addon_name):
    return os.path.join(addon_path(addon_name), WEBUI_REL_PATH)

def backend_path(addon_name):
    return os.path.join(addon_path(addon_name), BACKEND_REL_PATH)

def start_backend(script_path, port=BACKEND_PORT):
    """Starts the backend Flask server in a background thread."""
    if not os.path.exists(script_path):
        print(f"[Setup] ERROR: Backend script not found at {script_path}")
        return

    def run():
        env = os.environ.copy()
        env["FLASK_RUN_PORT"] = str(port)
        subprocess.run(["python", script_path], env=env)
    
    thread = Thread(target=run, daemon=True)
    thread.start()
    print(f"[Setup] Backend started on port {port}")

# =========================
# SETUP EXECUTION
# =========================

def setup_addon():
    folder = addon_path(ADDON_NAME)
    if not os.path.exists(folder):
        print(f"[Setup] ERROR: Addon folder '{folder}' not found.")
        return

    # Create logs directory if missing
    logs_dir = os.path.join(folder, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Start backend
    backend_script = backend_path(ADDON_NAME)
    start_backend(backend_script, BACKEND_PORT)

    # Print Web UI path
    ui_index = webui_path(ADDON_NAME)
    if os.path.exists(ui_index):
        abs_path = os.path.abspath(ui_index)
        print(f"[Setup] Web UI ready: file://{abs_path}")
    else:
        print(f"[Setup] WARNING: Web UI not found at {ui_index}")

# =========================
# RUN SETUP
# =========================
if __name__ == "__main__":
    setup_addon()
