# Plugin Wizard Documentation

## Overview

The Plugin Wizard is a comprehensive tool for creating and managing plugins in the MasterChief DevOps Platform. It provides a step-by-step interface for configuring plugins with support for multiple programming languages and frameworks.

## Supported Plugin Types

- **PHP** - Web applications and PHP-based plugins
- **Python** - Automation scripts and Python applications
- **PowerShell** - Windows automation and infrastructure management
- **Node.js** - JavaScript-based services and applications
- **Shell/Bash** - Unix/Linux shell scripts

## Architecture

### Components

1. **Wizard Engine** (`wizard_engine.py`)
   - Orchestrates the multi-step wizard workflow
   - Manages session state
   - Coordinates between step handlers and generators

2. **Step Handlers** (`step_handlers.py`)
   - Provides data structures for each wizard step
   - Returns configuration options based on plugin type

3. **Folder Generator** (`folder_generator.py`)
   - Creates plugin directory structure
   - Sets proper file permissions (755 for directories, 644 for files)
   - Generates README and .gitignore files

4. **Template Generator** (`template_generator.py`)
   - Creates type-specific configuration files
   - Generates plugin.yaml with metadata
   - Creates requirements.txt, package.json, etc.

5. **Validators** (`validators.py`)
   - Validates user input
   - Checks naming conventions
   - Validates version strings and dependencies

## Wizard Workflow

### Step 1: Plugin Type Selection

Select the type of plugin you want to create:

```json
{
  "plugin_type": "python"
}
```

### Step 2: Metadata Collection

Provide basic information about your plugin:

```json
{
  "name": "my-awesome-plugin",
  "description": "An awesome plugin for automation",
  "version": "1.0.0",
  "author": "Your Name",
  "tags": ["automation", "devops"],
  "dependencies": []
}
```

**Requirements:**
- Name: lowercase, alphanumeric with hyphens, 3-50 characters
- Description: minimum 10 characters
- Version: semantic versioning (e.g., 1.0.0)

### Step 3: Plugin-Specific Configuration

Configure settings specific to your plugin type:

#### Python Configuration
```json
{
  "python_version": "3.10",
  "venv_enabled": true,
  "venv_path": ".venv",
  "entry_point": "main.py",
  "dependencies": ["flask>=2.0", "requests", "pyyaml"]
}
```

#### PHP Configuration
```json
{
  "php_version": "8.2",
  "memory_limit": "256M",
  "upload_max_filesize": "64M",
  "post_max_size": "64M",
  "max_execution_time": 300,
  "extensions": ["curl", "mbstring", "xml", "json"]
}
```

#### PowerShell Configuration
```json
{
  "ps_version": "7.0",
  "execution_policy": "RemoteSigned",
  "modules": ["Az", "PSReadLine"],
  "script_signing": false,
  "entry_point": "main.ps1"
}
```

### Step 4: Review & Confirm

Review your configuration before creating the plugin.

### Step 5: Plugin Creation

The wizard creates the following structure:

```
plugins/my-awesome-plugin/
├── src/                 # Source code
│   └── __init__.py      # Python package marker
├── logs/                # Plugin logs
├── config/              # Configuration files
│   ├── plugin.yaml      # Main configuration
│   └── python_config.yaml  # Type-specific config
├── tests/               # Test files
├── README.md            # Documentation
├── .gitignore           # Git ignore rules
└── requirements.txt     # Python dependencies
```

## REST API Endpoints

### Start Wizard Session

```http
POST /api/wizard/start
```

**Response:**
```json
{
  "success": true,
  "session_id": "uuid-here",
  "current_step": "TYPE_SELECTION",
  "step_data": {
    "title": "Select Plugin Type",
    "options": [...]
  }
}
```

### Get Step Data

```http
GET /api/wizard/{session_id}/step/{step_num}
```

**Parameters:**
- `session_id`: UUID of wizard session
- `step_num`: Step number (1-5)

### Submit Step Data

```http
POST /api/wizard/{session_id}/step/{step_num}
Content-Type: application/json

{
  "plugin_type": "python"
}
```

### Complete Wizard

```http
POST /api/wizard/{session_id}/complete
Content-Type: application/json

{
  "confirm": true
}
```

### Get Session Status

```http
GET /api/wizard/{session_id}/status
```

### Cancel Wizard

```http
DELETE /api/wizard/{session_id}
```

### List Active Sessions

```http
GET /api/wizard/sessions
```

## Usage Examples

### Using Python

```python
import requests

# Start wizard
response = requests.post('http://localhost:8443/api/wizard/start')
session_id = response.json()['session_id']

# Select plugin type
requests.post(
    f'http://localhost:8443/api/wizard/{session_id}/step/1',
    json={'plugin_type': 'python'}
)

# Submit metadata
requests.post(
    f'http://localhost:8443/api/wizard/{session_id}/step/2',
    json={
        'name': 'my-plugin',
        'description': 'My awesome plugin',
        'version': '1.0.0'
    }
)

# Submit configuration
requests.post(
    f'http://localhost:8443/api/wizard/{session_id}/step/3',
    json={
        'python_version': '3.10',
        'venv_enabled': True,
        'dependencies': ['flask']
    }
)

# Complete
requests.post(
    f'http://localhost:8443/api/wizard/{session_id}/complete',
    json={'confirm': True}
)
```

### Using cURL

```bash
# Start wizard
SESSION_ID=$(curl -s -X POST http://localhost:8443/api/wizard/start | jq -r '.session_id')

# Select type
curl -X POST "http://localhost:8443/api/wizard/$SESSION_ID/step/1" \
  -H "Content-Type: application/json" \
  -d '{"plugin_type": "python"}'

# Submit metadata
curl -X POST "http://localhost:8443/api/wizard/$SESSION_ID/step/2" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-plugin",
    "description": "My awesome plugin",
    "version": "1.0.0"
  }'

# Complete
curl -X POST "http://localhost:8443/api/wizard/$SESSION_ID/complete" \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'
```

## Best Practices

1. **Naming Conventions**
   - Use lowercase letters, numbers, and hyphens
   - Keep names descriptive but concise
   - Avoid special characters and spaces

2. **Version Management**
   - Follow semantic versioning (MAJOR.MINOR.PATCH)
   - Start with 1.0.0 for initial release
   - Increment appropriately for changes

3. **Dependencies**
   - Pin dependency versions for reproducibility
   - Keep dependencies minimal
   - Document why each dependency is needed

4. **Configuration**
   - Use sensible defaults
   - Document all configuration options
   - Validate configuration at startup

5. **Security**
   - Follow principle of least privilege
   - Avoid hardcoding credentials
   - Use environment variables for secrets

## Troubleshooting

### Plugin Already Exists

**Error:** `Plugin 'my-plugin' already exists`

**Solution:** Choose a different name or delete the existing plugin directory.

### Invalid Plugin Name

**Error:** `Plugin name must contain only lowercase letters, numbers, and hyphens`

**Solution:** Use only lowercase alphanumeric characters and hyphens.

### Session Not Found

**Error:** `Session not found`

**Solution:** The session may have expired or been deleted. Start a new wizard session.

## Integration with IRC Bot

The Plugin Wizard is also available through IRC bot commands:

```
!plugin wizard        - Start the wizard (provides web UI link)
!plugin help <type>   - Get help for a plugin type
!plugin status        - Check wizard status
```

See the [AI Assistant Documentation](ai-assistant.md) for more IRC commands.
