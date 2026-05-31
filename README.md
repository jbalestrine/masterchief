# MasterChief Enterprise DevOps Platform

MasterChief is a modular DevOps automation platform with a web dashboard, CLI tools, dynamic modules, and Echo chat capabilities.

## What This Repo Includes

- Web dashboard runtime via main.py and masterchief launcher
- CLI automation under core/cli
- Module and addon system for platform features
- Terraform, Ansible, DSC, and cloud integrations
- Echo chat bot with optional local GGUF model runtime

## Install Profiles

Use one of these profiles depending on how much of the platform you want enabled.

### 1) Core Platform (recommended baseline)

```bash
python -m venv venv
# Windows PowerShell
venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### 2) Full Platform (core + heavy optional features)

```bash
python -m venv venv
# Windows PowerShell
venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt -r requirements-optional.txt
pip install -e .
```

This enables optional AI/ML, voice, queueing, and extra DB adapters in addition to core features.

## Quick Start

```bash
# Launch web dashboard
masterchief --port 8080

# Example CLI checks
python -m core.cli.main health check
python -m core.cli.main module list
python -m core.cli.main script list
```

Dashboard default URL:
- http://localhost:8080

## Python Compatibility

- Core platform: Python 3.10+
- Full AI local GGUF runtime (llama-cpp-python): currently most reliable on Python 3.10-3.13
- Python 3.14: core works, but local GGUF loading may be unavailable until upstream wheels are available

If local GGUF cannot load, the platform still starts and other features continue to work.

## Requirements Files

- requirements.txt: core and integration dependencies expected by default modules
- requirements-optional.txt: heavy/optional AI, voice, async, and additional data tooling

To keep behavior consistent, always install both files for a fully loaded environment.

## Release and PyPI Harmony

Your repo is designed for GitHub-driven automation and PyPI publishing. Keep these in sync when releasing:

1. setup.py version
2. CHANGELOG.md release notes
3. requirements.txt and requirements-optional.txt dependency updates
4. README install and compatibility notes

This prevents CI, packaging metadata, and runtime behavior from drifting.

## Project Structure (high level)

- core/: CLI and core services
- echo/: Echo chat and runtime components
- addons/: addon modules and script integrations
- modules/: infrastructure modules
- scripts/: script library
- data/: runtime state and uploaded/generated content
- docs/: extended documentation

## License

MIT. See LICENSE.

## Support

- Open a GitHub issue for bugs and regressions
- Open a PR for fixes and improvements
