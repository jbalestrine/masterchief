# Script Automation Guide

The MasterChief Script Automation Suite provides comprehensive capabilities for creating, managing, and automating scripts through AI generation, templates, validation, and scheduling.

## Overview

The Script Automation Suite extends the existing ScriptManager with powerful automation features:

- **AI Generation**: Generate scripts from natural language using local LLMs
- **Voice Control**: Create scripts by voice commands
- **Templates**: Use pre-built templates for common tasks
- **Validation**: Ensure scripts are safe before execution
- **Scheduling**: Automate script execution with cron-based scheduling

## AI Script Generation

### Setup Ollama

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull a code model
ollama pull codellama
```

### Usage

```python
from addons.scripts.manager import ScriptManager

config = {
    'ai_generation': {
        'enabled': True,
        'model': 'codellama',
        'ollama_url': 'http://localhost:11434'
    }
}
manager = ScriptManager(config=config)

# Generate a script
script = manager.generate_script(
    description="Backup PostgreSQL database to S3",
    language="bash",
    save=True
)
```

## Script Templates

Pre-built templates for common DevOps tasks.

### Available Templates

- **Backup**: PostgreSQL, MySQL, MongoDB
- **Monitoring**: Disk usage, service health, log monitoring
- **Deployment**: Docker, Kubernetes
- **Security**: SSL renewal, audit logs
- **Maintenance**: Log rotation

### Usage

```python
manager.create_from_template(
    template_path="backup/postgres",
    script_name="backup_prod.sh",
    variables={
        "database": "production",
        "backup_dir": "/backups",
        "retention_days": 14
    }
)
```

## Script Validation

Validates scripts for dangerous commands and syntax errors.

```python
result = manager.validate_script("backup.sh")

if result.valid:
    print("✓ Script is safe")
else:
    for error in result.errors:
        print(f"ERROR: {error}")
```

## Script Scheduling

Schedule scripts with cron expressions.

```python
# Schedule daily backup at 2 AM
job = manager.schedule_script(
    script_name="backup.sh",
    cron="0 2 * * *",
    notify=True
)

# List all schedules
jobs = manager.list_schedules()

# View execution history
history = manager.get_execution_history()
```

## Configuration

```yaml
scripts:
  ai_generation:
    enabled: true
    ollama_url: "http://localhost:11434"
    model: "codellama"
    
  validation:
    enabled: true
    block_dangerous: true
    
  scheduling:
    enabled: true
    database: "/var/lib/masterchief/schedules.db"
```

## Best Practices

1. **Always validate scripts** before execution
2. **Review AI-generated code** before running
3. **Use templates** for consistency
4. **Monitor scheduled executions**
5. **Test in non-production** first
