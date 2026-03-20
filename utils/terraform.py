"""
MasterChief Terraform Utilities

Contains Terraform-related utility classes and functions.
"""

import re
import uuid
import shutil
from pathlib import Path
from datetime import datetime


class EnterpriseTerraformGenerator:
    """
    Generates enterprise-grade Terraform projects from wizard configuration.
    """

    def __init__(self, output_base):
        self.output_base = Path(output_base)
        self.output_base.mkdir(parents=True, exist_ok=True)

    def generate(self, config, jobs_registry=None):
        """Generate a full enterprise Terraform project and return a job ID."""
        job_id = str(uuid.uuid4())[:8]
        project_name = config.get('project_name', 'enterprise-infra')
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '', project_name) or 'project'
        out_dir = self.output_base / f'{safe_name}_{job_id}'
        out_dir.mkdir(parents=True, exist_ok=True)

        self._write_providers(config, out_dir)
        self._write_backend(config, out_dir)
        self._write_variables(config, out_dir)
        self._write_locals(config, out_dir)
        self._write_modules(config, out_dir)

        # Create ZIP archive
        zip_path = out_dir.parent / f'{safe_name}_{job_id}.zip'
        shutil.make_archive(str(zip_path).replace('.zip', ''), 'zip', str(out_dir))

        job_record = {
            'id': job_id, 'path': str(zip_path), 'project_dir': str(out_dir),
            'name': project_name, 'created': datetime.now().isoformat()
        }
        if jobs_registry is not None:
            jobs_registry[job_id] = job_record
        return job_id, job_record

    def validate(self, config):
        """Validate the configuration and return any issues."""
        issues = []
        
        # Basic validation
        if not config.get('project_name'):
            issues.append({'type': 'error', 'field': 'project_name', 'message': 'Project name is required'})
        
        if not config.get('location'):
            issues.append({'type': 'warning', 'field': 'location', 'message': 'Location not specified, will use default'})
        
        # Validate CIDR blocks
        hub_cidr = config.get('network', {}).get('hub', {}).get('cidr', '')
        if hub_cidr:
            if not self._is_valid_cidr(hub_cidr):
                issues.append({'type': 'error', 'field': 'network.hub.cidr', 'message': 'Invalid CIDR format'})
        
        return issues

    def _is_valid_cidr(self, cidr):
        """Simple CIDR validation."""
        try:
            import ipaddress
            ipaddress.ip_network(cidr, strict=False)
            return True
        except:
            return False

    def _w(self, path, content):
        """Write content to file."""
        path.write_text(content, encoding='utf-8')

    def _write_providers(self, config, out_dir):
        self._w(out_dir / 'providers.tf', f"""terraform {{
  required_providers {{
    azurerm = {{
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }}
  }}
}}

provider "azurerm" {{
  features {{}}
  subscription_id = var.subscription_id
}}
""")

    def _write_backend(self, config, out_dir):
        backend_type = config.get('backend', 'azurerm')
        if backend_type == 'azurerm':
            self._w(out_dir / 'backend.tf', f"""terraform {{
  backend "azurerm" {{
    resource_group_name  = "{config.get('backend_rg', 'terraform-state')}"
    storage_account_name = "{config.get('backend_sa', 'tfstate123')}"
    container_name       = "tfstate"
    key                  = "{config.get('project_name', 'enterprise-infra')}.tfstate"
  }}
}}
""")

    def _write_variables(self, config, out_dir):
        self._w(out_dir / 'variables.tf', f"""variable "subscription_id" {{
  description = "Azure Subscription ID"
  type        = string
}}

variable "location" {{
  description = "Azure region"
  type        = string
  default     = "{config.get('location', 'East US')}"
}}

variable "environment" {{
  description = "Environment name"
  type        = string
  default     = "{config.get('environment', 'prod')}"
}}

variable "prefix" {{
  description = "Resource prefix"
  type        = string
  default     = "{config.get('prefix', 'ent')}"
}}
""")

    def _write_locals(self, config, out_dir):
        self._w(out_dir / 'locals.tf', f"""locals {{
  common_tags = {{
    Environment = var.environment
    Project     = "{config.get('project_name', 'enterprise-infra')}"
    ManagedBy   = "Terraform"
  }}

  resource_prefix = "${{var.prefix}}-${{var.environment}}"
}}
""")

    def _write_modules(self, config, out_dir):
        # Create modules directory
        mod_dir = out_dir / 'modules' / 'hub_network'
        mod_dir.mkdir(parents=True, exist_ok=True)

        # Main module files
        self._w(mod_dir / 'main.tf', f"""resource "azurerm_resource_group" "hub" {{
  name     = "${{local.resource_prefix}}-hub-rg"
  location = var.location
  tags     = local.common_tags
}}

resource "azurerm_virtual_network" "hub" {{
  name                = "${{local.resource_prefix}}-hub-vnet"
  location            = azurerm_resource_group.hub.location
  resource_group_name = azurerm_resource_group.hub.name
  address_space       = ["10.0.0.0/16"]
  tags                = local.common_tags
}}

resource "azurerm_subnet" "firewall" {{
  name                 = "AzureFirewallSubnet"
  resource_group_name  = azurerm_resource_group.hub.name
  virtual_network_name = azurerm_virtual_network.hub.name
  address_prefixes     = ["10.0.0.0/26"]
}}

resource "azurerm_subnet" "gateway" {{
  name                 = "GatewaySubnet"
  resource_group_name  = azurerm_resource_group.hub.name
  virtual_network_name = azurerm_virtual_network.hub.name
  address_prefixes     = ["10.0.1.0/27"]
}}

resource "azurerm_subnet" "bastion" {{
  name                 = "AzureBastionSubnet"
  resource_group_name  = azurerm_resource_group.hub.name
  virtual_network_name = azurerm_virtual_network.hub.name
  address_prefixes     = ["10.0.1.32/27"]
}}
""")

        self._w(mod_dir / 'variables.tf', f"""variable "prefix" {{ type = string }}
variable "location" {{ type = string }}
variable "environment" {{ type = string }}

locals {{
  common_tags = {{
    Environment = var.environment
    Project     = "{config.get('project_name', 'enterprise-infra')}"
    ManagedBy   = "Terraform"
  }}

  resource_prefix = "${{var.prefix}}-${{var.environment}}"
}}
""")

        self._w(mod_dir / 'outputs.tf', """output "hub_vnet_id" { value = azurerm_virtual_network.hub.id }
output "hub_resource_group_name" { value = azurerm_resource_group.hub.name }
output "firewall_subnet_id" { value = azurerm_subnet.firewall.id }
output "gateway_subnet_id" { value = azurerm_subnet.gateway.id }
output "bastion_subnet_id" { value = azurerm_subnet.bastion.id }
""")

        # Root module
        self._w(out_dir / 'main.tf', f"""module "hub_network" {{
  source = "./modules/hub_network"

  prefix      = var.prefix
  location    = var.location
  environment = var.environment
}}

# Additional enterprise resources can be added here
""")