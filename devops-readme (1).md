# DevOps Master Suite - Enterprise Modular Platform

A comprehensive, modular DevOps platform for infrastructure management, service deployment, and automation.

## 🚀 Features

### 1. **Module Builder** 
- Create custom modules dynamically
- Support for multiple module types:
  - Web Applications
  - REST APIs
  - Scale-Out File Servers (SOFS)
  - IRC Chat Servers (InspIRCd)
  - Shoutcast Media Servers
  - Docusaurus Documentation
  - Node.js Applications
  - Custom Services
- Auto-generates PowerShell scripts for each module:
  - Installation scripts
  - Start/Stop scripts
  - Deployment scripts
  - Configuration scripts

### 2. **File Manager**
- Browse directory structure
- Upload single or multiple files
- Upload entire folder directories
- Edit files directly in the interface
- Create ZIP archives of selected files
- Organize files by module/project

### 3. **Service Manager**
- Create and manage services
- Support for multiple server types:
  - Node.js
  - IIS
  - Apache
  - XAMPP
  - InspIRCd
  - Shoutcast
  - Docusaurus
- Start/Stop/Restart services
- Auto-start on boot configuration
- Real-time service status monitoring

### 4. **Web Application Deployment**
- One-click deployment to:
  - Local machine
  - Network shares
  - Azure VMs
  - Frontend directory (for live preview)
- Auto-install dependencies:
  - IIS (if not installed)
  - Apache (via Chocolatey)
  - XAMPP (via Chocolatey)
  - Node.js (via Chocolatey)
- Post-deployment configuration:
  - Unpack binaries
  - Configure web server
  - Set up virtual directories
  - Install npm packages

### 5. **Live Web Preview**
- View deployed web applications directly in the interface
- Test websites before production deployment
- Multiple apps on different ports
- Subdirectory support for same-port hosting

### 6. **IRC Chat & Bot Training**
- MIRC-style chat interface
- Connect to IRC servers
- Trainable bot system
- Remote command execution
- Data ingestion and feedback
- Bot commands:
  - `!help` - Show available commands
  - `!status` - Check system status
  - `!deploy` - Trigger deployments
  - `!services` - List running services
  - `!modules` - Show loaded modules

### 7. **Scale-Out File Server (SOFS)**
- Create Windows Server SOFS clusters
- Configure failover clustering
- Set up file share witnesses
- Create and manage SMB shares
- Auto-generated cluster scripts

### 8. **Infrastructure as Code (IaC)**
- Generate Terraform templates
- Generate ARM templates
- Generate Bicep templates
- Advanced configuration options:
  - VMs with custom sizing
  - Network configuration
  - Load balancers
  - SQL databases
  - AKS clusters
  - Storage accounts

### 9. **PowerShell Script Library**
- Store and organize scripts
- Execute scripts with parameters
- Track execution history
- View execution logs
- Auto-generated module scripts

### 10. **Resource Management**
- Track cloud resources
- Monitor costs
- Resource status tracking
- Multi-region support

## 📁 Project Structure

```
devops-master-suite/
├── backend/
│   ├── server.js              # Main API server
│   ├── package.json           # Dependencies
│   ├── .env                   # Configuration
│   ├── devops.db              # SQLite database
│   ├── scripts/               # PowerShell scripts
│   ├── logs/                  # Execution logs
│   ├── modules/               # Custom modules
│   │   ├── module1/
│   │   │   ├── index.html
│   │   │   ├── server.js
│   │   │   ├── package.json
│   │   │   └── config.json
│   │   └── module2/
│   ├── webapps/               # Deployed web apps
│   └── deployments/           # Deployment packages
│
└── frontend/
    ├── App.js                 # React application
    ├── package.json           # Frontend dependencies
    └── components/            # Modular components
```

## 🛠️ Installation

### Prerequisites
- Node.js 16+ 
- PowerShell 5.1+ (Windows)
- SQLite3
- (Optional) Chocolatey for auto-installs

### Backend Setup
```bash
cd backend
npm install
npm start
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 🔧 Configuration

### Environment Variables (.env)
```env
PORT=5000
NODE_ENV=development
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_TENANT_ID=your-tenant-id
DEFAULT_REGION=eastus
```

## 📖 Usage Guide

### Creating a Custom Module

1. Click **"Create Module"** button
2. Select module type (webapp, IRC, SOFS, etc.)
3. Configure options:
   - Name
   - Description
   - Ports
   - Features
4. Module is created with:
   - Directory structure
   - Template files
   - PowerShell scripts
   - Database entry

### Deploying a Web Application

1. Go to **Deployment** tab
2. Select deployment target:
   - Local machine
   - Network share
   - Azure VM
   - Frontend directory
3. Choose web server (IIS/Apache/XAMPP)
4. Configure options:
   - Auto-install server software
   - Install dependencies
   - Auto-configure
5. Click **Deploy Now**

### Managing Services

1. Navigate to **Service Manager**
2. Click **Add Service**
3. Configure:
   - Service type
   - Port
   - Directory
   - Auto-start
4. Control services:
   - Start
   - Stop
   - Restart
   - View status

### Using IRC Chat & Bot

1. Click **IRC Chat** button
2. Enter commands or messages
3. Bot responds to commands:
   - `!help` - List commands
   - `!deploy <app>` - Deploy application
   - `!status` - Check system
   - `!services` - List services
4. Train bot with new commands

### Setting up SOFS

1. Create new module → Select "Scale-Out File Server"
2. Configure cluster settings:
   - Node names
   - Cluster IP
   - File share witness path
3. Generated scripts:
   - Install-SOFS.ps1
   - Configure-Shares.ps1
   - Add-Node.ps1
4. Execute installation script
5. Manage shares through interface

## 🎯 Module Types Explained

### Web Application
- HTML/CSS/JS structure
- Package.json for dependencies
- Server.js for backend
- Can be hosted on IIS, Apache, or Node.js

### API Service
- RESTful API structure
- Express.js setup
- Route configuration
- Database integration

### SOFS (Scale-Out File Server)
- Windows Server clustering
- SMB share management
- High availability
- Load balancing

### IRC Server (InspIRCd)
- Chat server configuration
- Channel management
- User authentication
- Module support

### Shoutcast Server
- Audio streaming
- Playlist management
- Listener statistics
- DJ accounts

### Docusaurus
- Documentation site
- Markdown support
- Versioning
- Search functionality

## 🔐 Security Considerations

- All PowerShell scripts run with `-ExecutionPolicy Bypass`
- Service credentials should be stored in .env
- Use Windows Credential Manager for sensitive data
- Network deployments require proper authentication
- IRC bot commands should be restricted

## 🚦 API Endpoints

### Modules
- `GET /api/modules` - List all modules
- `POST /api/modules` - Create new module
- `DELETE /api/modules/:id` - Delete module

### Files
- `GET /api/files?path=` - List files
- `POST /api/files/upload` - Upload files
- `POST /api/files/save` - Save file content
- `POST /api/files/zip` - Create ZIP archive

### Services
- `GET /api/services` - List services
- `POST /api/services` - Create service
- `POST /api/services/:id/start` - Start service
- `POST /api/services/:id/stop` - Stop service
- `POST /api/services/:id/restart` - Restart service

### Deployments
- `GET /api/deployments` - List deployments
- `POST /api/deploy` - Deploy application

### IRC
- `POST /api/irc/command` - Send IRC command
- `GET /api/irc/logs` - Get chat logs

### Scripts
- `GET /api/scripts` - List scripts
- `POST /api/scripts` - Upload script
- `POST /api/execute` - Execute script
- `DELETE /api/scripts/:id` - Delete script

## 🎨 Customization

### Adding New Module Types

1. Update `moduleTypes` array in frontend
2. Add template generator in backend:
   ```javascript
   function generateFileTemplate(type, fileName, config) {
     // Add your templates
   }
   ```
3. Create PowerShell scripts for the module
4. Update database schema if needed

### Custom Bot Commands

1. Add to `processBotCommand()` function:
   ```javascript
   const commands = {
     '!mycmd': 'Custom response',
     // Add more commands
   };
   ```
2. Create training data in database
3. Link to actual functions

## 📊 Database Schema

### Tables
- `modules` - Custom modules
- `services` - Managed services
- `deployments` - Deployment history
- `scripts` - PowerShell scripts
- `execution_logs` - Script execution logs
- `resources` - Cloud resources
- `iac_templates` - IaC templates
- `irc_logs` - IRC chat logs
- `bot_training` - Bot command training

## 🐛 Troubleshooting

### Services won't start
- Check port availability
- Verify directory paths
- Ensure dependencies installed
- Check execution logs

### Deployment fails
- Verify target server accessibility
- Check credentials
- Ensure web server installed
- Review deployment logs

### IRC connection issues
- Verify server address/port
- Check firewall rules
- Ensure InspIRCd installed
- Review IRC logs

## 🔄 Roadmap

- [ ] Docker container support
- [ ] Kubernetes orchestration
- [ ] Azure DevOps integration
- [ ] GitLab CI/CD pipelines
- [ ] Ansible playbook generation
- [ ] Monitoring & alerting
- [ ] Multi-tenancy support
- [ ] RBAC (Role-Based Access Control)

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📧 Support

For issues and questions:
- GitHub Issues
- Email: support@devops-suite.com
- Documentation: https://docs.devops-suite.com

---

**DevOps Master Suite** - Making infrastructure management truly modular and automated.