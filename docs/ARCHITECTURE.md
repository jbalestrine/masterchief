# Platform Architecture

## Overview

MasterChief is a modular DevOps automation platform designed around a plugin-based architecture that enables extensibility and maintainability.

## Core Components

### 1. Module Loader

**Location**: `core/module-loader/`

The module loader provides dynamic discovery and loading of platform modules.

**Key Features**:
- Automatic module discovery from the modules directory
- Manifest-based module registration (module.yaml)
- Dependency resolution and validation
- Type-specific module loading (Terraform, Ansible, DSC)

**Module Discovery Process**:
1. Scan modules directory for subdirectories
2. Look for module.yaml manifest files
3. Parse and validate manifest
4. Register module with the platform
5. Resolve dependencies

### 2. Configuration Manager

**Location**: `core/config/`

Hierarchical configuration system with environment-based settings.

**Key Features**:
- Global configuration (applies to all environments)
- Environment-specific configuration (dev, staging, prod)
- Configuration inheritance (child inherits from parent)
- Secret management integration
- Variable override system

**Configuration Hierarchy**:
```
Global Config (global.yaml)
    ↓
Environment Config (dev.yaml)
    ↓
Child Environment (staging.yaml) → inherits from dev
```

### 3. Logging System

**Location**: `core/logging/`

Centralized logging with multiple output targets.

**Key Features**:
- Structured logging with log levels
- Console and file output
- Module lifecycle event logging
- Deployment event tracking
- Dynamic log level adjustment

### 4. Module API

**Location**: `core/api/`

Internal API for inter-module communication.

**Key Features**:
- Module registration and lifecycle management
- Message passing between modules
- Event system for module events
- State management
- Interface definition and validation

## Module System

### Module Types

#### Terraform Modules
- Infrastructure as Code for cloud resources
- Provider-agnostic (Azure focus)
- Standard structure: main.tf, variables.tf, outputs.tf
- Module manifest defines inputs/outputs

#### Ansible Modules
- Configuration management and orchestration
- Role-based organization
- Dynamic inventory support
- Integration with Terraform outputs

#### PowerShell DSC Modules
- Windows server configuration
- Declarative configuration
- MOF compilation and deployment
- Integration with CI/CD

### Module Manifest

Every module includes a `module.yaml` manifest:

```yaml
name: "module-name"
version: "1.0.0"
type: "terraform|ansible|powershell-dsc"
description: "Module description"
author: "Author name"
dependencies: []  # Other modules required
inputs: {}        # Expected inputs
outputs: {}       # Provided outputs
metadata: {}      # Additional metadata
```

### Module Lifecycle

1. **Discovery**: Module loader scans directory
2. **Registration**: Module registered with API
3. **Validation**: Dependencies validated
4. **Loading**: Module loaded into memory
5. **Execution**: Module deployed/applied
6. **Monitoring**: State tracked via API

## Data Flow

### Configuration Flow

```
User Input
    ↓
Environment Config (YAML)
    ↓
ConfigManager (merge with global)
    ↓
Module Execution
    ↓
Infrastructure/Config Change
```

### Module Communication Flow

```
Module A
    ↓
ModuleAPI.send_message()
    ↓
Message Handler
    ↓
Module B.handle_message()
    ↓
Response
```

## Integration Points

### Terraform ↔ Ansible

Terraform outputs can be consumed by Ansible:

```hcl
# Terraform output
output "vm_ips" {
  value = { for k, v in azurerm_virtual_machine.vms : k => v.private_ip_address }
}
```

```yaml
# Ansible playbook
- name: Configure VMs
  hosts: localhost
  tasks:
    - name: Add hosts from Terraform
      add_host:
        name: "{{ item.value }}"
        groups: vms
      loop: "{{ terraform_outputs.vm_ips | dict2items }}"
```

### Ansible ↔ PowerShell DSC

Ansible can trigger DSC configuration:

```yaml
- name: Apply DSC configuration
  win_dsc:
    resource_name: File
    Ensure: Present
    DestinationPath: C:\Config\app.config
```

### Module API Integration

Modules communicate via the Module API:

```python
from core.api import get_module_api

api = get_module_api()

# Register module
api.register_module("my-module", "terraform", {
    "deploy": deploy_function,
    "destroy": destroy_function
})

# Send message to another module
api.send_message(ModuleMessage(
    source="my-module",
    target="other-module",
    action="get_config",
    payload={}
))
```

## Security Considerations

### Secret Management

Secrets are handled through:
1. Environment variables (default)
2. Azure Key Vault integration
3. GitHub Secrets for CI/CD

Secrets are never stored in code or configuration files.

### Access Control

- Module-level permissions
- Environment-based access
- RBAC through Azure AD (for Azure resources)
- SSH key-based authentication (Ansible)

### Network Security

- Network segmentation via NSGs
- Private endpoints for Azure services
- Firewall rules managed by modules
- Bastion hosts for secure access

## Extensibility

### Adding New Module Types

1. Create module type directory: `modules/new-type/`
2. Define module template
3. Implement loader in `ModuleLoader._load_newtype_module()`
4. Add validation in CLI
5. Create CI/CD workflow

### Custom Hooks

Implement hooks for module lifecycle events:

```python
api.register_event_handler("module.*.deploy", pre_deploy_hook)
api.register_event_handler("module.*.deployed", post_deploy_hook)
```

### Plugin Architecture

Extend platform functionality with plugins:

```python
class MyPlugin:
    def on_load(self):
        # Plugin initialization
        pass
    
    def on_module_deploy(self, module):
        # Hook into deployment
        pass
```

## CI/CD Pipeline

### Validation Pipeline

```
Code Push
    ↓
Syntax Validation (format, lint)
    ↓
Module Validation (structure, manifest)
    ↓
Security Scan (checkov, ansible-lint)
    ↓
Unit Tests
    ↓
✓ Pass / ✗ Fail
```

### Deployment Pipeline

```
Manual Trigger / PR Merge
    ↓
Load Environment Config
    ↓
Validate Dependencies
    ↓
Plan Changes (Terraform)
    ↓
Manual Approval (prod only)
    ↓
Apply Changes
    ↓
Verify Deployment
    ↓
Update State
```

## Performance Considerations

### Module Loading

- Lazy loading: Modules loaded only when needed
- Caching: Loaded modules cached in memory
- Parallel discovery: Multiple modules discovered concurrently

### Configuration Management

- Config inheritance reduces duplication
- Merged configs cached per environment
- Lazy secret loading

### Deployment

- Parallel deployment option for independent modules
- Resource tagging for tracking
- State management for idempotency

## Monitoring and Observability

### Logging Levels

- **DEBUG**: Detailed execution information
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical failures

### Event Tracking

Platform tracks:
- Module lifecycle events (load, deploy, destroy)
- Configuration changes
- Deployment events
- API calls
- Errors and failures

### Metrics

Key metrics collected:
- Module deployment time
- Success/failure rates
- Resource counts
- Configuration drift

## Best Practices

### Module Development

1. Keep modules focused and single-purpose
2. Define clear inputs and outputs
3. Support standard tags and labels
4. Make modules composable
5. Include comprehensive documentation

### Configuration Management

1. Use environment inheritance
2. Keep secrets out of configuration files
3. Validate configuration before use
4. Version control all configuration
5. Document configuration options

### Deployment

1. Always plan before apply
2. Use manual approval for production
3. Implement rollback procedures
4. Monitor deployment progress
5. Verify after deployment

## Future Enhancements

### Planned Features

- Webhook support for external integrations
- GUI dashboard for platform management
- Advanced dependency graph visualization
- Multi-cloud support (AWS, GCP)
- Cost estimation and tracking
- Drift detection and remediation
- Automated testing framework
- Module marketplace

### Roadmap

**Phase 1** (Current): Core platform and Azure modules
**Phase 2**: Advanced orchestration and GUI
**Phase 3**: Multi-cloud expansion
**Phase 4**: Enterprise features (SSO, audit, compliance)
