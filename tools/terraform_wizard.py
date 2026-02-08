"""Terraform + ARM Template Creator Wizard

Usage:
  python tools/terraform_wizard.py create --name myproj --cloud azure --out ./out
  python tools/terraform_wizard.py save --config ./out/config.json
  python tools/terraform_wizard.py load --config ./out/config.json
  python tools/terraform_wizard.py init --dir ./out
  python tools/terraform_wizard.py plan --dir ./out
  python tools/terraform_wizard.py deploy --dir ./out

This script generates a minimal Terraform project (best-practice defaults),
an ARM template (Azure) and a PowerShell deployment helper. It also supports
saving/loading the wizard configuration as JSON.

It wraps `terraform init`, `terraform plan` and `terraform apply` if Terraform
is available on PATH.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, List


@dataclass
class WizardConfig:
    name: str = "terraform_project"
    cloud: str = "azure"  # azure, aws, gcp
    backend: Dict[str, Any] = None
    provider_settings: Dict[str, Any] = None
    variables: Dict[str, Any] = None
    resources: List[Dict[str, Any]] = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


def safe_mkdir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def generate_provider_tf(cfg: WizardConfig, out: Path):
    lines = [
        'terraform {',
        '  required_version = ">= 1.0.0"',
        '  required_providers {',
    ]

    if cfg.cloud == "azure":
        lines += [
            '    azurerm = {',
            '      source = "hashicorp/azurerm"',
            '      version = ">= 3.0.0"',
            '    }',
        ]
    elif cfg.cloud == "aws":
        lines += [
            '    aws = {',
            '      source = "hashicorp/aws"',
            '      version = ">= 4.0.0"',
            '    }',
        ]
    else:
        lines += [
            '    google = {',
            '      source = "hashicorp/google"',
            '      version = ">= 4.0.0"',
            '    }',
        ]

    lines += [
        '  }',
        '}',
        "",
    ]

    if cfg.cloud == "azure":
        lines += [
            'provider "azurerm" {',
            '  features {}',
            '}',
        ]
    elif cfg.cloud == "aws":
        lines += [
            'provider "aws" {',
            '  region = var.region',
            '}',
        ]
    else:
        lines += [
            'provider "google" {',
            '  project = var.project',
            '  region  = var.region',
            '}',
        ]

    (out / "provider.tf").write_text("\n".join(lines))


def generate_variables_tf(cfg: WizardConfig, out: Path):
    lines = []
    defaults = cfg.variables or {}
    # common vars
    if cfg.cloud == "azure":
        defaults.setdefault("location", "eastus")
    else:
        defaults.setdefault("region", "us-east-1")

    for k, v in defaults.items():
        t = type(v)
        tf_type = "string"
        if t is int:
            tf_type = "number"
        elif t is bool:
            tf_type = "bool"

        lines += [
            f'variable "{k}" {{',
            f'  type = {"string" if tf_type=="string" else tf_type}',
            f'  default = {json.dumps(v)}',
            '}',
            '',
        ]

    (out / "variables.tf").write_text("\n".join(lines))


def generate_outputs_tf(out: Path):
    (out / "outputs.tf").write_text('')


def generate_main_tf(cfg: WizardConfig, out: Path):
    res_lines = []
    resources = cfg.resources or []
    # Minimal example resource for each cloud (best-practice defaults)
    if not resources:
        if cfg.cloud == "azure":
            resources = [
                {"type": "azurerm_resource_group", "name": f"rg_{cfg.name}", "args": {"name": f"rg-{cfg.name}", "location": "${var.location}"}}
            ]
        elif cfg.cloud == "aws":
            resources = [
                {"type": "aws_s3_bucket", "name": f"bucket_{cfg.name}", "args": {"bucket": f"{cfg.name}-bucket"}}
            ]
        else:
            resources = [
                {"type": "google_storage_bucket", "name": f"bucket_{cfg.name}", "args": {"name": f"{cfg.name}-bucket"}}
            ]

    for r in resources:
        rtype = r.get("type")
        rname = r.get("name")
        args = r.get("args", {})
        res_lines.append(f'resource "{rtype}" "{rname}" {{')
        for k, v in args.items():
            if isinstance(v, str) and v.startswith("${"):
                res_lines.append(f'  {k} = {v}')
            else:
                res_lines.append(f'  {k} = {json.dumps(v)}')
        res_lines.append('}')
        res_lines.append('')

    (out / "main.tf").write_text("\n".join(res_lines))


def generate_backend_tf(cfg: WizardConfig, out: Path):
    # Default to local backend but include commented remote backend template
    lines = [
        '# Default local backend for ease of getting started',
        'terraform {',
        '  backend "local" {',
        '    path = "terraform.tfstate"',
        '  }',
        '}',
        '',
        '# Example Azure storage backend (commented):',
        '# terraform {',
        '#   backend "azurerm" {',
        '#     resource_group_name  = "my-rg"',
        '#     storage_account_name = "mystorageacct"',
        '#     container_name       = "tfstate"',
        '#     key                  = "state.tfstate"',
        '#   }',
        '# }',
    ]

    (out / "backend.tf").write_text("\n".join(lines))


def generate_arm_template(cfg: WizardConfig, out: Path):
    # Minimal ARM template skeleton
    arm = {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {},
        "resources": [],
        "outputs": {},
    }
    # Add example resource group if requested
    arm["resources"].append({
        "type": "Microsoft.Resources/resourceGroups",
        "apiVersion": "2021-04-01",
        "name": f"rg-{cfg.name}",
        "location": "[parameters('location')]" if arm["parameters"] else cfg.provider_settings.get("location", "eastus") if cfg.provider_settings else "eastus",
    })

    (out / "arm_template.json").write_text(json.dumps(arm, indent=2))


def generate_powershell_deploy(out: Path, cfg: WizardConfig):
    lines = [
        '# PowerShell helper to deploy the ARM template to a resource group',
        'param(',
        "  [string]$ResourceGroupName = 'rg-{name}',".format(name=cfg.name),
        "  [string]$Location = 'eastus',",
        "  [string]$TemplateFile = 'arm_template.json'",
        ')',
        '',
        'if (-not (Get-Command az -ErrorAction SilentlyContinue)) {',
        "  Write-Error 'Azure CLI (az) is required to run this script.'",
        '  exit 1',
        '}',
        '',
        "az group create --name $ResourceGroupName --location $Location",
        "az deployment group create --resource-group $ResourceGroupName --template-file $TemplateFile",
    ]

    (out / "deploy-arm.ps1").write_text("\n".join(lines))


def save_config(cfg: WizardConfig, path: Path):
    path.write_text(cfg.to_json())


def load_config(path: Path) -> WizardConfig:
    data = json.loads(path.read_text())
    return WizardConfig(**data)


def run_terraform_command(cmd: List[str], cwd: Path):
    print("Running: ", " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(cwd))


def create_project(cfg: WizardConfig, out_dir: Path):
    safe_mkdir(out_dir)
    generate_backend_tf(cfg, out_dir)
    generate_provider_tf(cfg, out_dir)
    generate_variables_tf(cfg, out_dir)
    generate_main_tf(cfg, out_dir)
    generate_outputs_tf(out_dir)
    if cfg.cloud == "azure":
        # provider_settings may contain location
        cfg.provider_settings = cfg.provider_settings or {"location": "eastus"}
        generate_arm_template(cfg, out_dir)
        generate_powershell_deploy(out_dir, cfg)
    save_config(cfg, out_dir / "config.json")
    print(f"Project created at {out_dir}")


def generate_mock_docker_compose(cfg: WizardConfig, out_dir: Path):
        """Create a docker-compose based mock environment for local testing.

        Services provided by default:
            - azurite (Azure Storage emulator)
            - mssql (Microsoft SQL Server container) for Azure SQL emulation
            - vault (HashiCorp Vault) for secrets/keyvault-like testing

        The function writes `mock/docker-compose.yml`, a `mock/start_mock.sh` helper
        and a `mock/provider_overrides.tf` which provides guidance for pointing providers
        at local emulator endpoints.
        """
        mock_dir = out_dir / 'mock'
        mock_dir.mkdir(parents=True, exist_ok=True)

        compose = """version: '3.8'
services:
    azurite:
        image: mcr.microsoft.com/azure-storage/azurite
        container_name: azurite
        command: "azurite-blob --blobHost 0.0.0.0 --location /data --debug /dev/stderr"
        ports:
            - "10000:10000"
        volumes:
            - ./azurite_data:/data

    mssql:
        image: mcr.microsoft.com/mssql/server:2019-latest
        container_name: mssql
        environment:
            - ACCEPT_EULA=Y
            - SA_PASSWORD=Your_strong!Passw0rd
        ports:
            - "14333:1433"
        healthcheck:
            test: ["CMD-SHELL","/opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P \"Your_strong!Passw0rd\" -Q \"select 1\" || exit 1"]
        volumes:
            - ./mssql_data:/var/opt/mssql

    vault:
        image: vault:latest
        container_name: vault
        environment:
            - VAULT_DEV_ROOT_TOKEN_ID=root
            - VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200
        ports:
            - "8200:8200"
        command: server -dev -dev-root-token-id=root
"""

        (mock_dir / 'docker-compose.yml').write_text(compose, encoding='utf-8')

        start_sh = """#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
echo "Starting mock services via docker-compose..."
if command -v docker-compose >/dev/null 2>&1; then
    docker-compose -f "$HERE/docker-compose.yml" up -d
else
    docker compose -f "$HERE/docker-compose.yml" up -d
fi
echo "Mock services started. Azurite: http://localhost:10000  MSSQL: localhost:14333  Vault: http://localhost:8200 (token=root)"
"""

        shp = mock_dir / 'start_mock.sh'
        shp.write_text(start_sh, encoding='utf-8')
        shp.chmod(0o755)

        stop_sh = """#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
echo "Stopping mock services..."
if command -v docker-compose >/dev/null 2>&1; then
    docker-compose -f "$HERE/docker-compose.yml" down
else
    docker compose -f "$HERE/docker-compose.yml" down
fi
echo "Stopped mock services"
"""
        ssp = mock_dir / 'stop_mock.sh'
        ssp.write_text(stop_sh, encoding='utf-8')
        ssp.chmod(0o755)

        provider_overrides = []
        if cfg.cloud == 'azure':
                provider_overrides.append('provider "azurerm" {\n  features {}\n  skip_provider_registration = true\n}')
                # guidance for azurerm to use Azurite for storage operations
                provider_overrides.append('provider "azurerm" {\n  features {}\n  storage_endpoint = "http://127.0.0.1:10000"\n}')
        elif cfg.cloud == 'aws':
                provider_overrides.append('# For AWS, consider using localstack and set endpoints accordingly')
        (mock_dir / 'provider_overrides.tf').write_text('\n\n'.join(provider_overrides), encoding='utf-8')

        return mock_dir


def generate_mock_hyperv(cfg: WizardConfig, out_dir: Path):
    """Generate PowerShell scripts to create a minimal Hyper-V based mock environment.

    This writes to `<project>/mock/start_mock_hyperv.ps1` and `stop_mock_hyperv.ps1`.
    The scripts are designed to be run on Windows with Hyper-V enabled and require
    administrative privileges. They create a virtual switch and a small VM for
    testing (no cloud emulators built-in). This is intended as a convenience
    for local integration tests; the generated scripts include guidance.
    """
    mock_dir = out_dir / 'mock'
    mock_dir.mkdir(parents=True, exist_ok=True)

    start_ps1 = """
# Requires: run as Administrator and Hyper-V feature enabled
Import-Module Hyper-V
$ErrorActionPreference = 'Stop'
Write-Host 'Creating virtual switch (if not exists)'
if (-not (Get-VMSwitch -Name 'MasterChiefSwitch' -ErrorAction SilentlyContinue)) {{
    New-VMSwitch -Name 'MasterChiefSwitch' -SwitchType Internal
}

Write-Host 'Creating VHD for VM (if not exists)'
    $vhd = "${PSScriptRoot}\masterchief_mock.vhdx"
if (-not (Test-Path $vhd)) {
    New-VHD -Path $vhd -SizeBytes 20GB -Dynamic
    Initialize-Disk -VirtualDisk (Get-VHD -Path $vhd) -PartitionStyle MBR -PassThru | New-Partition -AssignDriveLetter -UseMaximumSize | Format-Volume -FileSystem NTFS -NewFileSystemLabel 'MockVM'
}

Write-Host 'Creating VM (if not exists)'
if (-not (Get-VM -Name 'MasterChiefMock' -ErrorAction SilentlyContinue)) {
    New-VM -Name 'MasterChiefMock' -MemoryStartupBytes 2GB -VHDPath $vhd -SwitchName 'MasterChiefSwitch'
}

Start-VM -Name 'MasterChiefMock'
Write-Host 'VM started: MasterChiefMock'
"""

    stop_ps1 = """
Import-Module Hyper-V
if (Get-VM -Name 'MasterChiefMock' -ErrorAction SilentlyContinue) {
    Stop-VM -Name 'MasterChiefMock' -Force -ErrorAction SilentlyContinue
    Remove-VM -Name 'MasterChiefMock' -Force -ErrorAction SilentlyContinue
}
if (Get-VMSwitch -Name 'MasterChiefSwitch' -ErrorAction SilentlyContinue) {
    # Optionally remove virtual switch - commented out by default
    # Remove-VMSwitch -Name 'MasterChiefSwitch' -Force
}
Write-Host 'Hyper-V mock stopped and cleaned up (VM removed)'
"""

    (mock_dir / 'start_mock_hyperv.ps1').write_text(start_ps1, encoding='utf-8')
    (mock_dir / 'stop_mock_hyperv.ps1').write_text(stop_ps1, encoding='utf-8')
    return mock_dir


def parse_args():
    p = argparse.ArgumentParser(description="Terraform + ARM Template Creator Wizard")
    sub = p.add_subparsers(dest="cmd")

    create = sub.add_parser("create")
    create.add_argument("--name", required=True)
    create.add_argument("--cloud", choices=["azure", "aws", "gcp"], default="azure")
    create.add_argument("--out", default="./tf_out")

    sub.add_parser("save").add_argument("--config", required=True)
    sub.add_parser("load").add_argument("--config", required=True)

    init = sub.add_parser("init")
    init.add_argument("--dir", default="./tf_out")

    plan = sub.add_parser("plan")
    plan.add_argument("--dir", default="./tf_out")

    deploy = sub.add_parser("deploy")
    deploy.add_argument("--dir", default="./tf_out")
    deploy.add_argument("--auto-approve", action="store_true")

    return p.parse_args()


def main():
    args = parse_args()
    if args.cmd == "create":
        cfg = WizardConfig(name=args.name, cloud=args.cloud)
        create_project(cfg, Path(args.out))

    elif args.cmd == "save":
        p = Path(args.config)
        cfg = load_config(Path("./tf_out/config.json"))
        save_config(cfg, p)
        print(f"Saved config to {p}")

    elif args.cmd == "load":
        cfg = load_config(Path(args.config))
        print(cfg.to_json())

    elif args.cmd == "init":
        cwd = Path(args.dir)
        run_terraform_command(["terraform", "init", "-input=false"], cwd)

    elif args.cmd == "plan":
        cwd = Path(args.dir)
        run_terraform_command(["terraform", "plan", "-out=tfplan", "-input=false"], cwd)

    elif args.cmd == "deploy":
        cwd = Path(args.dir)
        # apply the plan if present or directly apply
        planfile = cwd / "tfplan"
        if planfile.exists():
            cmd = ["terraform", "apply", "-input=false", "tfplan"]
        else:
            cmd = ["terraform", "apply", "-auto-approve"]
        if args.auto_approve and "-auto-approve" not in cmd:
            cmd.append("-auto-approve")
        run_terraform_command(cmd, cwd)

    else:
        print("No command specified; run --help for options")


def _prompt(prompt_text, default=None, choices=None, yes=False):
    if yes:
        return default
    if choices:
        prompt_text = f"{prompt_text} ({'/'.join(choices)})"
    if default is not None:
        prompt_text = f"{prompt_text} [{default}]: "
    else:
        prompt_text = f"{prompt_text}: "
    val = input(prompt_text).strip()
    if not val and default is not None:
        return default
    return val


def _ensure_project_structure(out_dir: Path):
    # root dirs
    (out_dir / 'modules').mkdir(parents=True, exist_ok=True)
    (out_dir / 'arm').mkdir(parents=True, exist_ok=True)
    (out_dir / 'environments').mkdir(parents=True, exist_ok=True)


def _write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def generate_module_scaffold(out_dir: Path, module_name: str, resources_hcl: str, variables_hcl: str = '', outputs_hcl: str = '', readme_text: str = ''):
    mod_dir = out_dir / 'modules' / module_name
    mod_dir.mkdir(parents=True, exist_ok=True)
    _write_file(mod_dir / 'main.tf', resources_hcl)
    # If no variables/outputs provided, generate sensible module-specific defaults
    if not variables_hcl:
        if module_name == 'vnet':
            variables_hcl = '''variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "address_space" { type = string }
variable "subnets" { type = list(object({ name = string, cidr = string })) }
'''
        elif module_name == 'storage' or module_name == 'fileshare':
            variables_hcl = '''variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "account_tier" { type = string }
variable "account_replication_type" { type = string }
'''
        elif module_name == 'keyvault':
            variables_hcl = '''variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "tenant_id" { type = string }
'''
        elif module_name == 'aks':
            variables_hcl = '''variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "node_count" { type = number }
variable "node_size" { type = string }
'''
        elif module_name == 'sql':
            variables_hcl = '''variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "sql_admin" { type = string }
variable "sql_password" { type = string }
'''
        elif module_name == 'private_endpoint':
            variables_hcl = '''variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "subnet_id" { type = string }
variable "target_resource_id" { type = string }
variable "subresource_names" { type = list(string) }
'''
        elif module_name == 'ilb':
            variables_hcl = '''variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "subnet_id" { type = string }
'''
        elif module_name == 'monitoring':
            variables_hcl = '''variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "target_resource_id" { type = string }
variable "log_analytics_workspace_id" { type = string }
'''
        elif module_name == 'rbac':
            variables_hcl = '''variable "scope" { type = string }
variable "role_definition_id" { type = string }
variable "principal_id" { type = string }
'''
        else:
            variables_hcl = '/* module variables */\n'

    if not outputs_hcl:
        if module_name == 'vnet':
            outputs_hcl = 'output "vnet_id" { value = azurerm_virtual_network.this.id }\n'
        elif module_name == 'storage' or module_name == 'fileshare':
            outputs_hcl = 'output "storage_account_id" { value = azurerm_storage_account.this.id }\n'
        elif module_name == 'keyvault':
            outputs_hcl = 'output "key_vault_id" { value = azurerm_key_vault.this.id }\n'
        elif module_name == 'aks':
            outputs_hcl = 'output "aks_cluster_name" { value = azurerm_kubernetes_cluster.this.name }\n'
        elif module_name == 'sql':
            outputs_hcl = 'output "sql_server_id" { value = azurerm_mssql_server.this.id }\n'
        else:
            outputs_hcl = '/* module outputs */\n'

    _write_file(mod_dir / 'variables.tf', variables_hcl)
    _write_file(mod_dir / 'outputs.tf', outputs_hcl)
    _write_file(mod_dir / 'README.md', readme_text or f"# {module_name} module\n\nThis module manages {module_name} resources.\nUsage: see variables.tf for required inputs.\n")


def _module_vnet(name_prefix: str):
        # Returns main.tf for vnet module
        hcl = """variable "name_prefix" { type = string }
variable "address_space" { type = string }
variable "subnets" { type = list(object({ name = string, cidr = string })) }

resource "azurerm_virtual_network" "this" {
    name                = "${var.name_prefix}-vnet"
    location            = var.location
    resource_group_name = var.resource_group_name
    address_space       = [var.address_space]
}

resource "azurerm_subnet" "subnets" {
    for_each = { for s in var.subnets : s.name => s }
    name                 = each.value.name
    resource_group_name  = var.resource_group_name
    virtual_network_name = azurerm_virtual_network.this.name
    address_prefixes     = [each.value.cidr]
}

output "vnet_id" { value = azurerm_virtual_network.this.id }
"""
        return hcl


def _module_storage(name_prefix: str):
        hcl = """variable "name_prefix" { type = string }
variable "resource_group_name" { type = string }

resource "azurerm_storage_account" "this" {
    name                     = lower(replace("${var.name_prefix}st", "-", ""))
    resource_group_name      = var.resource_group_name
    location                 = var.location
    account_tier             = "Standard"
    account_replication_type = "LRS"
    enable_https_traffic_only = true
    min_tls_version = "TLS1_2"
    network_rules {
        default_action = "Deny"
    }
    lifecycle { prevent_destroy = true }
}

    output "storage_account_id" { value = azurerm_storage_account.this.id }
"""
        return hcl


def _module_keyvault():
    hcl = """variable "name_prefix" { type = string }
variable "resource_group_name" { type = string }

resource "azurerm_key_vault" "this" {
  name                        = "${var.name_prefix}-kv"
  location                    = var.location
  resource_group_name         = var.resource_group_name
  tenant_id                   = var.tenant_id
  sku_name                    = "standard"
  purge_protection_enabled    = true
  soft_delete_retention_days  = 90
}

output "key_vault_id" { value = azurerm_key_vault.this.id }
"""
    return hcl


def _module_aks():
        hcl = '''variable "name_prefix" { type = string }
variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "node_count" { type = number }
variable "node_size" { type = string }
variable "enable_aad" { type = bool }
variable "enable_autoscaler" { type = bool }
variable "min_node_count" { type = number }
variable "max_node_count" { type = number }

resource "azurerm_kubernetes_cluster" "this" {
    name                = "${var.name_prefix}-aks"
    location            = var.location
    resource_group_name = var.resource_group_name

    api_server_authorized_ip_ranges = []

    default_node_pool {
        name       = "default"
        node_count = var.node_count
        vm_size    = var.node_size
        max_pods   = 110
        enable_auto_scaling = var.enable_autoscaler
        min_count = var.min_node_count
        max_count = var.max_node_count
    }

    identity {
        type = "SystemAssigned"
    }

    network_profile {
        network_plugin = "azure"
        network_policy = "azure"
        dns_service_ip = "10.0.0.10"
        service_cidr    = "10.0.0.0/16"
        docker_bridge_cidr = "172.17.0.1/16"
    }

    role_based_access_control {
        enabled = true
    }

    addon_profile {
        oms_agent {
            enabled = true
            log_analytics_workspace_id = var.log_analytics_workspace_id
        }
        azure_policy {
            enabled = true
        }
    }

    azure_active_directory_role_based_access_control {
        managed = var.enable_aad
    }

    tags = {
        ManagedBy = "masterchief"
    }
}

output "aks_cluster_name" { value = azurerm_kubernetes_cluster.this.name }
output "aks_kube_config" { value = azurerm_kubernetes_cluster.this.kube_admin_config_raw }
'''
        return hcl


def _module_sql():
        hcl = '''variable "name_prefix" { type = string }
variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "sql_admin" { type = string }
variable "sql_password" { type = string }
variable "enable_firewall" { type = bool }
variable "allowed_ips" { type = list(string) }

resource "azurerm_mssql_server" "this" {
    name                         = "${var.name_prefix}-sql"
    resource_group_name          = var.resource_group_name
    location                     = var.location
    administrator_login          = var.sql_admin
    administrator_login_password = var.sql_password
    version                      = "12.0"
    tags = { ManagedBy = "masterchief" }
}

resource "azurerm_mssql_database" "this" {
    name      = "${var.name_prefix}-db"
    server_id = azurerm_mssql_server.this.id
    sku_name  = "GP_Gen5_2"
    max_size_gb = 128
}

resource "azurerm_mssql_server_security_alert_policy" "this" {
    resource_group_name = var.resource_group_name
    server_name         = azurerm_mssql_server.this.name
    state               = "Enabled"
    email_account_admins = true
}

resource "azurerm_mssql_server_virtual_network_rule" "example" {
    count = var.enable_firewall ? length(var.allowed_ips) : 0
    name                = "vnetrule-${count.index}"
    resource_group_name = var.resource_group_name
    server_name         = azurerm_mssql_server.this.name
    subnet_id           = element(var.allowed_ips, count.index)
}

output "sql_server_id" { value = azurerm_mssql_server.this.id }
output "sql_database_id" { value = azurerm_mssql_database.this.id }
'''
        return hcl


def _module_private_endpoint():
    hcl = '''variable "name_prefix" { type = string }
variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "subnet_id" { type = string }
variable "subresource_names" { type = list(string) }
variable "target_resource_id" { type = string }

resource "azurerm_private_endpoint" "this" {
    name                = "${var.name_prefix}-pe"
    location            = var.location
    resource_group_name = var.resource_group_name
    subnet_id           = var.subnet_id

    dynamic "private_service_connection" {
        for_each = var.subresource_names
        content {
            name                           = "psc-${private_service_connection.value}"
            is_manual_connection           = false
            private_connection_resource_id = var.target_resource_id
            subresource_names              = [private_service_connection.value]
        }
    }
}

output "private_endpoint_id" { value = azurerm_private_endpoint.this.id }
'''
    return hcl


def _module_fileserver():
        hcl = '''variable "name_prefix" { type = string }
variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "share_name" { type = string }
variable "quota_gb" { type = number }
variable "replication" { type = string }

resource "azurerm_storage_account" "files_sa" {
    name                     = lower(replace("${var.name_prefix}files", "-", ""))
    resource_group_name      = var.resource_group_name
    location                 = var.location
    account_tier             = "Standard"
    account_replication_type = var.replication
    enable_https_traffic_only = true
    min_tls_version = "TLS1_2"
    network_rules {
        default_action = "Deny"
    }
    lifecycle { prevent_destroy = true }
}

resource "azurerm_storage_share" "fileshare" {
    name                 = var.share_name
    storage_account_name = azurerm_storage_account.files_sa.name
    quota                = var.quota_gb
}

output "fileshare_url" { value = azurerm_storage_share.fileshare.name }
'''
        return hcl


def _module_ilb():
    hcl = '''variable "name_prefix" { type = string }
variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "subnet_id" { type = string }
variable "backend_pool" { type = list(string) }

resource "azurerm_lb" "this" {
    name                = "${var.name_prefix}-ilb"
    location            = var.location
    resource_group_name = var.resource_group_name
    sku                 = "Standard"
    frontend_ip_configuration {
        name                 = "LoadBalancerFrontEnd"
        private_ip_address_allocation = "Static"
        subnet_id            = var.subnet_id
    }
}

resource "azurerm_lb_backend_address_pool" "pool" {
    name                = "backendpool"
    loadbalancer_id     = azurerm_lb.this.id
}

output "ilb_id" { value = azurerm_lb.this.id }
'''
    return hcl


def _module_monitoring():
        hcl = '''variable "name_prefix" { type = string }
variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "target_resource_id" { type = string }

resource "azurerm_log_analytics_workspace" "law" {
    name                = "${var.name_prefix}-law"
    location            = var.location
    resource_group_name = var.resource_group_name
    sku                 = "PerGB2018"
}

resource "azurerm_monitor_diagnostic_setting" "diagnostics" {
    name                       = "${var.name_prefix}-diag"
    target_resource_id         = var.target_resource_id
    log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
    log {
        category = "Administrative"
        enabled  = true
        retention_policy { enabled = true, days = 30 }
    }
    metric {
        category = "AllMetrics"
        enabled  = true
        retention_policy { enabled = true, days = 30 }
    }
}

output "log_analytics_workspace_id" { value = azurerm_log_analytics_workspace.law.id }
output "monitoring_configured" { value = true }
'''
        return hcl


def _module_rbac():
        hcl = '''variable "name_prefix" { type = string }
variable "resource_group_name" { type = string }
variable "role_definition_id" { type = string }
variable "principal_id" { type = string }

resource "azurerm_role_assignment" "this" {
    scope                = var.scope
    role_definition_id   = var.role_definition_id
    principal_id         = var.principal_id
}

output "role_assignment_id" { value = azurerm_role_assignment.this.id }
'''
        return hcl


def generate_root_files(cfg: WizardConfig, out_dir: Path, selected_modules: list):
    # backend.tf
    backend_lines = []
    if cfg.backend and cfg.backend.get('type') == 'azurerm':
        backend_lines = [
            'terraform {',
            '  backend "azurerm" {',
            f'    resource_group_name = "{cfg.backend.get("resource_group")}"',
            f'    storage_account_name = "{cfg.backend.get("storage_account")}"',
            f'    container_name = "{cfg.backend.get("container")}"',
            f'    key = "{cfg.name}/terraform.tfstate"',
            '  }',
            '}',
        ]
    else:
        backend_lines = [
            'terraform {',
            '  backend "local" {',
            '    path = "terraform.tfstate"',
            '  }',
            '}',
        ]
    _write_file(out_dir / 'backend.tf', '\n'.join(backend_lines))

    # providers.tf
    prov = []
    prov.append('terraform {')
    prov.append('  required_providers {')
    prov.append('    azurerm = { source = "hashicorp/azurerm" version = ">= 3.0.0" }')
    prov.append('  }')
    prov.append('}')
    prov.append('\nprovider "azurerm" {')
    prov.append('  features {}')
    prov.append('}')
    _write_file(out_dir / 'providers.tf', '\n'.join(prov))

    # locals (naming)
    locals_hcl = f"locals {{ prefix = \"{cfg.provider_settings.get('naming_prefix') if cfg.provider_settings else cfg.name}\" }}\n"
    _write_file(out_dir / 'locals.tf', locals_hcl)

    # variables
    vars_lines = []
    vars_map = cfg.variables or {}
    vars_lines.append('variable "environment" { type = string }')
    vars_lines.append('variable "location" { type = string }')
    if 'subscription_id' in vars_map or cfg.provider_settings and cfg.provider_settings.get('subscription_id'):
        vars_lines.append('variable "subscription_id" { type = string }')
    vars_lines.append('\n')
    _write_file(out_dir / 'variables.tf', '\n'.join(vars_lines))

    # main.tf references modules
    main_lines = []
    for m in selected_modules:
        main_lines.append(f'module "{m}" {{')
        main_lines.append(f'  source = "./modules/{m}"')
        main_lines.append(f'  name_prefix = local.prefix')
        main_lines.append('  resource_group_name = var.resource_group_name')
        main_lines.append('  location = var.location')
        main_lines.append('}')
        main_lines.append('')
    _write_file(out_dir / 'main.tf', '\n'.join(main_lines))

    # environment tfvars
    for env in ('dev','test','prod'):
        tfvars = {
            'environment': env,
            'location': cfg.provider_settings.get('location') if cfg.provider_settings else 'eastus',
        }
        _write_file(out_dir / f'environments/{env}.tfvars', json.dumps(tfvars, indent=2))

    # README
    readme = f"""# {cfg.name}

This repository was generated by the Terraform + ARM wizard.

Environments: dev, test, prod

Usage:

  terraform init -backend-config=... (see backend.tf)
  terraform plan -var-file=environments/dev.tfvars
  terraform apply -var-file=environments/dev.tfvars

Modules:
  - {' ,'.join(selected_modules)}

Follow Azure Well-Architected Framework defaults: resource tagging, diagnostics and secure defaults are applied where available.
"""
    _write_file(out_dir / 'README.md', readme)


def interactive_wizard(out: Path, yes: bool = False):
    # Interactive prompts following user's spec
    print('Interactive Terraform/ARM generator - Azure best-practice defaults')
    name = _prompt('Project name', default='enterprise-infra', yes=yes)
    sub_id = _prompt('Subscription ID', default='', yes=yes)
    tenant_id = _prompt('Tenant ID', default='', yes=yes)
    env = _prompt('Environment (dev/test/prod)', default='dev', choices=['dev','test','prod'], yes=yes)
    region = _prompt('Region', default='eastus', yes=yes)
    prefix = _prompt('Naming prefix', default=name, yes=yes)
    res_types = _prompt('Resource types (comma separated: vnet,storage,keyvault,aks,sql,private_endpoint,fileshare,ilb,monitoring,rbac,appservice)', default='vnet,storage,keyvault,aks,sql,fileshare,private_endpoint,monitoring,rbac', yes=yes)
    res_list = [r.strip() for r in res_types.split(',') if r.strip()]
    security = _prompt('Security posture (baseline/hardened)', default='baseline', choices=['baseline','hardened'], yes=yes)
    identity = _prompt('Identity model (system/user)', default='system', choices=['system','user'], yes=yes)
    networking = _prompt('Networking model (hub-spoke/flat)', default='hub-spoke', choices=['hub-spoke','flat'], yes=yes)
    backend_choice = _prompt('State backend (local/azurerm)', default='azurerm', choices=['local','azurerm'], yes=yes)

    cfg = WizardConfig(name=name, cloud='azure', backend={}, provider_settings={'subscription_id': sub_id, 'tenant_id': tenant_id, 'location': region, 'naming_prefix': prefix}, variables={'environment': env, 'location': region, 'subscription_id': sub_id}, resources=[])

    # backend config
    if backend_choice == 'azurerm':
        storage_account = _prompt('State storage account name', default=f'{prefix}st', yes=yes)
        container = _prompt('State container name', default='tfstate', yes=yes)
        rg = _prompt('State resource group', default=f'{prefix}-rg', yes=yes)
        cfg.backend = {'type': 'azurerm', 'storage_account': storage_account, 'container': container, 'resource_group': rg}

    out_dir = Path(out).resolve()
    _ensure_project_structure(out_dir)

    # generate modules requested
    selected = []
    for r in res_list:
        if r == 'vnet':
            generate_module_scaffold(out_dir, 'vnet', _module_vnet(prefix))
            selected.append('vnet')
        elif r == 'storage':
            generate_module_scaffold(out_dir, 'storage', _module_storage(prefix))
            selected.append('storage')
        elif r == 'keyvault':
            generate_module_scaffold(out_dir, 'keyvault', _module_keyvault())
            selected.append('keyvault')
        elif r == 'aks':
            generate_module_scaffold(out_dir, 'aks', _module_aks())
            selected.append('aks')
        elif r == 'sql':
            generate_module_scaffold(out_dir, 'sql', _module_sql())
            selected.append('sql')
        elif r == 'private_endpoint' or r == 'pe':
            generate_module_scaffold(out_dir, 'private_endpoint', _module_private_endpoint())
            selected.append('private_endpoint')
        elif r == 'fileshare' or r == 'file':
            generate_module_scaffold(out_dir, 'fileshare', _module_fileserver())
            selected.append('fileshare')
        elif r == 'ilb':
            generate_module_scaffold(out_dir, 'ilb', _module_ilb())
            selected.append('ilb')
        elif r == 'monitoring':
            generate_module_scaffold(out_dir, 'monitoring', _module_monitoring())
            selected.append('monitoring')
        elif r == 'rbac':
            generate_module_scaffold(out_dir, 'rbac', _module_rbac())
            selected.append('rbac')
        else:
            # placeholder module
            generate_module_scaffold(out_dir, r, f"/* module {r} - implement resource */\n")
            selected.append(r)

    # root files
    generate_root_files(cfg, out_dir, selected)
    print(f'Generated project at: {out_dir}')
    print('Run `terraform init` and then `terraform plan` with the desired environment tfvars file.')


if __name__ == "__main__":
    main()
