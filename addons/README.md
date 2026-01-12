# MasterChief Platform - Addons

This directory contains addon integrations for the MasterChief platform.

## Available Addons

### 1. Shoutcast Integration (`shoutcast/`)

Automated deployment and management of Shoutcast DNAS streaming server.

**Features:**
- One-click installation
- Configuration wizard
- Stream management UI
- Listener statistics
- Multiple stream support
- Auto-DJ integration
- IRC bot commands

**Quick Start:**
```python
from addons.shoutcast.manager import ShoutcastManager

manager = ShoutcastManager()
manager.install()
manager.configure({
    'port': 8000,
    'password': 'changeme',
    'max_users': 100
})
manager.start()
```

**IRC Commands:**
```
!shoutcast status              # Server status
!shoutcast streams             # List active streams
!shoutcast listeners           # Current listener count
!shoutcast stats               # Detailed statistics
```

### 2. Jamroom Integration (`jamroom/`)

Automated setup and management of Jamroom CMS community platform.

**Features:**
- LAMP/LEMP stack auto-configuration
- Jamroom core installation
- Module management
- Skin management
- Database configuration
- SSL/TLS setup
- Backup automation

**Quick Start:**
```python
from addons.jamroom.manager import JamroomManager

manager = JamroomManager()
manager.install({
    'database': 'jamroom',
    'user': 'jamroom',
    'password': 'changeme'
})
```

### 3. Custom Script Manager (`scripts/`)

Upload, manage, and execute custom scripts with sandboxed execution.

**Features:**
- Web-based script upload
- Script editor with syntax highlighting
- Version control for scripts
- Script categorization and tagging
- Parameter definitions
- Sandboxed execution
- Resource limits and timeouts
- Scheduled execution (cron)
- Script marketplace

**Quick Start:**
```python
from addons.scripts.manager import ScriptManager

manager = ScriptManager()

# Upload script
manager.upload_script('backup.sh', '''
#!/bin/bash
tar -czf backup-$(date +%Y%m%d).tar.gz /var/www
''')

# Execute script
result = manager.execute_script('backup.sh')
print(result['stdout'])
```

**API Endpoints:**
```
GET  /api/scripts/           # List all scripts
POST /api/scripts/upload     # Upload new script
GET  /api/scripts/{name}     # Get script content
POST /api/scripts/{name}/execute  # Execute script
DELETE /api/scripts/{name}   # Delete script
```

## Plugin Wizard Integration

The MasterChief Plugin Wizard can also be used to create addon plugins:

**Via REST API:**
```bash
# Start wizard session for a new addon
curl -X POST http://localhost:8443/api/wizard/start

# Select plugin type (python, php, nodejs, etc.)
# Follow wizard steps to create addon structure
```

**Via IRC Bot:**
```irc
<user> !plugin wizard
<bot> Visit http://masterchief-host:8443/plugins/wizard

<user> !plugin help python
<bot> Setup guide for python addons...

<user> !plugin suggest python
<bot> Suggested defaults for Python addon creation...
```

See [Plugin Wizard Documentation](../docs/plugin-wizard.md) for detailed information.

## Creating Custom Addons

To create a new addon:

1. Create a directory in `addons/`
2. Create a `manager.py` with your addon logic
3. Create an `api.py` for REST endpoints (optional)
4. Add configuration to `config.yml`
5. Document your addon in a README.md

**OR use the Plugin Wizard:**

```bash
# Via API
curl -X POST http://localhost:8443/api/wizard/start

# Via CLI (future)
python -m platform.plugins.wizard create

# Via IRC
!plugin wizard
```

Example structure:
```
addons/
└── my-addon/
    ├── __init__.py
    ├── manager.py       # Core logic
    ├── api.py          # REST API endpoints
    ├── config/         # Configuration files
    │   └── plugin.yaml # Plugin configuration
    ├── src/            # Source code
    ├── tests/          # Unit tests
    └── README.md       # Documentation
```

## Configuration

Enable/disable addons in `/etc/masterchief/config.yml`:

```yaml
addons:
  shoutcast:
    enabled: true
    port: 8000
    password: "changeme"
  
  jamroom:
    enabled: true
    path: "/var/www/jamroom"
  
  scripts:
    enabled: true
    max_execution_time: 300
```

## Security Considerations

- Scripts run in sandboxed environments with resource limits
- All addon configurations should use secure defaults
- Passwords should never be stored in plain text
- Use proper input validation and sanitization
- Follow principle of least privilege

## Contributing

To contribute a new addon:

1. Fork the repository
2. Create your addon in a new directory (or use Plugin Wizard)
3. Include comprehensive documentation
4. Add tests for your addon
5. Submit a pull request

## Support

For addon-specific issues:
- Check addon documentation
- Review logs in `/var/log/masterchief/`
- Use IRC bot AI assistant: `!plugin ask <question>`
- Report issues on GitHub
