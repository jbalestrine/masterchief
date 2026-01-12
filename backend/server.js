const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const fs = require('fs').promises;
const { spawn } = require('child_process');
const sqlite3 = require('sqlite3').verbose();
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;
const SCRIPTS_DIR = path.join(__dirname, 'scripts');
const LOGS_DIR = path.join(__dirname, 'logs');
const DB_FILE = path.join(__dirname, 'devops.db');

app.use(cors());
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ limit: '50mb', extended: true }));

const db = new sqlite3.Database(DB_FILE, (err) => {
  if (err) console.error('Database connection error:', err);
  else console.log('✓ Connected to SQLite database');
  initializeDatabase();
});

async function initializeDatabase() {
  const dirs = [SCRIPTS_DIR, LOGS_DIR];
  for (const dir of dirs) {
    try {
      await fs.mkdir(dir, { recursive: true });
    } catch (e) {}
  }

  db.serialize(() => {
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
  });
}

// ==================== SCRIPTS ====================

app.get('/api/scripts', (req, res) => {
  db.all('SELECT * FROM scripts ORDER BY name ASC', (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows || []);
  });
});

app.get('/api/scripts/:id', (req, res) => {
  db.get('SELECT * FROM scripts WHERE id = ?', [req.params.id], (err, row) => {
    if (err) return res.status(500).json({ error: err.message });
    if (!row) return res.status(404).json({ error: 'Script not found' });
    res.json(row);
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

      saveScriptFile(name, content);

      res.status(201).json({
        id: this.lastID,
        name,
        category,
        description,
        content,
        execCount: 0,
        lastRun: null,
        avgDuration: 0
      });
    }
  );
});

app.put('/api/scripts/:id', (req, res) => {
  const { name, category, description, content } = req.body;

  db.run(
    'UPDATE scripts SET name = ?, category = ?, description = ?, content = ?, updatedAt = CURRENT_TIMESTAMP WHERE id = ?',
    [name, category, description, content, req.params.id],
    function (err) {
      if (err) {
        if (err.message.includes('UNIQUE')) {
          return res.status(409).json({ error: 'Script name already exists' });
        }
        return res.status(500).json({ error: err.message });
      }

      saveScriptFile(name, content);

      res.json({ message: 'Script updated successfully' });
    }
  );
});

app.delete('/api/scripts/:id', (req, res) => {
  db.get('SELECT name FROM scripts WHERE id = ?', [req.params.id], (err, row) => {
    if (err) return res.status(500).json({ error: err.message });
    if (!row) return res.status(404).json({ error: 'Script not found' });

    db.run('DELETE FROM scripts WHERE id = ?', [req.params.id], (err) => {
      if (err) return res.status(500).json({ error: err.message });

      try {
        fs.unlink(path.join(SCRIPTS_DIR, row.name));
      } catch (e) {}

      res.json({ message: 'Script deleted successfully' });
    });
  });
});

// ==================== EXECUTION ====================

app.post('/api/execute', (req, res) => {
  const { scriptName, params = {} } = req.body;

  if (!scriptName) {
    return res.status(400).json({ error: 'Script name is required' });
  }

  db.get('SELECT content FROM scripts WHERE name = ?', [scriptName], (err, row) => {
    if (err) return res.status(500).json({ error: err.message });
    if (!row) return res.status(404).json({ error: 'Script not found' });

    const executionId = Date.now();
    const startTime = Date.now();

    const ps = spawn('powershell.exe', [
      '-NoProfile',
      '-ExecutionPolicy', 'Bypass',
      '-File', path.join(SCRIPTS_DIR, scriptName),
      ...flattenParams(params)
    ]);

    let stdout = '';
    let stderr = '';

    ps.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    ps.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    ps.on('close', (code) => {
      const duration = (Date.now() - startTime) / 1000;
      const status = code === 0 ? 'success' : 'failed';

      db.run(
        `INSERT INTO execution_logs (scriptName, status, output, duration, exitCode) 
         VALUES (?, ?, ?, ?, ?)`,
        [scriptName, status, stdout + stderr, duration, code],
        () => {
          db.run(
            `UPDATE scripts SET execCount = execCount + 1, lastRun = CURRENT_TIMESTAMP WHERE name = ?`,
            [scriptName]
          );
        }
      );

      res.json({
        executionId,
        status,
        output: stdout + stderr,
        duration: duration.toFixed(2),
        exitCode: code,
        timestamp: new Date().toISOString()
      });
    });

    ps.on('error', (err) => {
      res.status(500).json({
        error: 'Failed to execute script',
        message: err.message
      });
    });
  });
});

// ==================== RESOURCES ====================

app.get('/api/resources', (req, res) => {
  db.all('SELECT * FROM resources ORDER BY name ASC', (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows || []);
  });
});

app.post('/api/resources', (req, res) => {
  const { name, type, status, cost, region, metadata } = req.body;

  db.run(
    'INSERT INTO resources (name, type, status, cost, region, metadata) VALUES (?, ?, ?, ?, ?, ?)',
    [name, type, status, cost, region, JSON.stringify(metadata || {})],
    function (err) {
      if (err) {
        if (err.message.includes('UNIQUE')) {
          return res.status(409).json({ error: 'Resource name already exists' });
        }
        return res.status(500).json({ error: err.message });
      }

      res.status(201).json({
        id: this.lastID,
        name,
        type,
        status,
        cost,
        region,
        metadata: metadata || {}
      });
    }
  );
});

app.put('/api/resources/:id', (req, res) => {
  const { name, type, status, cost, region, metadata } = req.body;

  db.run(
    `UPDATE resources SET name = ?, type = ?, status = ?, cost = ?, region = ?, 
     metadata = ?, updatedAt = CURRENT_TIMESTAMP WHERE id = ?`,
    [name, type, status, cost, region, JSON.stringify(metadata || {}), req.params.id],
    function (err) {
      if (err) return res.status(500).json({ error: err.message });
      if (this.changes === 0) return res.status(404).json({ error: 'Resource not found' });

      res.json({ message: 'Resource updated successfully' });
    }
  );
});

app.delete('/api/resources/:id', (req, res) => {
  db.run('DELETE FROM resources WHERE id = ?', [req.params.id], function (err) {
    if (err) return res.status(500).json({ error: err.message });
    if (this.changes === 0) return res.status(404).json({ error: 'Resource not found' });

    res.json({ message: 'Resource deleted successfully' });
  });
});

// ==================== LOGS ====================

app.get('/api/logs', (req, res) => {
  const limit = req.query.limit || 50;
  const scriptName = req.query.scriptName;

  let query = 'SELECT * FROM execution_logs';
  const params = [];

  if (scriptName) {
    query += ' WHERE scriptName = ?';
    params.push(scriptName);
  }

  query += ' ORDER BY executedAt DESC LIMIT ?';
  params.push(limit);

  db.all(query, params, (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows || []);
  });
});

app.delete('/api/logs', (req, res) => {
  const daysOld = req.query.daysOld || 30;
  const date = new Date(Date.now() - daysOld * 24 * 60 * 60 * 1000).toISOString();

  db.run('DELETE FROM execution_logs WHERE executedAt < ?', [date], function (err) {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ message: `Deleted ${this.changes} log entries` });
  });
});

// ==================== CONFIG ====================

app.get('/api/config', (req, res) => {
  db.all('SELECT key, value FROM config', (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });

    const config = {};
    (rows || []).forEach(row => {
      config[row.key] = row.value;
    });

    res.json(config);
  });
});

app.post('/api/config', (req, res) => {
  const { key, value } = req.body;

  if (!key) {
    return res.status(400).json({ error: 'Key is required' });
  }

  db.run(
    'INSERT OR REPLACE INTO config (key, value, updatedAt) VALUES (?, ?, CURRENT_TIMESTAMP)',
    [key, value],
    (err) => {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ key, value, message: 'Configuration updated' });
    }
  );
});

// ==================== STATS ====================

app.get('/api/stats', (req, res) => {
  const stats = {};

  db.get('SELECT COUNT(*) as count FROM scripts', (err, row) => {
    stats.totalScripts = row?.count || 0;
  });

  db.get('SELECT COUNT(*) as count FROM resources WHERE status = "running"', (err, row) => {
    stats.activeResources = row?.count || 0;
  });

  db.get('SELECT COUNT(*) as count FROM resources', (err, row) => {
    stats.totalResources = row?.count || 0;
  });

  db.get('SELECT SUM(cost) as total FROM resources', (err, row) => {
    stats.monthlyCost = row?.total || 0;
  });

  db.get('SELECT SUM(execCount) as total FROM scripts', (err, row) => {
    stats.totalExecutions = row?.total || 0;
  });

  db.all(
    'SELECT * FROM execution_logs ORDER BY executedAt DESC LIMIT 10',
    (err, rows) => {
      stats.recentActivity = rows || [];
      res.json(stats);
    }
  );
});

// ==================== UTILITY ====================

async function saveScriptFile(name, content) {
  try {
    await fs.mkdir(SCRIPTS_DIR, { recursive: true });
    await fs.writeFile(path.join(SCRIPTS_DIR, name), content, 'utf8');
  } catch (err) {
    console.error('Error saving script file:', err);
  }
}

function flattenParams(params) {
  const result = [];
  for (const [key, value] of Object.entries(params)) {
    result.push(`-${key}`);
    result.push(String(value));
  }
  return result;
}

// ==================== ERROR HANDLING ====================

app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({
    error: 'Internal server error',
    message: err.message
  });
});

// ==================== START ====================
// ==================== IaC ROUTES ====================

// Create IaC templates table if not exists
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

// Generate IaC template
app.post('/api/iac/generate', (req, res) => {
  const { name, type, resourceType, environment, region, config } = req.body;

  let template = '';

  if (type === 'terraform') {
    template = generateTerraformTemplate(resourceType, environment, region, name, config);
  } else if (type === 'arm') {
    template = generateArmTemplate(resourceType, environment, region, name, config);
  } else if (type === 'bicep') {
    template = generateBicepTemplate(resourceType, environment, region, name, config);
  }

  db.run(
    `INSERT INTO iac_templates (name, type, resourceType, environment, region, template) VALUES (?, ?, ?, ?, ?, ?)`,
    [name, type, resourceType, environment, region, template],
    function(err) {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ id: this.lastID, name, type, resourceType, environment, region, createdAt: new Date().toISOString() });
    }
  );
});

// Get all IaC templates
app.get('/api/iac/templates', (req, res) => {
  db.all(`SELECT id, name, type, resourceType, environment, region, createdAt FROM iac_templates ORDER BY createdAt DESC`, [], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows || []);
  });
});

// Download IaC template
app.get('/api/iac/download/:id', (req, res) => {
  db.get(`SELECT template, name, type FROM iac_templates WHERE id = ?`, [req.params.id], (err, row) => {
    if (err || !row) return res.status(404).json({ error: 'Template not found' });
    
    const ext = row.type === 'terraform' ? 'tf' : row.type === 'arm' ? 'json' : 'bicep';
    const filename = `${row.name}.${ext}`;
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
    res.setHeader('Content-Type', row.type === 'arm' ? 'application/json' : 'text/plain');
    res.send(row.template);
  });
});

// Delete IaC template
app.delete('/api/iac/templates/:id', (req, res) => {
  db.run(`DELETE FROM iac_templates WHERE id = ?`, [req.params.id], function(err) {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ success: true });
  });
});

// ==================== TEMPLATE GENERATORS ====================

function generateTerraformTemplate(resourceType, environment, region, name, config = {}) {
  const vmCount = (config && config.vmCount) || 1;
  const vmSize = (config && config.vmSize) || 'Standard_D2s_v3';
  const diskType = (config && config.diskType) || 'Premium_LRS';
  const diskSize = (config && config.diskSize) || 128;
  const vnetAddressSpace = (config && config.vnetAddressSpace) || '10.0.0.0/16';
  const subnetAddressSpace = (config && config.subnetAddressSpace) || '10.0.1.0/24';
  const enablePublicIP = (config && config.enablePublicIP !== false) || true;
  const enableInternalLB = (config && config.enableInternalLB) || false;
  const enableExternalLB = (config && config.enableExternalLB) || false;
  const allowedPorts = (config && config.allowedPorts) || '3389,5985,5986';
  const enableAKS = (config && config.enableAKS) || false;
  const aksNodeCount = (config && config.aksNodeCount) || 3;
  const aksVMSize = (config && config.aksVMSize) || 'Standard_D2s_v3';
  const enableSQL = (config && config.enableSQL) || false;
  const adminUsername = (config && config.adminUsername) || 'azureadmin';

  let template = `terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

variable "environment" {
  type    = string
  default = "${environment}"
}

variable "region" {
  type    = string
  default = "${region}"
}

variable "admin_password" {
  type      = string
  sensitive = true
  default   = "ChangeMe@123"
}

resource "azurerm_resource_group" "main" {
  name     = "${environment}-rg-${region}"
  location = var.region

  tags = {
    Environment = var.environment
  }
}

resource "azurerm_virtual_network" "main" {
  name                = "${environment}-vnet-${region}"
  address_space       = ["${vnetAddressSpace}"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_subnet" "internal" {
  name                 = "internal"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["${subnetAddressSpace}"]
}

resource "azurerm_network_security_group" "main" {
  name                = "${environment}-nsg-${region}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "AllowRDP"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "3389"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowWinRM"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "5985-5986"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}
`;

  // Add NIC and VM resources
  for (let i = 0; i < vmCount; i++) {
    template += `
resource "azurerm_network_interface" "nic${i}" {
  name                = "${environment}-nic-${i+1}-${region}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "config${i+1}"
    subnet_id                     = azurerm_subnet.internal.id
    private_ip_address_allocation = "Dynamic"
    ${enablePublicIP ? `public_ip_address_id          = azurerm_public_ip.pip${i}.id` : ''}
  }
}
`;

    if (enablePublicIP) {
      template += `
resource "azurerm_public_ip" "pip${i}" {
  name                = "${environment}-pip-${i+1}-${region}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
}
`;
    }

    template += `
resource "azurerm_windows_virtual_machine" "vm${i}" {
  name                = "${environment}-vm-${i+1}-${region}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  size                = "${vmSize}"

  admin_username = "${adminUsername}"
  admin_password = var.admin_password

  disable_password_authentication = false

  network_interface_ids = [
    azurerm_network_interface.nic${i}.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "${diskType}"
    disk_size_gb         = ${diskSize}
  }

  source_image_reference {
    publisher = "MicrosoftWindowsServer"
    offer     = "WindowsServer"
    sku       = "2022-Datacenter"
    version   = "latest"
  }

  tags = {
    Environment = var.environment
  }
}
`;
  }

  if (enableInternalLB) {
    template += `
resource "azurerm_lb" "internal" {
  name                = "${environment}-ilb-${region}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  load_balancer_sku   = "Standard"

  frontend_ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.internal.id
    private_ip_address_allocation = "Dynamic"
  }
}
`;
  }

  if (enableExternalLB) {
    template += `
resource "azurerm_public_ip" "lbpip" {
  name                = "${environment}-lbpip-${region}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_lb" "external" {
  name                = "${environment}-elb-${region}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  load_balancer_sku   = "Standard"

  frontend_ip_configuration {
    name                 = "external"
    public_ip_address_id = azurerm_public_ip.lbpip.id
  }
}
`;
  }

  if (enableSQL) {
    template += `
resource "azurerm_mssql_server" "sql" {
  name                         = "${environment}-sql-${region}"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = "${adminUsername}"
  administrator_login_password = var.admin_password

  tags = {
    Environment = var.environment
  }
}

resource "azurerm_mssql_database" "sqldb" {
  name           = "${environment}-db"
  server_id      = azurerm_mssql_server.sql.id
  collation      = "SQL_Latin1_General_CP1_CI_AS"
  sku_name       = "S0"
}
`;
  }

  if (enableAKS) {
    template += `
resource "azurerm_kubernetes_cluster" "aks" {
  name                = "${environment}-aks-${region}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "${environment}aks${region}"

  default_node_pool {
    name       = "default"
    node_count = ${aksNodeCount}
    vm_size    = "${aksVMSize}"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = var.environment
  }
}
`;
  }

  template += `
output "resource_group_id" {
  value = azurerm_resource_group.main.id
}

output "vnet_id" {
  value = azurerm_virtual_network.main.id
}
`;

  return template;
}

function generateArmTemplate(resourceType, environment, region, name, config = {}) {
  return JSON.stringify({
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
      "location": { "type": "string", "defaultValue": region },
      "environment": { "type": "string", "defaultValue": environment }
    },
    "variables": { "resourceGroupName": `${environment}-rg-${region}` },
    "resources": [{
      "type": "Microsoft.Resources/resourceGroups",
      "apiVersion": "2021-04-01",
      "name": `${environment}-rg-${region}`,
      "location": region
    }],
    "outputs": {
      "resourceGroupId": { "type": "string", "value": `${environment}-rg-${region}` }
    }
  }, null, 2);
}

function generateArmTemplate(resourceType, environment, region, name, config = {}) {
  const vmCount = (config && config.vmCount) || 1;
  const vmSize = (config && config.vmSize) || 'Standard_D2s_v3';
  const diskSize = (config && config.diskSize) || 128;
  const vnetAddressSpace = (config && config.vnetAddressSpace) || '10.0.0.0/16';
  const subnetAddressSpace = (config && config.subnetAddressSpace) || '10.0.1.0/24';
  const enablePublicIP = (config && config.enablePublicIP !== false) || true;
  const enableSQL = (config && config.enableSQL) || false;
  const enableAKS = (config && config.enableAKS) || false;
  const aksNodeCount = (config && config.aksNodeCount) || 3;
  const adminUsername = (config && config.adminUsername) || 'azureadmin';

  const template = {
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
      "location": { "type": "string", "defaultValue": region },
      "environment": { "type": "string", "defaultValue": environment },
      "vmCount": { "type": "int", "defaultValue": vmCount },
      "vmSize": { "type": "string", "defaultValue": vmSize },
      "adminUsername": { "type": "string", "defaultValue": adminUsername },
      "adminPassword": { "type": "securestring", "defaultValue": "ChangeMe@123" }
    },
    "variables": {
      "resourceGroupName": `${environment}-rg-${region}`,
      "vnetName": `${environment}-vnet-${region}`,
      "subnetName": "internal",
      "nsgName": `${environment}-nsg-${region}`
    },
    "resources": [
      {
        "type": "Microsoft.Network/networkSecurityGroups",
        "apiVersion": "2021-02-01",
        "name": "[variables('nsgName')]",
        "location": "[parameters('location')]",
        "properties": {
          "securityRules": [
            {
              "name": "AllowRDP",
              "properties": {
                "protocol": "Tcp",
                "sourcePortRange": "*",
                "destinationPortRange": "3389",
                "sourceAddressPrefix": "*",
                "destinationAddressPrefix": "*",
                "access": "Allow",
                "priority": 100,
                "direction": "Inbound"
              }
            },
            {
              "name": "AllowWinRM",
              "properties": {
                "protocol": "Tcp",
                "sourcePortRange": "*",
                "destinationPortRange": "5985-5986",
                "sourceAddressPrefix": "*",
                "destinationAddressPrefix": "*",
                "access": "Allow",
                "priority": 110,
                "direction": "Inbound"
              }
            }
          ]
        }
      },
      {
        "type": "Microsoft.Network/virtualNetworks",
        "apiVersion": "2021-02-01",
        "name": "[variables('vnetName')]",
        "location": "[parameters('location')]",
        "properties": {
          "addressSpace": { "addressPrefixes": ["${vnetAddressSpace}"] },
          "subnets": [
            {
              "name": "[variables('subnetName')]",
              "properties": {
                "addressPrefix": "${subnetAddressSpace}",
                "networkSecurityGroup": {
                  "id": "[resourceId('Microsoft.Network/networkSecurityGroups', variables('nsgName'))]"
                }
              }
            }
          ]
        },
        "dependsOn": [
          "[resourceId('Microsoft.Network/networkSecurityGroups', variables('nsgName'))]"
        ]
      }
    ],
    "outputs": {
      "resourceGroupId": { "type": "string", "value": `${environment}-rg-${region}` },
      "vnetId": { "type": "string", "value": `[resourceId('Microsoft.Network/virtualNetworks', variables('vnetName'))]` }
    }
  };

  if (enablePublicIP) {
    template.resources.push({
      "type": "Microsoft.Network/publicIPAddresses",
      "apiVersion": "2021-02-01",
      "name": `${environment}-pip-${region}`,
      "location": "[parameters('location')]",
      "sku": { "name": "Standard" },
      "properties": { "publicIPAllocationMethod": "Static" }
    });
  }

  if (enableSQL) {
    template.resources.push({
      "type": "Microsoft.Sql/servers",
      "apiVersion": "2019-06-01",
      "name": `${environment}-sql-${region}`,
      "location": "[parameters('location')]",
      "properties": {
        "administratorLogin": "[parameters('adminUsername')]",
        "administratorLoginPassword": "[parameters('adminPassword')]",
        "version": "12.0"
      }
    });
  }

  if (enableAKS) {
    template.resources.push({
      "type": "Microsoft.ContainerService/managedClusters",
      "apiVersion": "2021-05-01",
      "name": `${environment}-aks-${region}`,
      "location": "[parameters('location')]",
      "identity": { "type": "SystemAssigned" },
      "properties": {
        "dnsPrefix": `${environment}aks${region}`,
        "agentPoolProfiles": [
          {
            "name": "default",
            "count": aksNodeCount,
            "vmSize": "[parameters('vmSize')]",
            "osType": "Linux"
          }
        ]
      }
    });
  }

  return JSON.stringify(template, null, 2);
}

function generateBicepTemplate(resourceType, environment, region, name, config = {}) {
  const vmCount = (config && config.vmCount) || 1;
  const vmSize = (config && config.vmSize) || 'Standard_D2s_v3';
  const diskSize = (config && config.diskSize) || 128;
  const vnetAddressSpace = (config && config.vnetAddressSpace) || '10.0.0.0/16';
  const subnetAddressSpace = (config && config.subnetAddressSpace) || '10.0.1.0/24';
  const enablePublicIP = (config && config.enablePublicIP !== false) || true;
  const enableSQL = (config && config.enableSQL) || false;
  const enableAKS = (config && config.enableAKS) || false;
  const aksNodeCount = (config && config.aksNodeCount) || 3;
  const adminUsername = (config && config.adminUsername) || 'azureadmin';

  let template = `param location string = '${region}'
param environment string = '${environment}'
param vmCount int = ${vmCount}
param vmSize string = '${vmSize}'
param adminUsername string = '${adminUsername}'
@secure()
param adminPassword string = 'ChangeMe@123'

var resourceGroupName = '${environment}-rg-${region}'
var vnetName = '${environment}-vnet-${region}'
var subnetName = 'internal'
var nsgName = '${environment}-nsg-${region}'

resource nsg 'Microsoft.Network/networkSecurityGroups@2021-02-01' = {
  name: nsgName
  location: location
  properties: {
    securityRules: [
      {
        name: 'AllowRDP'
        properties: {
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '3389'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Allow'
          priority: 100
          direction: 'Inbound'
        }
      }
      {
        name: 'AllowWinRM'
        properties: {
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '5985-5986'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Allow'
          priority: 110
          direction: 'Inbound'
        }
      }
    ]
  }
}

resource vnet 'Microsoft.Network/virtualNetworks@2021-02-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '${vnetAddressSpace}'
      ]
    }
    subnets: [
      {
        name: subnetName
        properties: {
          addressPrefix: '${subnetAddressSpace}'
          networkSecurityGroup: {
            id: nsg.id
          }
        }
      }
    ]
  }
}
`;

  if (enablePublicIP) {
    template += `
resource pip 'Microsoft.Network/publicIPAddresses@2021-02-01' = {
  name: '${environment}-pip-${region}'
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {
    publicIPAllocationMethod: 'Static'
  }
}
`;
  }

  if (enableSQL) {
    template += `
resource sqlServer 'Microsoft.Sql/servers@2019-06-01' = {
  name: '${environment}-sql-${region}'
  location: location
  properties: {
    administratorLogin: adminUsername
    administratorLoginPassword: adminPassword
    version: '12.0'
  }
}
`;
  }

  if (enableAKS) {
    template += `
resource aks 'Microsoft.ContainerService/managedClusters@2021-05-01' = {
  name: '${environment}-aks-${region}'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    dnsPrefix: '${environment}aks${region}'
    agentPoolProfiles: [
      {
        name: 'default'
        count: ${aksNodeCount}
        vmSize: vmSize
        osType: 'Linux'
      }
    ]
  }
}
`;
  }

  template += `
output resourceGroupName string = resourceGroupName
output vnetId string = vnet.id
`;

  return template;
}
app.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║         DevOps Master Suite API Server                     ║
║         Running on http://localhost:${PORT}                   ║
║         Database: ${DB_FILE}                ║
╚════════════════════════════════════════════════════════════╝
  `);
});

module.exports = app;