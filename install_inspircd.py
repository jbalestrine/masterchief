import os
import zipfile
import urllib.request
import subprocess

# --- SETTINGS ---
INSPIRCD_URL = "https://github.com/inspircd/inspircd/releases/latest/download/inspircd-windows.zip"
INSTALL_DIR = os.path.join(os.getcwd(), "inspircd")
CONFIG_FILE = os.path.join(INSTALL_DIR, "conf", "inspircd.conf")

# --- DOWNLOAD ZIP ---
print("[*] Downloading InspIRCd...")
zip_path = os.path.join(os.getcwd(), "inspircd.zip")
urllib.request.urlretrieve(INSPIRCD_URL, zip_path)
print("[+] Download complete.")

# --- EXTRACT ZIP ---
print("[*] Extracting files...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(INSTALL_DIR)
print("[+] Extraction complete.")

# --- CREATE BASIC CONFIG ---
print("[*] Creating configuration...")
os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
config_content = """
<server name="MyIRCd" description="My InspIRCd Server" network="MyNet">
<admin name="Admin" nick="Admin" email="admin@example.com">
<bind address="" port="6667" type="clients">
<bind address="" port="7000" type="servers">
<connect allow="*" password="linkpass" timeout="60">
<oper name="admin" password="adminpass" host="*" type="NetAdmin">
<files motd="conf/motd.txt">
"""
with open(CONFIG_FILE, "w") as f:
    f.write(config_content.strip())
print("[+] Configuration created.")

# --- CREATE MOTD ---
motd_path = os.path.join(INSTALL_DIR, "conf", "motd.txt")
with open(motd_path, "w") as f:
    f.write("Welcome to My InspIRCd Server!\n")
print("[+] MOTD created.")

# --- START SERVER ---
print("[*] Starting InspIRCd...")
subprocess.Popen([os.path.join(INSTALL_DIR, "inspircd.exe")], cwd=INSTALL_DIR)
print("[+] InspIRCd is running. Connect via IRC client on port 6667.")
