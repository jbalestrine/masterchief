# MasterChief Runbooks

## Overview

This directory contains operational runbooks for managing and troubleshooting the MasterChief platform.

## Available Runbooks

### Platform Operations

- [Platform Startup](platform-startup.md)
- [Platform Shutdown](platform-shutdown.md)
- [Configuration Update](config-update.md)
- [Module Management](module-management.md)

### Deployment Operations

- [Infrastructure Deployment](infrastructure-deployment.md)
- [Application Deployment](application-deployment.md)
- [Rollback Procedures](rollback.md)
- [Blue-Green Deployment](blue-green-deployment.md)

### Incident Response

- [High CPU Usage](incidents/high-cpu.md)
- [Database Connection Issues](incidents/database-issues.md)
- [Network Connectivity Problems](incidents/network-issues.md)
- [API Errors](incidents/api-errors.md)

### Maintenance

- [Backup Procedures](maintenance/backup.md)
- [Database Maintenance](maintenance/database.md)
- [Certificate Renewal](maintenance/certificates.md)
- [Security Updates](maintenance/security-updates.md)

## Quick Reference

### Emergency Contacts

| Role | Contact | Escalation |
|------|---------|------------|
| Platform Admin | platform-admin@example.com | manager@example.com |
| Security Team | security@example.com | ciso@example.com |
| Network Team | network@example.com | network-lead@example.com |

### Common Commands

```bash
# Check platform status
masterchief status

# View logs
masterchief logs --follow --tail 100

# List modules
masterchief module list

# Deploy with plan
masterchief deploy --plan

# Interactive mode
masterchief interactive
```

### Health Check Endpoints

- Platform API: `http://localhost:8000/health`
- Prometheus Metrics: `http://localhost:9090/metrics`
- Database: `psql -h localhost -U masterchief -c "SELECT 1"`

### Log Locations

- Platform logs: `/var/log/masterchief/platform.log`
- Module logs: `/var/log/masterchief/modules/`
- Audit logs: `/var/log/masterchief/audit.log`
- IRC bot logs: `/var/log/masterchief/irc/bot.log`

## Runbook Template

When creating new runbooks, use this template:

```markdown
# [Runbook Title]

## Overview
Brief description of the procedure.

## Prerequisites
- Required tools
- Required access
- Required knowledge

## Procedure

### Step 1: [Action]
Detailed instructions...

### Step 2: [Action]
Detailed instructions...

## Verification
How to verify the procedure was successful.

## Rollback
How to undo changes if needed.

## Troubleshooting
Common issues and solutions.

## Related Runbooks
Links to related procedures.
```

## Best Practices

1. **Test runbooks regularly**: Run through procedures during maintenance windows
2. **Keep updated**: Update runbooks when processes change
3. **Document assumptions**: Clearly state prerequisites and environment assumptions
4. **Include examples**: Provide command examples with expected output
5. **Version control**: All runbooks are version controlled in Git
6. **Review process**: Runbooks should be peer-reviewed before use

## Contributing

To add or update runbooks:

1. Create/edit the runbook in this directory
2. Follow the template structure
3. Test the procedure
4. Submit a pull request
5. Get review from operations team

## Automation

Many procedures in these runbooks can be automated:

- Use Ansible playbooks for repeated tasks
- Create scripts for common operations
- Integrate with CI/CD pipelines
- Set up monitoring alerts for proactive response

## Support

For questions about runbooks:
- Create an issue in the repository
- Contact the platform team
- Check the internal wiki
