# Configuration Editor Documentation

## Overview

The Configuration Editor provides a real-time interface for editing plugin configurations with validation, diff viewing, and schema support.

## Features

- **Real-time Editing** - Edit configurations on-the-fly
- **YAML/JSON Support** - Work with both YAML and JSON formats
- **Schema Validation** - Validate against plugin type schemas
- **Diff Viewing** - See changes before saving
- **Backup & Restore** - Automatic backups on save
- **Type-specific Schemas** - Different schemas for each plugin type

## Architecture

### Components

1. **ConfigEditor** (`editor.py`)
   - Manages configuration file operations
   - Handles validation and saving
   - Creates backups before updates
   - Tracks pending changes

2. **SchemaValidator** (`schema_validator.py`)
   - Provides JSON schemas for plugin types
   - Validates configurations
   - Returns detailed error messages

## REST API Endpoints

### Get Plugin Configuration

```http
GET /api/config/{plugin_id}
```

**Response:**
```json
{
  "success": true,
  "plugin_id": "my-plugin",
  "config": {
    "plugin": {
      "name": "my-plugin",
      "version": "1.0.0",
      "description": "My plugin",
      "type": "python"
    }
  }
}
```

### Update Plugin Configuration

```http
PUT /api/config/{plugin_id}
Content-Type: application/json

{
  "plugin": {
    "name": "my-plugin",
    "version": "2.0.0",
    "description": "Updated plugin"
  }
}
```

**Query Parameters:**
- `validate` (optional): Set to `false` to skip validation (default: `true`)

**Response:**
```json
{
  "success": true,
  "message": "Configuration updated successfully",
  "plugin_id": "my-plugin"
}
```

### Validate Configuration

```http
POST /api/config/{plugin_id}/validate
Content-Type: application/json

{
  "plugin": {
    "name": "my-plugin",
    "version": "1.0.0"
  }
}
```

**Response:**
```json
{
  "success": true,
  "plugin_id": "my-plugin",
  "validation": {
    "valid": true,
    "errors": []
  }
}
```

### Get Configuration Schema

```http
GET /api/config/{plugin_id}/schema
```

**Response:**
```json
{
  "success": true,
  "plugin_id": "my-plugin",
  "plugin_type": "python",
  "schema": {
    "type": "object",
    "properties": {...},
    "required": [...]
  }
}
```

### Get Configuration Diff

```http
POST /api/config/{plugin_id}/diff
Content-Type: application/json

{
  "plugin": {
    "version": "2.0.0"
  }
}
```

**Response:**
```json
{
  "success": true,
  "plugin_id": "my-plugin",
  "differences": [
    {
      "type": "modified",
      "path": "plugin.version",
      "old_value": "1.0.0",
      "new_value": "2.0.0"
    }
  ],
  "count": 1
}
```

## Configuration Structure

### Main Plugin Configuration (plugin.yaml)

```yaml
plugin:
  name: my-plugin
  version: 1.0.0
  description: Plugin description
  author: Your Name
  type: python
  tags:
    - automation
    - devops
  enabled: true
  dependencies: []

logging:
  level: INFO
  file: logs/my-plugin.log
  max_size: 10M
  backup_count: 5
```

### Python-Specific Configuration (python_config.yaml)

```yaml
python:
  version: "3.10"
  venv_enabled: true
  venv_path: .venv
  dependencies:
    - flask>=2.0
    - requests
  entry_point: main.py
  environment: {}
```

### PHP-Specific Configuration (php_config.yaml)

```yaml
php:
  version: "8.2"
  memory_limit: 256M
  upload_max_filesize: 64M
  post_max_size: 64M
  max_execution_time: 300
  extensions:
    - curl
    - mbstring
    - xml
  ini_overrides: {}
```

## Usage Examples

### Using Python

```python
import requests

base_url = 'http://localhost:8443/api/config'

# Get current configuration
response = requests.get(f'{base_url}/my-plugin')
config = response.json()['config']

# Modify configuration
config['plugin']['version'] = '2.0.0'

# Validate before saving
validation = requests.post(
    f'{base_url}/my-plugin/validate',
    json=config
)

if validation.json()['validation']['valid']:
    # Save configuration
    requests.put(f'{base_url}/my-plugin', json=config)
```

### Using cURL

```bash
# Get configuration
curl http://localhost:8443/api/config/my-plugin

# Update configuration
curl -X PUT http://localhost:8443/api/config/my-plugin \
  -H "Content-Type: application/json" \
  -d '{
    "plugin": {
      "name": "my-plugin",
      "version": "2.0.0",
      "description": "Updated plugin"
    }
  }'

# Get diff
curl -X POST http://localhost:8443/api/config/my-plugin/diff \
  -H "Content-Type: application/json" \
  -d '{
    "plugin": {
      "version": "2.0.0"
    }
  }'
```

## Validation Rules

### Common Rules (All Plugin Types)

- **name**: 3-50 characters, lowercase alphanumeric with hyphens
- **version**: Semantic versioning (MAJOR.MINOR.PATCH)
- **description**: Minimum 10 characters
- **type**: Must match plugin type (php, python, powershell, nodejs, shell)

### Type-Specific Rules

#### Python
- **python_version**: Must be 3.8 or newer
- **venv_path**: Required if venv_enabled is true
- **dependencies**: Valid Python package specifications

#### PHP
- **memory_limit**: Format like "256M" or "1G"
- **max_execution_time**: Positive integer
- **extensions**: Valid PHP extension names

#### PowerShell
- **execution_policy**: Valid PowerShell execution policy
- **ps_version**: Valid PowerShell version

## Backup and Recovery

### Automatic Backups

When updating a configuration, a backup is automatically created:

```
config/plugin.yaml      # Current config
config/plugin.yaml.bak  # Backup
```

### Manual Recovery

If you need to restore from backup:

```bash
cd /opt/masterchief/plugins/my-plugin/config
cp plugin.yaml.bak plugin.yaml
```

Or use the API to revert changes by getting the old configuration and updating again.

## Best Practices

1. **Always Validate** - Use the validate endpoint before saving
2. **Check Diffs** - Review changes with the diff endpoint
3. **Test Changes** - Test in development before production
4. **Version Control** - Keep configurations in version control
5. **Document Changes** - Add comments explaining configuration changes

## Troubleshooting

### Configuration Not Found

**Error:** `Plugin 'my-plugin' not found`

**Solution:** Check that the plugin exists and the name is correct.

### Validation Failed

**Error:** `Configuration validation failed: [errors]`

**Solution:** Review the validation errors and correct the configuration.

### Permission Denied

**Error:** `Permission denied writing configuration`

**Solution:** Check file permissions on the plugin directory and config files.

### Backup Failed

**Error:** `Could not create backup`

**Solution:** Check disk space and write permissions on the config directory.

## Security Considerations

1. **Input Validation** - All inputs are validated before processing
2. **Path Traversal** - Plugin IDs are validated to prevent path traversal
3. **Backup Creation** - Automatic backups prevent data loss
4. **Schema Enforcement** - Type-specific schemas enforce structure
5. **Error Handling** - Errors are caught and backups restored on failure

## Integration

The Configuration Editor integrates with:

- **Plugin Wizard** - Uses the same configuration structure
- **IRC Bot** - AI Assistant can help with configuration
- **Monitoring** - Configuration changes can be logged and monitored
