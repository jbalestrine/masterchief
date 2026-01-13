# MasterChief Flask Web Application

## Overview

This is a comprehensive DevOps automation platform built as a **single-file Flask application** (`main.py`) with all HTML embedded. No templates folder needed!

## Features

### 1. Dashboard
- Real-time system statistics (CPU, Memory, Disk, Uptime)
- Auto-refreshing every 5 seconds
- Quick action buttons to all features

### 2. Jamroom Site Manager
- Add, edit, and delete Jamroom CMS sites
- Store site name, URL (clickable links), and description
- Track creation timestamps
- Full CRUD operations

### 3. Shoutcast/Icecast Server Manager
- Manage streaming servers
- Support for both Shoutcast and Icecast
- Start/Stop server controls
- Configure host, port, and server type
- Track server status

### 4. Script Manager
- Upload and manage scripts (PowerShell .ps1, Python .py, Bash .sh)
- Execute scripts with custom arguments
- View script content
- Delete scripts
- See execution results (stdout, stderr, return code)

### 5. Process Monitor
- View top 50 processes by CPU usage
- Real-time CPU and Memory usage per process
- Kill processes directly from the UI
- Process status monitoring

### 6. Windows Services Monitor
- Monitor Windows services (Windows only)
- Start, Stop, and Restart services
- View service status and display names
- Note: Requires Windows platform

### 7. Addon Installer
- Upload .zip addon packages
- Install addons by extracting them
- View uploaded addon files
- Delete addon packages
- Track file sizes and upload timestamps

## Installation

### Prerequisites
```bash
# Python 3.8 or higher
python3 --version

# Install required packages
pip install flask werkzeug psutil
```

Or use requirements.txt:
```bash
pip install -r requirements.txt
```

### Quick Start
```bash
# Navigate to the repository
cd /path/to/masterchief

# Run the application
python3 main.py
```

The application will start on `http://localhost:8080`

## Usage

### Starting the Application
```bash
python3 main.py
```

Output:
```
======================================================================
MasterChief DevOps Platform
======================================================================
Dashboard: http://localhost:8080
======================================================================
 * Running on http://0.0.0.0:8080
```

### Accessing the Web Interface
Open your browser and navigate to:
- **Local**: http://localhost:8080
- **Network**: http://YOUR_IP:8080

### Navigation
Use the top navigation bar to access different features:
- Dashboard - System statistics and quick actions
- Jamroom Sites - Manage CMS sites
- Shoutcast/Icecast - Manage streaming servers
- Scripts - Upload and execute scripts
- Processes - Monitor running processes
- Services - Monitor Windows services (Windows only)
- Addons - Install addon packages

## Data Storage

All data is stored locally in the `data/` directory:
- `data/jamroom.json` - Jamroom sites database
- `data/shoutcast.json` - Shoutcast/Icecast servers database
- `data/scripts/` - Uploaded scripts
- `data/uploads/` - Uploaded addon packages
- `data/uploads/extracted/` - Extracted addon files

## API Endpoints

### System Stats API
```bash
GET /api/stats
```
Returns JSON with CPU, memory, disk, and uptime information.

Example:
```bash
curl http://localhost:8080/api/stats
```

### Jamroom Sites
- `GET /jamroom` - List all sites
- `POST /jamroom/add` - Add new site
- `GET /jamroom/edit/<id>` - Edit site form
- `POST /jamroom/update/<id>` - Update site
- `GET /jamroom/delete/<id>` - Delete site

### Shoutcast Servers
- `GET /shoutcast` - List all servers
- `POST /shoutcast/add` - Add new server
- `GET /shoutcast/edit/<id>` - Edit server form
- `POST /shoutcast/update/<id>` - Update server
- `GET /shoutcast/start/<id>` - Start server
- `GET /shoutcast/stop/<id>` - Stop server
- `GET /shoutcast/delete/<id>` - Delete server

### Scripts
- `GET /scripts` - List all scripts
- `POST /scripts/add` - Add new script
- `GET /scripts/view/<filename>` - View script content
- `GET /scripts/execute/<filename>` - Execute form
- `POST /scripts/run/<filename>` - Run script
- `GET /scripts/delete/<filename>` - Delete script

### Processes
- `GET /processes` - List top 50 processes
- `GET /processes/kill/<pid>` - Kill process

### Services (Windows only)
- `GET /services` - List all services
- `GET /services/start/<name>` - Start service
- `GET /services/stop/<name>` - Stop service
- `GET /services/restart/<name>` - Restart service

### Addons
- `GET /addons` - List uploaded addons
- `POST /addons/upload` - Upload addon package
- `GET /addons/install/<filename>` - Install addon
- `GET /addons/delete/<filename>` - Delete addon

## Security Notes

⚠️ **This is a development application!**

1. **Change the secret key** in production:
   ```python
   app.config['SECRET_KEY'] = 'your-random-secret-key'
   ```

2. **Use a production WSGI server** (not Flask's built-in):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8080 main:app
   ```

3. **Add authentication** before deploying to production

4. **Restrict file upload types** and sizes as needed

5. **Run with appropriate user permissions** (not root)

6. **Use HTTPS** in production with proper SSL certificates

## Code Structure

The entire application is in `main.py` (~900 lines):
- Python classes for managers (Jamroom, Shoutcast, Script)
- Flask route handlers
- Embedded HTML templates as Python strings
- Embedded CSS styles
- Embedded JavaScript for interactivity

## Customization

### Changing the Port
Edit the last line in `main.py`:
```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

### Modifying Styles
Edit the `HTML_TEMPLATE` string in `main.py` (CSS is in the `<style>` section)

### Adding New Features
Add new route handlers and HTML templates as strings in `main.py`

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8080
lsof -i :8080  # Linux/Mac
netstat -ano | findstr :8080  # Windows

# Kill the process or change the port in main.py
```

### Permission Denied Errors
```bash
# Ensure data directory has write permissions
chmod -R 755 data/
```

### Module Not Found
```bash
# Install missing dependencies
pip install flask werkzeug psutil
```

### Windows Services Not Working
- Ensure you're running on Windows
- Run as Administrator for service control
- Check Windows service names match exactly

## Development

### Debug Mode
The application runs in debug mode by default:
```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

Set `debug=False` for production.

### Adding Dependencies
Update `requirements.txt` and install:
```bash
pip install -r requirements.txt
```

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/jbalestrine/masterchief/issues
- Documentation: See main README.md

## Author

Part of the MasterChief DevOps Automation Platform
