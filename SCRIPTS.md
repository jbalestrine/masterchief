# MasterChief Scripts Documentation

## Overview

The MasterChief platform includes a comprehensive library of DevOps automation scripts organized by category. All scripts follow consistent patterns for error handling, logging, and command-line interfaces.

## Directory Structure

```
scripts/devops/
├── deployment/      - Application and service deployment
├── infrastructure/  - Infrastructure provisioning and management
├── cicd/           - CI/CD pipeline automation
├── monitoring/     - Health checks and metrics collection
├── security/       - Security scanning and compliance
├── database/       - Database operations
└── utils/          - Utility and helper scripts
```

## Script Categories

### 1. Deployment Scripts (`deployment/`)

#### deploy-app.sh
Generic application deployment with validation and rollback support.

```bash
./deploy-app.sh --app myapp --env prod --version 1.2.3
./deploy-app.sh --app myapp --env staging --dry-run
```

**Options:**
- `--app APP_NAME` - Application name (required)
- `--env ENVIRONMENT` - Target environment: dev, staging, prod (required)
- `--version VERSION` - Application version (default: latest)
- `--dry-run` - Preview changes without applying
- `--help` - Show usage information

#### deploy-docker.sh
Deploy Docker containers with configuration validation.

```bash
./deploy-docker.sh --image nginx:latest --name web-server
```

#### deploy-kubernetes.sh
Deploy applications to Kubernetes clusters.

```bash
./deploy-kubernetes.sh --manifest deployment.yaml --namespace production
```

#### blue-green-deploy.sh
Blue/green deployment strategy for zero-downtime releases.

```bash
./blue-green-deploy.sh --app myapi --version 2.0.0 --env prod
```

#### rollback.sh
Rollback deployments to previous versions.

```bash
./rollback.sh --app myapp --env prod
```

### 2. Infrastructure Scripts (`infrastructure/`)

#### provision-vm.sh
Provision virtual machines on cloud providers (Azure, AWS, GCP).

```bash
./provision-vm.sh --provider azure --name production-vm-01
```

#### provision-aks.sh
Create and configure Azure Kubernetes Service clusters.

```bash
./provision-aks.sh --name my-cluster --resource-group my-rg --nodes 5
```

### 3. CI/CD Scripts (`cicd/`)

#### build-docker.sh
Build Docker images with proper tagging and validation.

```bash
./build-docker.sh --tag myapp:1.0.0 --file Dockerfile.prod
```

#### run-tests.sh
Execute test suites with optional coverage reporting.

```bash
./run-tests.sh --type unit --coverage
./run-tests.sh --type integration
```

#### security-scan.sh
Perform SAST/DAST security scanning on code and containers.

```bash
./security-scan.sh --target ./src --type sast
```

### 4. Monitoring Scripts (`monitoring/`)

#### check-health.sh
Health endpoint checker for services and applications.

```bash
./check-health.sh --url https://api.example.com/health --timeout 30
```

#### collect-metrics.sh
Collect Prometheus metrics from targets.

```bash
./collect-metrics.sh --target localhost:9090 --interval 60
```

### 5. Security Scripts (`security/`)

#### scan-vulnerabilities.sh
Scan for CVE vulnerabilities in applications and dependencies.

```bash
./scan-vulnerabilities.sh --target /app/src
```

#### rotate-secrets.sh
Automate secret rotation for services.

```bash
./rotate-secrets.sh --service myapi --dry-run
```

### 6. Database Scripts (`database/`)

#### backup-database.sh
Create database backups with timestamps.

```bash
./backup-database.sh --db production_db --output /backups
```

#### migrate-schema.sh
Run database schema migrations.

```bash
./migrate-schema.sh --db mydb --version 1.5.0
```

### 7. Utility Scripts (`utils/`)

#### cleanup-resources.sh
Clean up unused resources and artifacts.

```bash
./cleanup-resources.sh --type containers --dry-run
./cleanup-resources.sh --type images
```

#### cost-analyzer.sh
Analyze cloud infrastructure costs.

```bash
./cost-analyzer.sh --provider azure --report monthly-costs.txt
```

## Common Features

All scripts include:

- ✅ **Error Handling**: `set -euo pipefail` for safe execution
- ✅ **Help Documentation**: `--help` flag shows usage
- ✅ **Dry-Run Mode**: Test changes before applying
- ✅ **Colored Logging**: Visual feedback with INFO/WARN/ERROR
- ✅ **Exit Codes**: Proper codes for success/failure
- ✅ **Input Validation**: Required parameters checked

## Usage from CLI

Scripts can be executed via the MasterChief CLI:

```bash
# List all scripts
masterchief script list

# List scripts in specific category
masterchief script list --category deployment

# Execute a script
masterchief script run deploy-app.sh -- --app myapp --env dev --dry-run

# Execute with category hint
masterchief script run check-health.sh --category monitoring -- --url http://localhost

# Validate script syntax
masterchief script validate scripts/devops/deployment/deploy-app.sh

# Generate custom script
masterchief script generate --template deployment --output my-deploy.sh
```

## Script Wizard Integration

The Script Wizard provides AI-assisted script generation:

```bash
# Interactive generation
masterchief script generate --template deployment

# API endpoint
curl -X POST http://localhost:5000/api/script-wizard/generate \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "deployment",
    "parameters": {
      "app_name": "myapp",
      "environment": "prod"
    }
  }'
```

## Adding Custom Scripts

To add new scripts:

1. **Create Script**: Place in appropriate category directory
2. **Follow Template**: Use standard structure with shebang, help, error handling
3. **Make Executable**: `chmod +x script.sh`
4. **Test**: Run with `--dry-run` and `--help` flags
5. **Document**: Add entry to this file

### Script Template

```bash
#!/usr/bin/env bash
#
# script-name.sh - Brief description
#
# Usage:
#   script-name.sh --param VALUE [--help]
#

set -euo pipefail

# Parse arguments
PARAM=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --param) PARAM="$2"; shift 2 ;;
        --help|-h) sed -n '/^# Usage:/,/^$/p' "$0" | sed 's/^# //g'; exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# Validate inputs
[[ -z "$PARAM" ]] && { echo "ERROR: --param is required" >&2; exit 1; }

# Main logic
echo "[INFO] Executing with param: $PARAM"
echo "[INFO] Completed successfully"
exit 0
```

## Best Practices

1. **Always Use Dry-Run**: Test changes before applying to production
2. **Check Exit Codes**: Verify script success in automation
3. **Review Logs**: Check output for warnings and errors
4. **Version Control**: Store custom scripts in version control
5. **Environment Specific**: Use appropriate environment configurations
6. **Security First**: Never hardcode secrets in scripts

## Troubleshooting

### Script Not Found
```bash
# Verify script exists
masterchief script list

# Check file permissions
ls -l scripts/devops/deployment/deploy-app.sh
```

### Permission Denied
```bash
# Make script executable
chmod +x scripts/devops/deployment/deploy-app.sh
```

### Script Fails
```bash
# Run with verbose output
bash -x scripts/devops/deployment/deploy-app.sh --help

# Check script syntax
shellcheck scripts/devops/deployment/deploy-app.sh
```

## See Also

- [Platform Documentation](../docs/)
- [CLI Reference](../core/cli/)
- [Script Wizard](../platform/script_wizard/)
- [API Documentation](../platform/api.py)
