const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.join(__dirname, 'devops.db');
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) console.error('Database error:', err);
  else console.log('Connected to database for seeding');
});

db.serialize(() => {
  // Insert initial resources
  const resources = [
    { name: 'prod-rg-eastus-001', type: 'Resource Group', status: 'running', region: 'East US', cost: 0 },
    { name: 'prod-vnet-hub-001', type: 'Virtual Network', status: 'running', region: 'East US', cost: 50 },
    { name: 'prod-sql-cluster-001', type: 'SQL Always On', status: 'running', region: 'East US', cost: 2500 },
    { name: 'prod-app-eastus-001', type: 'App Service', status: 'running', region: 'East US', cost: 300 },
    { name: 'prod-app-westus-001', type: 'App Service', status: 'running', region: 'West US', cost: 300 },
    { name: 'prod-storage-001', type: 'Storage Account', status: 'running', region: 'East US', cost: 150 }
  ];

  resources.forEach(resource => {
    db.run(
      `INSERT OR IGNORE INTO resources (name, type, status, region, cost) VALUES (?, ?, ?, ?, ?)`,
      [resource.name, resource.type, resource.status, resource.region, resource.cost],
      (err) => {
        if (err) console.error('Error inserting resource:', err);
        else console.log(`Inserted resource: ${resource.name}`);
      }
    );
  });

  // Insert default config
  const config = [
    { key: 'AZURE_SUBSCRIPTION_ID', value: 'your-subscription-id' },
    { key: 'DEFAULT_REGION', value: 'eastus' },
    { key: 'NAMING_PATTERN', value: '[env]-[type]-[location]-[instance]' },
    { key: 'ENVIRONMENT', value: 'production' }
  ];

  config.forEach(item => {
    db.run(
      `INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)`,
      [item.key, item.value],
      (err) => {
        if (err) console.error('Error inserting config:', err);
        else console.log(`Inserted config: ${item.key}`);
      }
    );
  });

  setTimeout(() => {
    console.log('Seeding complete!');
    db.close();
  }, 1000);
});