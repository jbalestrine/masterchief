# Ansible Integration for MasterChief Platform

This directory contains Ansible playbooks, roles, and inventory configurations for the MasterChief DevOps automation platform.

## Directory Structure

```
ansible/
├── inventory/           # Inventory files and dynamic inventory scripts
│   ├── azure_rm.yml    # Azure dynamic inventory
│   └── hosts/          # Static inventory files
├── roles/              # Ansible roles
│   ├── common/         # Common configuration for all hosts
│   ├── webserver/      # Web server configuration
│   └── database/       # Database server configuration
└── playbooks/          # Ansible playbooks
    ├── site.yml        # Main playbook
    └── templates/      # Playbook templates
```

## Requirements

- Ansible 2.14+
- Python 3.10+
- Azure collection: `ansible-galaxy collection install azure.azcollection`
- Azure SDK: `pip install -r requirements-azure.txt`

## Usage

### Dynamic Inventory

Use Azure Resource Manager dynamic inventory:

```bash
ansible-inventory -i inventory/azure_rm.yml --list
```

### Run Playbooks

```bash
# Run site-wide configuration
ansible-playbook -i inventory/azure_rm.yml playbooks/site.yml

# Run specific playbook
ansible-playbook -i inventory/azure_rm.yml playbooks/webserver-setup.yml

# Limit to specific environment
ansible-playbook -i inventory/azure_rm.yml playbooks/site.yml --limit dev
```

### Integration with Terraform

Terraform outputs can be used to populate Ansible inventory:

```bash
# Export Terraform outputs
terraform output -json > /tmp/tf_outputs.json

# Use in Ansible
ansible-playbook -e "@/tmp/tf_outputs.json" playbooks/site.yml
```

## Best Practices

1. **Use tags**: Tag resources in Azure for dynamic inventory filtering
2. **Vault secrets**: Use Ansible Vault for sensitive data
3. **Role dependencies**: Define clear role dependencies
4. **Idempotency**: Ensure all tasks are idempotent
5. **Testing**: Test roles with molecule before deployment
