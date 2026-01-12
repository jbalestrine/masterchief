# Web UI for Plugin Management and Deployment

This document describes the new Web UI features for managing plugins and deployments in the MasterChief DevOps Platform.

## Features

### Plugin Management
- **List Plugins**: View all installed plugins with their metadata
- **Upload Plugin**: Install new plugins from .zip files
- **Remove Plugin**: Uninstall plugins from the system
- **Update Plugin**: Update existing plugins to new versions

### Deployment Dashboard
- **Start Deployment**: Initiate new deployments with custom configurations
- **List Deployments**: View all deployments with status filtering
- **Stop Deployment**: Stop running deployments
- **View Logs**: Access deployment logs in real-time
- **Status Summary**: Visual overview of deployment statuses

## Architecture

### Backend APIs

#### Plugin Management API (`/api/plugins`)

**List all plugins**
```http
GET /api/plugins/
```

Response:
```json
{
  "success": true,
  "plugins": [
    {
      "id": "plugin-name",
      "name": "Plugin Name",
      "version": "1.0.0",
      "description": "Plugin description",
      "author": "Author Name",
      "type": "generic",
      "path": "/path/to/plugin"
    }
  ],
  "count": 1
}
```

**Get plugin by ID**
```http
GET /api/plugins/{plugin_id}
```

**Upload and install plugin**
```http
POST /api/plugins/upload
Content-Type: multipart/form-data

file: <plugin.zip>
name: <optional-plugin-name>
```

**Remove plugin**
```http
DELETE /api/plugins/{plugin_id}
```

**Update plugin**
```http
POST /api/plugins/{plugin_id}/update
Content-Type: multipart/form-data

file: <plugin.zip>
```

#### Deployment Management API (`/api/deployments`)

**List deployments**
```http
GET /api/deployments/?status={status}&limit={limit}
```

Query parameters:
- `status` (optional): Filter by status (pending, running, success, failed, stopped)
- `limit` (optional): Maximum number of results to return

**Get deployment by ID**
```http
GET /api/deployments/{deployment_id}
```

**Start new deployment**
```http
POST /api/deployments/start
Content-Type: application/json

{
  "name": "Deployment Name",
  "target": "dev|staging|prod",
  "config": {
    "optional": "configuration"
  }
}
```

**Stop deployment**
```http
POST /api/deployments/{deployment_id}/stop
```

**Get deployment logs**
```http
GET /api/deployments/{deployment_id}/logs
```

### Frontend

The frontend is built with React.js and Vite, providing a modern, responsive interface.

**Location**: `/platform/portal/`

**Key Components**:
- `PluginManagement`: Main page for plugin operations
- `DeploymentDashboard`: Main page for deployment operations
- `PluginCard`: Individual plugin display component
- `PluginUpload`: Modal for uploading plugins
- `DeploymentCard`: Individual deployment display with logs
- `DeploymentForm`: Modal for starting new deployments

## Usage

### Starting the Backend API

```bash
cd /home/runner/work/masterchief/masterchief
python -c "
from platform.api import create_app

config = {
    'SECRET_KEY': 'dev-secret-key',
    'DEBUG': True
}

app = create_app(config)
app.run(host='0.0.0.0', port=5000)
"
```

### Starting the Frontend

```bash
cd platform/portal
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Plugin Package Format

Plugins must be packaged as .zip files with the following structure:

```
plugin-name.zip
├── manifest.yaml (or manifest.yml, manifest.json)
└── [plugin files]
```

**Manifest Example (manifest.yaml)**:
```yaml
name: my-plugin
version: 1.0.0
description: My custom plugin
author: Your Name
type: generic
dependencies: []
entry_point: main
```

## Synchronization Between Web UI and CLI

Both the Web UI and CLI use the same backend APIs, ensuring consistency:

- **CLI**: Uses `core/cli/main.py` for command-line operations
- **Web UI**: Uses REST APIs in `/api/plugins` and `/api/deployments`
- **Backend**: Shared managers in `platform/plugins/manager.py` and `platform/deployments/manager.py`

### Example: Installing a Plugin

**Via CLI**:
```bash
masterchief module add /path/to/plugin
```

**Via Web UI**:
1. Navigate to Plugin Management page
2. Click "Upload Plugin"
3. Select your plugin.zip file
4. Click "Upload"

Both methods use the same `PluginManager` class, ensuring identical behavior.

### Example: Starting a Deployment

**Via CLI**:
```bash
masterchief deploy --target=prod
```

**Via Web UI**:
1. Navigate to Deployment Dashboard
2. Click "Start New Deployment"
3. Fill in deployment details
4. Click "Start Deployment"

Both methods use the same `DeploymentManager` class.

## Security Considerations

1. **File Upload Validation**: Only .zip files are accepted for plugin uploads
2. **File Size Limits**: Consider implementing file size limits in production
3. **Authentication**: The current implementation does not include authentication. Add authentication middleware before deploying to production.
4. **CORS**: CORS is enabled for development. Configure appropriately for production.
5. **Input Validation**: All API inputs are validated on the backend

## Testing

### Backend Tests

Run the backend tests:
```bash
cd /home/runner/work/masterchief/masterchief
python -m pytest tests/unit/platform/ -v
```

Note: Due to the `platform` directory name conflicting with Python's built-in `platform` module, tests should be run from outside the project directory:

```bash
cd /tmp
python -c "
import sys
sys.path.insert(0, '/home/runner/work/masterchief/masterchief')
# ... run tests
"
```

### Frontend Tests

The frontend can be manually tested by:
1. Starting the backend API
2. Starting the frontend development server
3. Navigating through the UI and testing all features

## Future Enhancements

- Add authentication and authorization
- Implement plugin versioning and update notifications
- Add plugin marketplace integration
- Implement real deployment orchestration (currently simulated)
- Add deployment history and rollback capabilities
- Implement WebSocket for real-time deployment updates
- Add plugin dependency resolution
- Implement plugin configuration UI
- Add deployment templates
- Implement deployment scheduling
