# Getting Started with MasterChief

This guide will walk you through setting up and using the MasterChief DevOps Automation Platform.

## Prerequisites

Before you begin, ensure you have:

- Python 3.10 or higher
- Azure CLI (for Azure deployments)
- Terraform 1.5+ (for Terraform modules)
- Ansible 2.14+ (for Ansible modules)
- PowerShell 7+ (for DSC modules)
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/jbalestrine/masterchief.git
cd masterchief
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
python3 scripts/python/masterchief.py list
```

You should see a list of available modules.

## Quick Start Guide

### Step 1: Configure Your Environment

Create your own environment configuration:

```bash
cp core/config/dev.yaml core/config/myenv.yaml
```

Edit `myenv.yaml` with your settings:

```yaml
config:
  azure:
    subscription_id: "your-subscription-id"
    tenant_id: "your-tenant-id"
    resource_group: "rg-myproject"
    region: "eastus"
    tags:
      environment: "myenv"
      project: "myproject"
  
  terraform:
    workspace: "myenv"
    backend:
      resource_group: "rg-tfstate"
      storage_account: "stmyprojecttfstate"
      container: "tfstate"

secrets:
  azure_client_id: "$AZURE_CLIENT_ID"
  azure_client_secret: "$AZURE_CLIENT_SECRET"
```

### Step 2: Set Up Azure Authentication

```bash
# Login to Azure
az login

# Set your subscription
az account set --subscription "your-subscription-id"

# Create service principal for automation
az ad sp create-for-rbac --name "masterchief-sp" --role="Contributor" --scopes="/subscriptions/your-subscription-id"

# Export credentials
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
```

### Step 3: Deploy Your First Infrastructure

Let's deploy a virtual network:

```bash
cd modules/terraform/azure-vnet

# Create terraform.tfvars
cat > terraform.tfvars << EOF
resource_group_name = "rg-myproject"
location            = "eastus"
vnet_name           = "vnet-myproject"
address_space       = ["10.0.0.0/16"]

subnets = {
  "subnet-web" = {
    address_prefix    = "10.0.1.0/24"
    service_endpoints = ["Microsoft.Storage", "Microsoft.KeyVault"]
  }
  "subnet-app" = {
    address_prefix    = "10.0.2.0/24"
    service_endpoints = ["Microsoft.Sql"]
  }
  "subnet-data" = {
    address_prefix = "10.0.3.0/24"
  }
}

nsg_rules = {
  "subnet-web" = [
    {
      name                       = "allow-https"
      priority                   = 100
      direction                  = "Inbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "*"
      destination_port_range     = "443"
      source_address_prefix      = "*"
      destination_address_prefix = "*"
    },
    {
      name                       = "allow-http"
      priority                   = 110
      direction                  = "Inbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "*"
      destination_port_range     = "80"
      source_address_prefix      = "*"
      destination_address_prefix = "*"
    }
  ]
}

tags = {
  project     = "myproject"
  cost_center = "engineering"
}

environment = "myenv"
EOF

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -out=tfplan

# Review the plan and apply
terraform apply tfplan

# Save outputs for later use
terraform output -json > vnet_outputs.json
```

### Step 4: Deploy AKS Cluster

Now let's deploy an AKS cluster using the VNet we just created:

```bash
cd ../azure-aks

# Create terraform.tfvars
cat > terraform.tfvars << EOF
resource_group_name = "rg-myproject"
location            = "eastus"
cluster_name        = "aks-myproject"
kubernetes_version  = "1.27.3"

# Use the subnet from our VNet
subnet_id = "$(terraform output -raw subnet_ids -state=../azure-vnet/terraform.tfstate | jq -r '.["subnet-app"]')"

default_node_pool = {
  name                = "system"
  vm_size             = "Standard_D4s_v3"
  node_count          = 3
  enable_auto_scaling = true
  min_count           = 2
  max_count           = 5
  os_disk_size_gb     = 128
  max_pods            = 30
  availability_zones  = ["1", "2", "3"]
}

additional_node_pools = {
  "user" = {
    vm_size             = "Standard_D8s_v3"
    node_count          = 2
    enable_auto_scaling = true
    min_count           = 1
    max_count           = 10
    node_labels = {
      workload = "user"
    }
  }
}

network_plugin = "azure"
network_policy = "azure"

enable_azure_policy = true
enable_oms_agent    = true

tags = {
  project     = "myproject"
  cost_center = "engineering"
}

environment = "myenv"
EOF

# Initialize and apply
terraform init
terraform plan -out=tfplan
terraform apply tfplan

# Get kubeconfig
az aks get-credentials --resource-group rg-myproject --name aks-myproject

# Verify cluster
kubectl get nodes
```

### Step 5: Configure VMs with Ansible

After deploying VMs (not shown in this example), configure them with Ansible:

```bash
cd ../../ansible

# Install Azure collection
ansible-galaxy collection install azure.azcollection

# Install Azure SDK
pip install -r requirements-azure.txt

# Test dynamic inventory
ansible-inventory -i inventory/azure_rm.yml --list

# Run playbook
ansible-playbook -i inventory/azure_rm.yml playbooks/site.yml

# Run for specific environment
ansible-playbook -i inventory/azure_rm.yml playbooks/site.yml --limit myenv
```

## Common Operations

### List Available Modules

```bash
python3 scripts/python/masterchief.py list

# Filter by type
python3 scripts/python/masterchief.py list --type terraform
```

### View Configuration

```bash
python3 scripts/python/masterchief.py config myenv
```

### Validate a Module

```bash
python3 scripts/python/masterchief.py validate modules/terraform/azure-vnet
```

### Create a New Module

```bash
python3 scripts/python/masterchief.py init terraform my-custom-module

cd modules/terraform/my-custom-module
# Edit the files to implement your module
```

## Example: Complete Infrastructure Stack

Here's an example of deploying a complete stack:

### 1. Network Infrastructure

```bash
# Deploy VNet
cd modules/terraform/azure-vnet
terraform init && terraform apply -auto-approve

# Save outputs
terraform output -json > ../../outputs/vnet.json
```

### 2. Security Infrastructure

```bash
# Deploy Key Vault
cd ../azure-keyvault

cat > terraform.tfvars << EOF
resource_group_name = "rg-myproject"
location            = "eastus"
keyvault_name       = "kv-myproject-001"
sku_name            = "standard"

access_policies = [
  {
    tenant_id = "your-tenant-id"
    object_id = "your-object-id"
    secret_permissions = ["Get", "List", "Set", "Delete"]
    key_permissions    = ["Get", "List", "Create"]
  }
]

secrets = {
  "db-password" = "$(openssl rand -base64 32)"
}

environment = "myenv"
EOF

terraform init && terraform apply -auto-approve
```

### 3. Storage Infrastructure

```bash
# Deploy Storage Account
cd ../azure-storage

cat > terraform.tfvars << EOF
resource_group_name   = "rg-myproject"
location              = "eastus"
storage_account_name  = "stmyproject001"

account_tier             = "Standard"
account_replication_type = "GRS"
access_tier              = "Hot"

enable_blob_versioning = true

containers = {
  "data" = {
    access_type = "private"
  }
  "backups" = {
    access_type = "private"
  }
}

file_shares = {
  "shared" = {
    quota_gb = 100
    tier     = "TransactionOptimized"
  }
}

environment = "myenv"
EOF

terraform init && terraform apply -auto-approve
```

### 4. Compute Infrastructure (AKS)

```bash
# Deploy AKS (shown in Step 4 above)
```

### 5. Configure All VMs

```bash
# Apply Ansible configuration
cd ../../ansible
ansible-playbook -i inventory/azure_rm.yml playbooks/site.yml
```

## Best Practices

### 1. Always Use Version Control

```bash
git add .
git commit -m "Deploy infrastructure for myproject"
git push
```

### 2. Use Remote State for Terraform

Configure in your backend:

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-tfstate"
    storage_account_name = "stmyprojecttfstate"
    container_name       = "tfstate"
    key                  = "myproject.terraform.tfstate"
  }
}
```

### 3. Tag All Resources

Always include tags for cost tracking and management:

```hcl
tags = {
  environment = "myenv"
  project     = "myproject"
  cost_center = "engineering"
  managed_by  = "masterchief"
  owner       = "your-email@example.com"
}
```

### 4. Use Environments

Separate environments properly:

- **dev**: Development and testing
- **staging**: Pre-production validation
- **prod**: Production workloads

### 5. Secure Your Secrets

Never commit secrets to version control:

```bash
# Add to .gitignore
echo "*.tfvars" >> .gitignore
echo "secrets/" >> .gitignore
```

Use environment variables or Key Vault:

```bash
export TF_VAR_admin_password="$(az keyvault secret show --vault-name kv-myproject --name admin-password --query value -o tsv)"
```

## Troubleshooting

### Terraform Issues

**Issue**: Provider authentication fails
```bash
# Solution: Ensure Azure credentials are set
az login
az account show
```

**Issue**: State file locked
```bash
# Solution: Force unlock (use with caution)
terraform force-unlock <lock-id>
```

### Ansible Issues

**Issue**: Dynamic inventory not working
```bash
# Solution: Verify Azure credentials
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_SECRET="your-client-secret"
export AZURE_TENANT="your-tenant-id"
```

**Issue**: SSH connection fails
```bash
# Solution: Check SSH keys and network connectivity
ssh-add ~/.ssh/id_rsa
ansible all -i inventory/azure_rm.yml -m ping
```

### Module Issues

**Issue**: Module not discovered
```bash
# Solution: Verify module.yaml exists and is valid
python3 -c "import yaml; yaml.safe_load(open('modules/terraform/my-module/module.yaml'))"
```

## Next Steps

- Read the [Module Development Guide](MODULE_DEVELOPMENT.md)
- Explore the [Architecture Documentation](ARCHITECTURE.md)
- Review example modules in `modules/`
- Check CI/CD workflows in `.github/workflows/`

## Getting Help

- Check documentation in `docs/`
- Review existing modules for examples
- Open an issue on GitHub
- Contact: support@balestrine-devops.com
