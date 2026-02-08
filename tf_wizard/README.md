TF Wizard — Terraform module generator

Quickstart

- Create and activate a Python venv

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r tf_wizard/requirements.txt
uvicorn tf_wizard.app:app --reload
```

- Open http://localhost:8000

Run helper scripts

Windows:

```bat
start_tf_wizard.bat
```

Linux/macOS:

```sh
./start_tf_wizard.sh
```

Install CLI

After installing the package (pip install -e .) the CLI is available as `tf_wizard`:

```bash
tf_wizard examples/aws.json -o mymodule.zip
```

Features

- Provider selection (AWS, Azure, GCP)
- Variable, resource, output definition (JSON input)
- Validation of inputs
- Generates a complete module and offers zip download
- Small unit test for generator

Advanced

- Paste a JSON Schema in the web UI to auto-generate variables (useful for typed module inputs)
- Provider-specific templates for cleaner provider blocks
