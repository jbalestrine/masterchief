# MasterChief Web UI Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────┐          ┌──────────────────────┐     │
│  │  Plugin Management │          │ Deployment Dashboard │     │
│  ├────────────────────┤          ├──────────────────────┤     │
│  │ - List Plugins     │          │ - Status Summary     │     │
│  │ - Upload Plugin    │          │ - Start Deployment   │     │
│  │ - Remove Plugin    │          │ - Stop Deployment    │     │
│  │ - View Details     │          │ - View Logs          │     │
│  └────────────────────┘          └──────────────────────┘     │
│                                                                 │
│                      React.js (port 3000)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              │
┌─────────────────────────────▼─────────────────────────────────────┐
│                      API GATEWAY LAYER                            │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐              ┌──────────────────────┐     │
│  │  /api/plugins    │              │ /api/deployments     │     │
│  ├──────────────────┤              ├──────────────────────┤     │
│  │ GET    /         │              │ GET    /             │     │
│  │ GET    /:id      │              │ GET    /:id          │     │
│  │ POST   /upload   │              │ POST   /start        │     │
│  │ DELETE /:id      │              │ POST   /:id/stop     │     │
│  │ POST   /:id/update│             │ GET    /:id/logs     │     │
│  └──────────────────┘              └──────────────────────┘     │
│                                                                   │
│                   Flask API (port 5000)                           │
└───────────────────────────────────────────────────────────────────┘
                              │
                              │ Function Calls
                              │
┌─────────────────────────────▼─────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                         │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────┐         ┌───────────────────────┐     │
│  │   PluginManager      │         │  DeploymentManager    │     │
│  ├──────────────────────┤         ├───────────────────────┤     │
│  │ - list_plugins()     │         │ - create_deployment() │     │
│  │ - get_plugin()       │         │ - start_deployment()  │     │
│  │ - install_plugin()   │         │ - stop_deployment()   │     │
│  │ - remove_plugin()    │         │ - list_deployments()  │     │
│  │ - update_plugin()    │         │ - get_logs()          │     │
│  └──────────────────────┘         └───────────────────────┘     │
│                                                                   │
│              Python Classes (platform/*/manager.py)               │
└───────────────────────────────────────────────────────────────────┘
                              │
                              │ File I/O
                              │
┌─────────────────────────────▼─────────────────────────────────────┐
│                      STORAGE LAYER                                │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────┐         ┌───────────────────────┐     │
│  │   modules/           │         │  In-Memory Store      │     │
│  ├──────────────────────┤         ├───────────────────────┤     │
│  │ plugin-1/            │         │ Deployments Dict      │     │
│  │ ├─ manifest.yaml     │         │ - deployment_id       │     │
│  │ └─ [plugin files]    │         │ - status              │     │
│  │                      │         │ - logs                │     │
│  │ plugin-2/            │         │ - timestamps          │     │
│  │ └─ ...               │         └───────────────────────┘     │
│  └──────────────────────┘                                        │
│                                                                   │
│              File System + Memory                                 │
└───────────────────────────────────────────────────────────────────┘


┌───────────────────────────────────────────────────────────────────┐
│                    CLI INTERFACE (Parallel Path)                  │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  masterchief module list    ──────┐                              │
│  masterchief module add     ──────┤                              │
│  masterchief deploy         ──────┼──> Same Business Logic       │
│  masterchief status         ──────┤    (PluginManager,           │
│                                    │     DeploymentManager)       │
│  core/cli/main.py                 ─┘                              │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘


Data Flow Example - Installing a Plugin:

1. User clicks "Upload Plugin" in Web UI
2. PluginUpload component captures file and sends POST request
3. Axios sends multipart/form-data to /api/plugins/upload
4. Flask plugins_bp blueprint receives request
5. Validates file type and extracts data
6. Calls PluginManager.install_plugin(file_path, name)
7. PluginManager:
   - Extracts zip to temp directory
   - Finds and parses manifest.yaml
   - Validates plugin structure
   - Copies to modules/ directory
   - Returns success response
8. API returns JSON response
9. React component updates UI with new plugin
10. User sees plugin in the list


Deployment Flow:

1. User fills deployment form and clicks "Start"
2. DeploymentForm sends POST to /api/deployments/start
3. DeploymentManager.create_deployment() creates new deployment
4. DeploymentManager.start_deployment() begins execution
5. Deployment status updated to "running"
6. Logs are generated and stored
7. Status changes to "success" or "failed"
8. Dashboard auto-refreshes every 5s to show updates
9. User can view logs by clicking "View Logs"
10. User can stop deployment with "Stop" button


Technology Stack:

Frontend:              Backend:              Storage:
- React 18            - Flask 3.0           - File System (plugins)
- React Router 6      - Flask-CORS          - In-Memory (deployments)
- Axios               - Werkzeug            
- Vite                - PyYAML              
- CSS3                - Python 3.10+        


Key Design Decisions:

1. Shared Backend: CLI and Web UI use same manager classes
2. RESTful API: Standard HTTP methods and status codes
3. In-Memory Deployments: Fast access, suitable for demo
4. File-Based Plugins: Persistent storage, easy to manage
5. React SPA: Modern, responsive, client-side routing
6. Modular Components: Reusable UI components
7. Auto-Refresh: Dashboard updates without user action
8. Error Handling: Comprehensive validation at all layers
```
