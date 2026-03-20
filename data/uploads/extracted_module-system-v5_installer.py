"""
Module Installer
Handles uploaded .zip files, extracts them, validates structure,
and registers the plugin live.
"""
import zipfile
import subprocess
import sys
import shutil
from pathlib import Path

PLUGINS_DIR = Path(__file__).parent / "plugins"
REQUIRED_FILES = {"plugin.py"}
OPTIONAL_FILES = {"template.html", "requirements.txt", "README.md"}


def install_from_zip(zip_path: Path, plugins_dir: Path = PLUGINS_DIR) -> dict:
    """
    Extract, validate, install requirements, and register a module zip.
    Returns {success, slug, installed_files, warnings, errors}
    """
    warnings = []
    errors = []

    # 1. Validate zip
    if not zipfile.is_zipfile(zip_path):
        return {"success": False, "errors": ["Not a valid zip file"]}

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()

    # Detect slug from zip structure (top-level folder or flat)
    top_dirs = set()
    for name in names:
        parts = Path(name).parts
        if parts:
            top_dirs.add(parts[0])

    if len(top_dirs) == 1:
        slug = list(top_dirs)[0].rstrip("/")
        flat = False
    else:
        # Flat zip — use zip filename as slug
        slug = zip_path.stem
        flat = True

    dest_dir = plugins_dir / slug
    dest_dir.mkdir(parents=True, exist_ok=True)

    # 2. Extract
    with zipfile.ZipFile(zip_path, "r") as zf:
        if flat:
            zf.extractall(dest_dir)
        else:
            for member in zf.infolist():
                parts = Path(member.filename).parts
                if len(parts) > 1:
                    rel = Path(*parts[1:])
                elif len(parts) == 1 and parts[0] == slug:
                    continue  # skip top dir entry
                else:
                    rel = Path(member.filename)
                target = dest_dir / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                if not member.is_dir():
                    with zipfile.ZipFile(zip_path) as zf2:
                        target.write_bytes(zf2.read(member.filename))

    installed_files = [f.name for f in dest_dir.iterdir() if f.is_file()]

    # 3. Validate required files
    missing = REQUIRED_FILES - set(installed_files)
    if missing:
        errors.append(f"Missing required files: {missing}. Upload aborted.")
        shutil.rmtree(dest_dir)
        return {"success": False, "errors": errors}

    for opt in OPTIONAL_FILES:
        if opt not in installed_files:
            warnings.append(f"Optional file '{opt}' not found — some features may be limited")

    # 4. Install requirements if present
    req_file = dest_dir / "requirements.txt"
    if req_file.exists():
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(req_file), "--quiet"],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            warnings.append(f"pip install warning: {result.stderr.strip()[:200]}")
        else:
            warnings.append(f"Requirements installed from requirements.txt")

    # 5. Copy template to templates/modules/ if present
    template_src = dest_dir / "template.html"
    templates_dir = Path(__file__).parent / "templates" / "modules"
    templates_dir.mkdir(parents=True, exist_ok=True)
    if template_src.exists():
        shutil.copy(template_src, templates_dir / f"{slug}.html")

    # 6. Copy plugin.py to plugins/ root for plugin_manager discovery
    plugin_src = dest_dir / "plugin.py"
    shutil.copy(plugin_src, plugins_dir / f"{slug}.py")

    return {
        "success": True,
        "slug": slug,
        "dest_dir": str(dest_dir),
        "installed_files": installed_files,
        "warnings": warnings,
        "errors": errors,
    }
