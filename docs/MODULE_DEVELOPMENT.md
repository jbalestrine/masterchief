# Module Development Guide

This guide explains how to create new modules for the MasterChief platform.

## Module Types

The platform supports three module types:
1. **Terraform**: Infrastructure as Code for cloud resources
2. **Ansible**: Configuration management and automation
3. **PowerShell DSC**: Windows server configuration

## Module Structure

### Required Files

Every module must include:

1. **module.yaml**: Module manifest with metadata
2. **README.md**: Module documentation

Type-specific requirements:

**Terraform modules:**
- `main.tf`: Resource definitions
- `variables.tf`: Input variables
- `outputs.tf`: Output values
- `versions.tf`: Provider version constraints

**Ansible modules:**
- `playbook.yml` or `tasks/main.yml`: Ansible tasks
- `defaults/main.yml`: Default variables
- `meta/main.yml`: Role metadata

**PowerShell DSC modules:**
- `Configuration.ps1`: DSC configuration script

## Module Manifest

The `module.yaml` file defines module metadata:

```yaml
name: "module-name"
version: "1.0.0"
type: "terraform"  # or ansible, powershell-dsc
description: "Brief description"
author: "Your Name"

dependencies: []  # List of required modules
  # - "dependency-module-name"

inputs:
  # Define expected inputs
  input_name:
    type: "string"
    description: "Input description"
    required: true
    default: null

outputs:
  # Define outputs
  output_name:
    type: "string"
    description: "Output description"

metadata:
  category: "networking"  # infrastructure, compute, storage, security, etc.
  azure_services: []  # List of Azure services used
  terraform_version: ">=1.5.0"  # Version constraints
```

## Creating a Terraform Module

### Step 1: Initialize Module

```bash
python scripts/python/masterchief.py init terraform my-module
cd modules/terraform/my-module
```

### Step 2: Define Resources (main.tf)

```hcl
# Example: Simple resource group module
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = merge(
    var.tags,
    {
      environment = var.environment
      managed_by  = "masterchief"
    }
  )
}
```

### Step 3: Define Variables (variables.tf)

```hcl
variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}
```

### Step 4: Define Outputs (outputs.tf)

```hcl
output "resource_group_id" {
  description = "Resource group ID"
  value       = azurerm_resource_group.main.id
}

output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.main.name
}
```

### Step 5: Configure Providers (versions.tf)

```hcl
terraform {
  required_version = ">=1.5.0"
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">=3.0.0"
    }
  }
}

provider "azurerm" {
  features {}
}
```

### Step 6: Document Module (README.md)

```markdown
# My Module

Description of what the module does.

## Features

- Feature 1
- Feature 2

## Usage

\`\`\`hcl
module "my_module" {
  source = "../../modules/terraform/my-module"
  
  resource_group_name = "rg-example"
  location            = "eastus"
  tags                = {
    project = "example"
  }
}
\`\`\`

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| resource_group_name | Resource group name | string | - | yes |

## Outputs

| Name | Description |
|------|-------------|
| resource_group_id | Resource group ID |
```

## Creating an Ansible Role

### Step 1: Initialize Role Structure

```bash
mkdir -p modules/ansible/roles/my-role/{tasks,handlers,templates,defaults,vars,meta,files}
```

### Step 2: Define Tasks (tasks/main.yml)

```yaml
---
- name: Install packages
  package:
    name: "{{ my_packages }}"
    state: present

- name: Configure service
  template:
    src: config.j2
    dest: /etc/myservice/config.conf
    mode: '0644'
  notify: restart service

- name: Start service
  systemd:
    name: myservice
    state: started
    enabled: yes
```

### Step 3: Define Defaults (defaults/main.yml)

```yaml
---
my_packages:
  - package1
  - package2

my_config_option: "default_value"
```

### Step 4: Define Handlers (handlers/main.yml)

```yaml
---
- name: restart service
  systemd:
    name: myservice
    state: restarted
```

### Step 5: Add Metadata (meta/main.yml)

```yaml
---
galaxy_info:
  author: Your Name
  description: Role description
  license: MIT
  min_ansible_version: 2.14
  platforms:
    - name: Ubuntu
      versions:
        - focal
        - jammy

dependencies: []
```

### Step 6: Create Module Manifest (module.yaml)

```yaml
name: "my-role"
version: "1.0.0"
type: "ansible"
description: "Role description"
author: "Your Name"
dependencies: []
inputs:
  my_config_option:
    type: "string"
    description: "Configuration option"
    required: false
    default: "default_value"
outputs: {}
metadata:
  category: "configuration"
```

## Creating a PowerShell DSC Configuration

### Step 1: Create Configuration Script

```powershell
# Configuration.ps1
Configuration MyConfiguration
{
    param(
        [Parameter(Mandatory=$false)]
        [string]$ComputerName = "localhost",
        
        [Parameter(Mandatory=$false)]
        [hashtable]$ConfigurationData
    )
    
    Import-DscResource -ModuleName PSDesiredStateConfiguration
    
    Node $ComputerName
    {
        # Install Windows feature
        WindowsFeature MyFeature
        {
            Ensure = "Present"
            Name = "Web-Server"
        }
        
        # Configure service
        Service MyService
        {
            Name = "W3SVC"
            State = "Running"
            StartupType = "Automatic"
            DependsOn = "[WindowsFeature]MyFeature"
        }
        
        # Configure firewall
        Firewall MyFirewallRule
        {
            Name = "Allow-HTTP"
            Ensure = "Present"
            Enabled = "True"
            Direction = "Inbound"
            Protocol = "TCP"
            LocalPort = "80"
            Action = "Allow"
        }
    }
}
```

### Step 2: Create Module Manifest

```yaml
name: "my-configuration"
version: "1.0.0"
type: "powershell-dsc"
description: "Windows server configuration"
author: "Your Name"
dependencies: []
inputs:
  computer_name:
    type: "string"
    description: "Target computer name"
    required: false
    default: "localhost"
outputs: {}
metadata:
  category: "configuration"
  required_modules:
    - PSDesiredStateConfiguration
```

## Best Practices

### General Guidelines

1. **Modularity**: Create small, focused modules
2. **Reusability**: Make modules configurable and reusable
3. **Documentation**: Include comprehensive README with examples
4. **Testing**: Test modules in development before production
5. **Versioning**: Use semantic versioning (MAJOR.MINOR.PATCH)

### Terraform-Specific

1. **Variables**: Use consistent naming (snake_case)
2. **Tags**: Always support tags parameter
3. **Outputs**: Return resource IDs and essential attributes
4. **Validation**: Add variable validation where appropriate
5. **Dependencies**: Use depends_on for explicit dependencies

### Ansible-Specific

1. **Idempotency**: Ensure tasks can run multiple times safely
2. **Variables**: Use role defaults for configuration
3. **Handlers**: Use handlers for service restarts
4. **Facts**: Gather facts when needed, skip when not
5. **Conditions**: Use when clauses for conditional execution

### PowerShell DSC-Specific

1. **Resources**: Use built-in resources when available
2. **Dependencies**: Define resource dependencies explicitly
3. **Configuration Data**: Support configuration data separation
4. **Testing**: Test compilation before deployment
5. **Idempotency**: DSC resources should be idempotent by design

## Testing Modules

### Terraform Modules

```bash
cd modules/terraform/my-module

# Format check
terraform fmt -check

# Initialize
terraform init -backend=false

# Validate
terraform validate

# Plan (requires valid credentials)
terraform plan
```

### Ansible Roles

```bash
cd modules/ansible

# Syntax check
ansible-playbook --syntax-check playbooks/my-playbook.yml

# Lint
ansible-lint roles/my-role/

# Dry run
ansible-playbook playbooks/my-playbook.yml --check
```

### PowerShell DSC

```powershell
cd modules/powershell-dsc

# Compile configuration
.\scripts\Compile-Configuration.ps1 `
    -ConfigurationName "MyConfiguration" `
    -OutputPath "test"

# Test configuration
Test-DscConfiguration -Path "test"
```

## Publishing Modules

### Validation Checklist

Before publishing a module, ensure:

- [ ] Module manifest (module.yaml) is complete
- [ ] README.md includes usage examples
- [ ] All required files are present
- [ ] Code passes linting/validation
- [ ] Module has been tested
- [ ] Version number follows semantic versioning
- [ ] Dependencies are documented

### Submission Process

1. Create module following guidelines
2. Validate module: `python scripts/python/masterchief.py validate modules/{type}/{name}`
3. Commit to version control
4. CI/CD will automatically validate
5. Create pull request for review

## Advanced Topics

### Module Dependencies

Specify dependencies in module.yaml:

```yaml
dependencies:
  - "azure-vnet"
  - "azure-keyvault"
```

The module loader will ensure dependencies are loaded first.

### Custom Resources

For advanced scenarios, create custom resources:

**Terraform**: Use null_resource or custom providers
**Ansible**: Create custom modules in library/
**DSC**: Create custom DSC resources

### Integration Points

Modules can integrate through:

1. **Outputs**: Pass data between modules
2. **Shared state**: Use remote state (Terraform)
3. **Facts**: Share data via Ansible facts
4. **Configuration**: Share via ConfigManager

## Getting Help

- Review existing modules for examples
- Check documentation in docs/
- Run CLI with --help flag
- Open an issue on GitHub
