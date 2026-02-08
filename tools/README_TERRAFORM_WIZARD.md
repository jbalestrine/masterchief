Terraform + ARM Template Creator Wizard
=====================================

File: tools/terraform_wizard.py

Quick start
-----------

- Create a project (Azure example):

```powershell
python tools/terraform_wizard.py create --name myapp --cloud azure --out .\myapp_tf
```

- Initialize terraform:

```powershell
python tools/terraform_wizard.py init --dir .\myapp_tf
```

- Plan:

```powershell
python tools/terraform_wizard.py plan --dir .\myapp_tf
```

- Deploy (Terraform apply):

```powershell
python tools/terraform_wizard.py deploy --dir .\myapp_tf --auto-approve
```

Notes
-----
- The script generates a default `main.tf`, `variables.tf`, `provider.tf`, `backend.tf`,
  a `config.json`, an `arm_template.json` and `deploy-arm.ps1` for Azure.
- It defaults to a local backend for easy getting started; example remote backend
  snippets are included commented in `backend.tf`.
- The script will call `terraform` commands directly when running `init`, `plan`,
  or `deploy`. Ensure `terraform` is installed and on PATH.

Extending
---------
- The `WizardConfig` dataclass is the canonical configuration; load/save JSON to
  customize resources and variables.
