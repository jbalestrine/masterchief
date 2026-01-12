const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const fs = require('fs').promises;
const { spawn, exec } = require('child_process');
const sqlite3 = require('sqlite3').verbose();
const dotenv = require('dotenv');
const multer = require('multer');
const archiver = require('archiver');
const util = require('util');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;
const SCRIPTS_DIR = path.join(__dirname, 'scripts');
const LOGS_DIR = path.join(__dirname, 'logs');
const MODULES_DIR = path.join(__dirname, 'modules');
const WEBAPPS_DIR = path.join(__dirname, 'webapps');
const DEPLOYMENTS_DIR = path.join(__dirname, 'deployments');
const DB_FILE = path.join(__dirname, 'devops.db');

const execPromise = util.promisify(exec);

// Multer setup for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadPath = req.body.path || MODULES_DIR;
    cb(null, uploadPath);
  },
  filename: (req, file, cb) => {
    cb(null, file.originalname);
  }
});
const upload = multer({ storage });

app.use(cors());
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ limit: '50mb', extended: true }));
app.use('/webapps', express.static(WEBAPPS_DIR));

const db = new sqlite3.Database(DB_FILE, (err) => {
  if (err) console.error('Database connection error:', err);
  else console.log('✓ Connected to SQLite database');
  initializeDatabase();
});

async function initializeDatabase() {
  const dirs = [SCRIPTS_DIR, LOGS_DIR, MODULES_DIR, WEBAPPS_DIR, DEPLOYMENTS_DIR];
  for (const dir of dirs) {
    try {
      await fs.mkdir(dir, { recursive: true });
    } catch (e) {}
  }

  db.serialize(() => {
    // Existing tables
    db.run(`
      CREATE TABLE IF NOT EXISTS scripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        content TEXT NOT NULL,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        execCount INTEGER DEFAULT 0,
        lastRun DATETIME,
        avgDuration REAL DEFAULT 0
      )
    `);

    db.run(`
      CREATE TABLE IF NOT EXISTS execution_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scriptName TEXT NOT NULL,
        status TEXT NOT NULL,
        output TEXT,
        duration REAL,
        executedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        exitCode INTEGER,
        FOREIGN KEY(scriptName) REFERENCES scripts(name)
      )
    `);

    db.run(`
      CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL,
        status TEXT NOT NULL,
        cost REAL DEFAULT 0,
        region TEXT NOT NULL,
        metadata TEXT,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    db.run(`
      CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT,
        updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    db.run(`
      CREATE TABLE IF NOT EXISTS iac_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        type TEXT,
        resourceType TEXT,
        environment TEXT,
        region TEXT,
        template TEXT,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // New tables for modular features
    db.run(`
      CREATE TABLE IF NOT EXISTS modules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL,
        description TEXT,
        features TEXT,
        scripts TEXT,
        ports TEXT,
        config TEXT,
        status TEXT DEFAULT 'inactive',
        directory TEXT,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    db.run(`
      CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL,
        port INTEGER NOT NULL,
        directory TEXT NOT NULL,
        autoStart BOOLEAN DEFAULT 0,
        config TEXT,
        status TEXT DEFAULT 'stopped',
        pid INTEGER,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    db.run(`
      CREATE TABLE IF NOT EXISTS deployments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        target TEXT NOT NULL,
        type TEXT NOT NULL,
        server TEXT NOT NULL,
        sourceDir TEXT,
        targetPath TEXT,
        status TEXT DEFAULT 'pending',
        output TEXT,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    db.run(`
      CREATE TABLE IF NOT EXISTS irc_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        message TEXT NOT NULL,
        response TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    db.run(`
      CREATE TABLE IF NOT EXISTS bot_training (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        command TEXT UNIQUE NOT NULL,
        action TEXT NOT NULL,
        parameters TEXT,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);
  });
}

// ==================== MODULES API ====================

app.get('/api/modules', (req, res) => {
  db.all('SELECT * FROM modules ORDER BY createdAt DESC', (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    const modules = rows.map(row => ({
      ...row,
      features: JSON.parse(row.features || '[]'),
      scripts: JSON.parse(row.scripts || '[]'),
      ports: JSON.parse(row.ports || '[]'),
      config: JSON.parse(row.config || '{}')
    }));
    res.json(modules);
  });
});

app.post('/api/modules', async (req, res) => {
  const { name, type, description, features, scripts, ports, config } = req.body;

  if (!name || !type) {
    return res.status(400).json({ error: 'Name and type are required' });
  }

  try {
    // Create module directory
    const moduleDir = path.join(MODULES_DIR, name);
    await fs.mkdir(moduleDir, { recursive: true });

    // Generate module structure
    await generateModuleStructure(moduleDir, type, config);

    // Generate PowerShell scripts for the module
    const generatedScripts = await generateModuleScripts(name, type, config);

    db.run(
      `INSERT INTO modules (name, type, description, features, scripts, ports, config, directory) 
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        name,
        type,
        description,
        JSON.stringify(features || []),
        JSON.stringify(generatedScripts),
        JSON.stringify(ports || []),
        JSON.stringify(config || {}),
        moduleDir
      ],
      function (err) {
        if (err) {
          if (err.message.includes('UNIQUE')) {
            return res.status(409).json({ error: 'Module name already exists' });
          }
          return res.status(500).json({ error: err.message });
        }

        res.status(201).json({
          id: this.lastID,
          name,
          type,
          scripts: generatedScripts,
          message: 'Module created successfully'
        });
      }
    );
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.delete('/api/modules/:id', (req, res) => {
  db.get('SELECT directory FROM modules WHERE id = ?', [req.params.id], async (err, row) => {
    if (err) return res.status(500).json({ error: err.message });
    if (!row) return res.status(404).json({ error: 'Module not found' });

    db.run('DELETE FROM modules WHERE id = ?', [req.params.id], async (err) => {
      if (err) return res.status(500).json({ error: err.message });

      try {
        await fs.rm(row.directory, { recursive: true, force: true });
      } catch (e) {}

      res.json({ message: 'Module deleted successfully' });
    });
  });
});

// ==================== FILE MANAGEMENT API ====================

app.get('/api/files', async (req, res) => {
  try {
    const requestedPath = req.query.path || '/';
    const basePath = MODULES_DIR;
    const fullPath = path.join(basePath, requestedPath);

    const files = await fs.readdir(fullPath, { withFileTypes: true });
    const fileList = await Promise.all(
      files.map(async (file) => {
        const filePath = path.join(fullPath, file.name);
        const stats = await fs.stat(filePath);
        return {
          name: file.name,
          isDirectory: file.isDirectory(),
          size: stats.size,
          modified: stats.mtime
        };
      })
    );

    res.json({ path: requestedPath, files: fileList });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/files/upload', upload.array('files'), async (req, res) => {
  try {
    res.json({ message: 'Files uploaded successfully', files: req.files });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/files/save', async (req, res) => {
  try {
    const { path: filePath, content } = req.body;
    const fullPath = path.join(MODULES_DIR, filePath);
    await fs.writeFile(fullPath, content, 'utf8');
    res.json({ message: 'File saved successfully' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/files/zip', async (req, res) => {
  try {
    const { files, outputName, path: dirPath } = req.body;
    const zipPath = path.join(DEPLOYMENTS_DIR, outputName);
    const output = require('fs').createWriteStream(zipPath);
    const archive = archiver('zip', { zlib: { level: 9 } });

    output.on('close', () => {
      res.download(zipPath, outputName);
    });

    archive.on('error', (err) => {
      throw err;
    });

    archive.pipe(output);

    for (const file of files) {
      const filePath = path.join(MODULES_DIR, dirPath, file);
      archive.file(filePath, { name: file });
    }

    await archive.finalize();
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ==================== SERVICES API ====================

app.get('/api/services', (req, res) => {
  db.all('SELECT * FROM services ORDER BY createdAt DESC', (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    const services = rows.map(row => ({
      ...row,
      config: JSON.parse(row.config || '{}')
    }));
    res.json(services);
  });
});

app.post('/api/services', (req, res) => {
  const { name, type, port, directory, autoStart, config } = req.body;

  if (!name || !type) {
    return res.status(400).json({ error: 'Name and type are required' });
  }

  db.run(
    `INSERT INTO services (name, type, port, directory, autoStart, config) 
     VALUES (?, ?, ?, ?, ?, ?)`,
    [name, type, port, directory, autoStart ? 1 : 0, JSON.stringify(config || {})],
    function (err) {
      if (err) {
        if (err.message.includes('UNIQUE')) {
          return res.status(409).json({ error: 'Service name already exists' });
        }
        return res.status(500).json({ error: err.message });
      }

      res.status(201).json({
        id: this.lastID,
        name,
        type,
        message: 'Service created successfully'
      });
    }
  );
});

app.post('/api/services/:id/start', async (req, res) => {
  try {
    const service = await getService(req.params.id);
    const pid = await startService(service);
    
    db.run('UPDATE services SET status = ?, pid = ? WHERE id = ?', 
      ['running', pid, req.params.id]);

    res.json({ message: 'Service started', pid });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/services/:id/stop', async (req, res) => {
  try {
    const service = await getService(req.params.id);
    await stopService(service);
    
    db.run('UPDATE services SET status = ?, pid = NULL WHERE id = ?', 
      ['stopped', req.params.id]);

    res.json({ message: 'Service stopped' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/services/:id/restart', async (req, res) => {
  try {
    const service = await getService(req.params.id);
    await stopService(service);
    const pid = await startService(service);
    
    db.run('UPDATE services SET status = ?, pid = ? WHERE id = ?', 
      ['running', pid, req.params.id]);

    res.json({ message: 'Service restarted', pid });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ==================== DEPLOYMENT API ====================

app.get('/api/deployments', (req, res) => {
  db.all('SELECT * FROM deployments ORDER BY createdAt DESC LIMIT 50', (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows || []);
  });
});

app.post('/api/deploy', async (req, res) => {
  const { target, type, server, sourceDir, targetPath, installDependencies, autoConfig } = req.body;

  try {
    let output = '';
    
    // Check if server software is installed
    if (autoConfig) {
      const installScript = await generateInstallScript(server);
      const { stdout, stderr } = await execPromise(installScript);
      output += stdout + stderr;
    }

    // Create deployment package
    const deploymentName = `deployment-${Date.now()}`;
    const zipPath = path.join(DEPLOYMENTS_DIR, `${deploymentName}.zip`);
    await createDeploymentPackage(sourceDir, zipPath);

    // Generate deployment script
    const deployScript = await generateDeploymentScript(
      target,
      type,
      server,
      zipPath,
      targetPath,
      installDependencies
    );

    // Save deployment script
    const scriptPath = path.join(DEPLOYMENTS_DIR, `${deploymentName}.ps1`);
    await fs.writeFile(scriptPath, deployScript, 'utf8');

    // Execute deployment
    if (target === 'local' || target === 'frontend') {
      const { stdout, stderr } = await execPromise(`powershell -File "${scriptPath}"`);
      output += stdout + stderr;
    }

    db.run(
      `INSERT INTO deployments (name, target, type, server, sourceDir, targetPath, status, output) 
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      [deploymentName, target, type, server, sourceDir, targetPath, 'completed', output],
      function (err) {
        if (err) return res.status(500).json({ error: err.message });

        res.json({
          id: this.lastID,
          name: deploymentName,
          message: 'Deployment completed successfully',
          output
        });
      }
    );
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ==================== IRC API ====================

app.post('/api/irc/command', async (req, res) => {
  const { command } = req.body;

  try {
    let response = '';
    
    // Process bot commands
    if (command.startsWith('!')) {
      response = await processBotCommand(command);
    } else {
      response = 'Message sent to channel';
    }

    db.run(
      `INSERT INTO irc_logs (type, message, response) VALUES (?, ?, ?)`,
      ['command', command, response]
    );

    res.json({ output: response });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/irc/logs', (req, res) => {
  db.all('SELECT * FROM irc_logs ORDER BY timestamp DESC LIMIT 100', (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows || []);
  });
});

// ==================== UTILITY FUNCTIONS ====================

async function generateModuleStructure(moduleDir, type, config) {
  const structure = {
    webapp: ['index.html', 'style.css', 'script.js', 'package.json'],
    api: ['server.js', 'routes.js', 'package.json'],
    sofs: ['setup.ps1', 'config.xml', 'scale-out.ps1'],
    irc: ['inspircd.conf', 'start.sh', 'modules.conf'],
    shoutcast: ['sc_serv.conf', 'start.sh'],
    docusaurus: ['docusaurus.config.js', 'sidebars.js', 'package.json'],
    nodejs: ['server.js', 'package.json'],
    custom: ['main.js', 'config.json']
  };

  const files = structure[type] || structure.custom;

  for (const file of files) {
    const filePath = path.join(moduleDir, file);
    const content = await generateFileTemplate(type, file, config);
    await fs.writeFile(filePath, content, 'utf8');
  }
}

async function generateModuleScripts(name, type, config) {
  const scripts = [];
  
  // Generate install script
  scripts.push({
    name: `Install-${name}.ps1`,
    content: generateInstallScriptContent(type, name, config)
  });

  // Generate start script
  scripts.push({
    name: `Start-${name}.ps1`,
    content: generateStartScriptContent(type, name, config)
  });

  // Generate stop script
  scripts.push({
    name: `Stop-${name}.ps1`,
    content: generateStopScriptContent(type, name)
  });

  // Generate deploy script
  scripts.push({
    name: `Deploy-${name}.ps1`,
    content: generateDeployScriptContent(type, name, config)
  });

  // Save scripts to database and files
  for (const script of scripts) {
    const scriptPath = path.join(SCRIPTS_DIR, script.name);
    await fs.writeFile(scriptPath, script.content, 'utf8');

    await new Promise((resolve, reject) => {
      db.run(
        `INSERT OR IGNORE INTO scripts (name, category, description, content) VALUES (?, ?, ?, ?)`,
        [script.name, type, `Auto-generated script for ${name}`, script.content],
        (err) => {
          if (err) reject(err);
          else resolve();
        }
      );
    });
  }

  return scripts.map(s => s.name);
}

function generateInstallScriptContent(type, name, config) {
  const templates = {
    sofs: `
# SOFS Installation Script
param(
    [string]$ClusterName = "${name}",
    [string[]]$Nodes = @("Node1", "Node2"),
    [string]$FileShareWitness = "\\\\FileServer\\Witness"
)

Write-Host "Installing Scale-Out File Server: $ClusterName" -ForegroundColor Green

# Install required features
Install-WindowsFeature -Name Failover-Clustering, FS-FileServer -IncludeManagementTools

# Create cluster
New-Cluster -Name $ClusterName -Node $Nodes -StaticAddress ${config.clusterIP || '10.0.0.100'}

# Configure File Share Witness
Set-ClusterQuorum -FileShareWitness $FileShareWitness

# Create SOFS role
Add-ClusterScaleOutFileServerRole -Name "$ClusterName-SOFS"

# Create file shares
$shares = @("Share1", "Share2", "Share3")
foreach ($share in $shares) {
    New-SmbShare -Name $share -Path "C:\\ClusterStorage\\Volume1\\$share" -FullAccess Everyone
}

Write-Host "SOFS installation completed successfully!" -ForegroundColor Green
    `,
    webapp: `
# Web Application Installation Script
param(
    [string]$ServerType = "${config.server || 'iis'}",
    [string]$AppPath = "C:\\inetpub\\wwwroot\\${name}",
    [int]$Port = ${config.port || 80}
)

Write-Host "Installing Web Application: ${name}" -ForegroundColor Green

if ($ServerType -eq "iis") {
    Install-WindowsFeature -Name Web-Server -IncludeManagementTools
    New-WebSite -Name "${name}" -Port $Port -PhysicalPath $AppPath
} elseif ($ServerType -eq "nodejs") {
    npm install
    npm start
}

Write-Host "Web application installed successfully!" -ForegroundColor Green
    `,
    irc: `
# IRC Server Installation Script
param(
    [string]$ServerName = "${name}",
    [int]$Port = ${config.port || 6667}
)

Write-Host "Installing InspIRCd Server: $ServerName" -ForegroundColor Green

# Download and install InspIRCd (Windows)
# This would download from official source
# For demo purposes, assuming it's already available

# Configure inspircd.conf
$config = @"
<server name="$ServerName" description="IRC Server">
<bind address="" port="$Port" type="clients">
"@

Set-Content -Path "inspircd.conf" -Value $config

Write-Host "IRC server installed successfully!" -ForegroundColor Green
    `
  };

  return templates[type] || `# Installation script for ${name}\nWrite-Host "Installing ${name}..." -ForegroundColor Green`;
}

function generateStartScriptContent(type, name, config) {
  return `
# Start ${name} Service
param([string]$ConfigPath = ".")

Write-Host "Starting ${name}..." -ForegroundColor Green

$serviceName = "${name}"
$status = Get-Service -Name $serviceName -ErrorAction SilentlyContinue

if ($status) {
    Start-Service -Name $serviceName
    Write-Host "Service started: $serviceName" -ForegroundColor Green
} else {
    Write-Host "Service not found: $serviceName" -ForegroundColor Yellow
}
  `;
}

function generateStopScriptContent(type, name) {
  return `
# Stop ${name} Service
Write-Host "Stopping ${name}..." -ForegroundColor Yellow

$serviceName = "${name}"
Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
Write-Host "Service stopped: $serviceName" -ForegroundColor Green
  `;
}

function generateDeployScriptContent(type, name, config) {
  return `
# Deploy ${name}
param(
    [string]$SourcePath,
    [string]$TargetPath,
    [string]$Server = "localhost"
)

Write-Host "Deploying ${name} to $Server..." -ForegroundColor Cyan

# Create deployment package
Compress-Archive -Path $SourcePath -DestinationPath "$name.zip"

# Copy to target
Copy-Item -Path "$name.zip" -Destination $TargetPath -Force

# Extract on target
Expand-Archive -Path "$TargetPath\\$name.zip" -DestinationPath $TargetPath -Force

Write-Host "Deployment completed successfully!" -ForegroundColor Green
  `;
}

async function generateFileTemplate(type, fileName, config) {
  const templates = {
    'index.html': `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${config.title || 'My App'}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>Welcome to ${config.title || 'My App'}</h1>
    <div id="app"></div>
    <script src="script.js"></script>
</body>
</html>`,
    'style.css': `* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: Arial, sans-serif; padding: 20px; }
h1 { color: #333; }`,
    'script.js': `console.log('App loaded');
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('app').innerHTML = '<p>Application is running!</p>';
});`,
    'package.json': JSON.stringify({
      name: config.name || 'my-app',
      version: '1.0.0',
      main: 'server.js',
      scripts: {
        start: 'node server.js',
        dev: 'nodemon server.js'
      },
      dependencies: {
        express: '^4.18.2'
      }
    }, null, 2),
    'server.js': `const express = require('express');
const app = express();
const PORT = ${config.port || 3000};

app.get('/', (req, res) => {
    res.send('Server is running!');
});

app.listen(PORT, () => {
    console.log(\`Server running on port \${PORT}\`);
});`
  };

  return templates[fileName] || `// ${fileName}\n// Auto-generated file`;
}

async function generateInstallScript(serverType) {
  const scripts = {
    iis: 'Install-WindowsFeature -Name Web-Server -IncludeManagementTools',
    apache: 'choco install apache-httpd -y',
    xampp: 'choco install xampp-81 -y',
    nodejs: 'choco install nodejs -y'
  };

  return `powershell -Command "${scripts[serverType] || 'echo "Unknown server type"'}"`;
}

async function createDeploymentPackage(sourceDir, zipPath) {
  return new Promise((resolve, reject) => {
    const output = require('fs').createWriteStream(zipPath);
    const archive = archiver('zip', { zlib: { level: 9 } });

    output.on('close', resolve);
    archive.on('error', reject);

    archive.pipe(output);
    archive.directory(sourceDir, false);
    archive.finalize();
  });
}

async function generateDeploymentScript(target, type, server, zipPath, targetPath, installDeps) {
  return `
# Deployment Script
param(
    [string]$ZipPath = "${zipPath}",
    [string]$TargetPath = "${targetPath}",
    [string]$ServerType = "${server}"
)

Write-Host "Starting deployment..." -ForegroundColor Cyan

# Extract package
Expand-Archive -Path $ZipPath -DestinationPath $TargetPath -Force

${installDeps ? '# Install dependencies\ncd $TargetPath\nnpm install' : ''}

# Configure web server
if ($ServerType -eq "iis") {
    Import-Module WebAdministration
    New-Website -Name "DeployedApp" -Port 80 -PhysicalPath $TargetPath
} elseif ($ServerType -eq "nodejs") {
    Start-Process node -ArgumentList "server.js" -WorkingDirectory $TargetPath
}

Write-Host "Deployment completed!" -ForegroundColor Green
  `;
}

async function processBotCommand(command) {
  const commands = {
    '!help': 'Available commands: !help, !status, !deploy, !services, !modules',
    '!status': 'System Status: All services running',
    '!services': 'Checking services...',
    '!modules': 'Loading modules list...',
    '!deploy': 'Starting deployment process...'
  };

  const cmd = command.split(' ')[0];
  return commands[cmd] || 'Unknown command. Type !help for available commands.';
}

function getService(id) {
  return new Promise((resolve, reject) => {
    db.get('SELECT * FROM services WHERE id = ?', [id], (err, row) => {
      if (err) reject(err);
      else if (!row) reject(new Error('Service not found'));
      else resolve({ ...row, config: JSON.parse(row.config || '{}') });
    });
  });
}

async function startService(service) {
  // This is a simplified example
  // In production, you'd use proper process management (PM2, systemd, etc.)
  return new Promise((resolve, reject) => {
    const proc = spawn('node', [path.join(service.directory, 'server.js')], {
      detached: true,
      stdio: 'ignore'
    });
    proc.unref();
    resolve(proc.pid);
  });
}

async function stopService(service) {
  if (service.pid) {
    try {
      process.kill(service.pid);
    } catch (e) {
      // Process might already be dead
    }
  }
}

// ==================== EXISTING ENDPOINTS (from original) ====================

app.get('/api/scripts', (req, res) => {
  db.all('SELECT * FROM scripts ORDER BY name ASC', (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows || []);
  });
});

app.post('/api/scripts', (req, res) => {
  const { name, category, description, content } = req.body;

  if (!name || !content) {
    return res.status(400).json({ error: 'Name and content are required' });
  }

  db.run(
    'INSERT INTO scripts (name, category, description, content) VALUES (?, ?, ?, ?)',
    [name, category, description, content],
    function (err) {
      if (err) {
        if (err.message.includes('UNIQUE')) {
          return res.status(409).json({ error: 'Script name already exists' });
        }
        return res.status(500).json({ error: err.message });
      }

      res.status(201).json({ id: this.lastID, name, category, description, content });
    }
  );
});

app.get('/api/stats', (req, res) => {
  const stats = {};

  db.get('SELECT COUNT(*) as count FROM scripts', (err, row) => {
    stats.totalScripts = row?.count || 0;
  });

  db.get('SELECT COUNT(*) as count FROM modules', (err, row) => {
    stats.totalModules = row?.count || 0;
  });

  db.get('SELECT COUNT(*) as count FROM services WHERE status = "running"', (err, row) => {
    stats.activeServices = row?.count || 0;
  });

  db.get('SELECT COUNT(*) as count FROM deployments', (err, row) => {
    stats.totalDeployments = row?.count || 0;
    res.json(stats);
  });
});

app.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║         DevOps Master Suite API Server                   ║
║         Running on http://localhost:${PORT}                   ║
║         Enhanced Modular Platform                         ║
╚═══════════════════════════════════════════════════════════╝
  `);
});

module.exports = app;