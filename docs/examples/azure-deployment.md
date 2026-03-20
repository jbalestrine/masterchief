# Example: Deploy Azure Infrastructure

This example demonstrates deploying a complete Azure infrastructure using MasterChief.

## Prerequisites
- Azure subscription
- Azure CLI configured
- MasterChief installed

## Deployment Steps

### 1. Initialize Project

```bash
python -m core.cli.main init --name azure-infrastructure
cd azure-infrastructure
```

### 2. Configure Environment

Create `config/environments/azure-prod.yaml`:

```yaml
environment: azure-prod
azure:
  subscription_id: "${env:AZURE_SUBSCRIPTION_ID}"
  resource_group: "prod-masterchief-rg"
  location: eastus2
```

### 3. Deploy

```bash
python -m core.cli.main deploy --environment azure-prod
```
