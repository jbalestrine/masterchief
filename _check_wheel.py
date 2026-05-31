import zipfile, sys

z = zipfile.ZipFile('dist/masterchief-2.2.4-py3-none-any.whl')
names = z.namelist()

critical = [
    'features/templates/feature_manager.html',
    'features/templates/github_integration.html',
    'managers/rbac.py', 'managers/vault.py', 'managers/data/script_index.json',
    'tf_wizard/templates/index.html', 'tf_wizard/static/style.css', 'tf_wizard/static/wizard.js',
    'blueprints/ide.py', 'blueprints/terraform.py',
    'core/cli/main.py', 'auth_module.py',
    'platform/chat/chat.html', 'templates/base.py',
    'static/echo_chat.css', 'static/echo_chat.js', 'renderers/__init__.py',
]
data = [
    'main.py', 'caf.html', 'gallery.html', 'arm_creator.html',
    'cloud_dashboard.html', 'echo_chat_page_latest.html', 'rbac.html',
    'secrets_vault.html', 'marketplace.html', 'notifications.html',
    'pipelines.html', 'web_ide.html', 'api_settings.json', 'cert_audit.json', 'config.yml',
]

print("=== PACKAGE FILES ===")
for k in critical:
    found = any(n == k or n.endswith('/' + k) for n in names)
    print(f"  {'OK' if found else 'MISSING':>7}  {k}")

print("\n=== DATA FILES (share/masterchief/) ===")
for k in data:
    found = any(n.endswith('share/masterchief/' + k) for n in names)
    print(f"  {'OK' if found else 'MISSING':>7}  {k}")

total = sum(i.file_size for i in z.infolist())
print(f"\nWheel: {len(names)} files, {total/1024/1024:.2f} MB uncompressed")
