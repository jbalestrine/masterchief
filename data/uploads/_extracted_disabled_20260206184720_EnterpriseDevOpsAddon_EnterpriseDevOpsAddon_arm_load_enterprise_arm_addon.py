import os
import subprocess
from threading import Thread

# =========================
# CONFIGURATION SECTION
# =========================
ADDONS_DIR = "./addons"  # Base folder where all addons are stored
ADDON_NAME = "EnterpriseARMAddon"  # Folder name for this addon
WEBUI_REL_PATH = "webui/index.html"  # Path to the web UI relative to addon folder
BACKEND_REL_PATH = "backend/deploy.py"  # Path to backend script relative to addon folder
BACKEND_PORT = 8080  # Port to run Flask backend
START_BACKEND = True  # Set False if you want to start manually

# =========================
# HELPER FUNCTIONS
# =========================

def addon_path(addon_name):
    """
    Returns the full path to the addon folder.
    """
    return os.path.join(ADDONS_DIR, addon_name)

def webui_path(addon_name):
    """
    Returns the full path to the web UI index file.
    """
    return os.path.join(addon_path(addon_name), WEBUI_REL_PATH)

def backend_path(addon_name):
    """
    Returns the full path to the backend Flask script.
    """
    return os.path.join(addon_path(addon_name), BACKEND_REL_PATH)

def start_backend(script_path, port=BACKEND_PORT):
    """
    Starts the Flask backend in a separate thread so it doesn't block your main application.
    You can customize this function to run in background with logging or supervision.
    """
    def run():
        # Optional: customize environment variables for Flask if needed
        env = os.environ.copy()
        env["FLASK_RUN_PORT"] = str(port)
        subprocess.run(["python", script_path], env=env)
    thread = Thread(target=run, daemon=True)
    thread.start()
    print(f"[Addon] Backend started on port {port}")

# =========================
# ADDON REGISTRATION
# =========================

def register_enterprise_arm_addon():
    """
    Main function to register addon in your platform.
    You can customize this to integrate with your site UI.
    """
    addon_folder = addon_path(ADDON_NAME)

    # Check if addon exists
    if not os.path.exists(addon_folder):
        print(f"[Addon] ERROR: Addon folder '{addon_folder}' not found.")
        return

    # Register web UI (example: add to menu or tab system)
    ui_index = webui_path(ADDON_NAME)
    if os.path.exists(ui_index):
        print(f"[Addon] Web UI detected: {ui_index}")
        # TODO: Integrate this path into your site menu or tab system
        # Example: add_tab("Enterprise ARM Deployment", ui_index)
    else:
        print(f"[Addon] WARNING: Web UI not found at {ui_index}")

    # Start backend if configured
    backend_script = backend_path(ADDON_NAME)
    if START_BACKEND and os.path.exists(backend_script):
        start_backend(backend_script, BACKEND_PORT)
    elif not os.path.exists(backend_script):
        print(f"[Addon] WARNING: Backend script not found at {backend_script}")

    print(f"[Addon] '{ADDON_NAME}' registration complete.")

# =========================
# RUN REGISTRATION
# =========================
if __name__ == "__main__":
    register_enterprise_arm_addon()
