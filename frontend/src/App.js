import React, { useState, useEffect } from 'react';
import { Cloud, Server, Database, Network, Boxes, Terminal, Settings, PlayCircle, StopCircle, List, Plus, FileCode, GitBranch, Layers, Edit, Save, X, Upload, Download, Trash2, Copy, Eye, Clock, TrendingUp, Activity, Shield, Bell, RefreshCw, AlertCircle, Check, Package, Code } from 'lucide-react';

const DevOpsMasterSuite = () => {
  const API_URL = 'http://localhost:5000/api';

  // State Management
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [editingItem, setEditingItem] = useState(null);

  // Data States
  const [scripts, setScripts] = useState([]);
  const [resources, setResources] = useState([]);
  const [executionLog, setExecutionLog] = useState([]);
  const [config, setConfig] = useState({});
  const [stats, setStats] = useState({});
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showExecutionPanel, setShowExecutionPanel] = useState(false);
  const [iacTemplates, setIacTemplates] = useState([]);
  const [showIacModal, setShowIacModal] = useState(false);

  // Form States
  const [uploadData, setUploadData] = useState({ name: '', category: 'Deployment', content: '' });
  const [resourceData, setResourceData] = useState({ name: '', type: '', status: 'running', cost: 0, region: 'East US' });
  const [configData, setConfigData] = useState({ key: '', value: '' });
  const [iacData, setIacData] = useState({ 
    name: '', 
    type: 'terraform', 
    resourceType: 'virtual_machine',
    environment: 'dev',
    region: 'eastus'
  });

  // Advanced IaC Config
  const [advancedMode, setAdvancedMode] = useState(false);
  const [advancedConfig, setAdvancedConfig] = useState({
    vmCount: 1,
    vmSize: 'Standard_D2s_v3',
    osType: 'Windows',
    adminUsername: 'azureadmin',
    diskType: 'Premium_LRS',
    diskSize: 128,
    vnetAddressSpace: '10.0.0.0/16',
    subnetAddressSpace: '10.0.1.0/24',
    enableStaticIP: false,
    staticIPAddress: '10.0.1.10',
    enablePublicIP: true,
    enableInternalLB: false,
    enableExternalLB: false,
    lbType: 'Standard',
    enableFirewall: true,
    allowedPorts: '3389,5985,5986',
    enableAKS: false,
    aksNodeCount: 3,
    aksVMSize: 'Standard_D2s_v3',
    aksVersion: '1.27.0',
    enableSQL: false,
    sqlVersion: '2019',
    sqlEdition: 'Standard',
    sqlAdminUsername: 'sqladmin',
    storageType: 'Standard_LRS',
    enableSOFS: false,
    enableDSC: false,
    enablePostConfig: false,
    postConfigScript: '',
    enableUmbrellaPolicy: false,
    enableSecretStore: false,
    tags: 'Environment=Production,CostCenter=IT',
  });

  const categories = [
    { id: 'iac', name: 'Infrastructure as Code', icon: FileCode, color: 'blue' },
    { id: 'compute', name: 'Compute Resources', icon: Server, color: 'green' },
    { id: 'network', name: 'Networking', icon: Network, color: 'purple' },
    { id: 'database', name: 'Database Clusters', icon: Database, color: 'red' },
    { id: 'cicd', name: 'CI/CD Pipelines', icon: GitBranch, color: 'orange' },
    { id: 'webapp', name: 'Web App Clusters', icon: Layers, color: 'cyan' },
    { id: 'scripts', name: 'PowerShell Scripts', icon: Terminal, color: 'yellow' },
    { id: 'admin', name: 'Admin Panel', icon: Settings, color: 'gray' }
  ];

  // ==================== API CALLS ====================

  useEffect(() => {
    loadScripts();
    loadResources();
    loadStats();
    loadConfig();
    loadLogs();
    loadIacTemplates();
  }, []);

  const loadScripts = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/scripts`);
      if (!response.ok) throw new Error('Failed to load scripts');
      const data = await response.json();
      setScripts(data);
    } catch (err) {
      setError(err.message);
      console.error('Error loading scripts:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadResources = async () => {
    try {
      const response = await fetch(`${API_URL}/resources`);
      if (!response.ok) throw new Error('Failed to load resources');
      const data = await response.json();
      setResources(data);
    } catch (err) {
      console.error('Error loading resources:', err);
    }
  };

  const loadLogs = async () => {
    try {
      const response = await fetch(`${API_URL}/logs?limit=20`);
      if (!response.ok) throw new Error('Failed to load logs');
      const data = await response.json();
      setExecutionLog(data);
    } catch (err) {
      console.error('Error loading logs:', err);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch(`${API_URL}/stats`);
      if (!response.ok) throw new Error('Failed to load stats');
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  };

  const loadConfig = async () => {
    try {
      const response = await fetch(`${API_URL}/config`);
      if (!response.ok) throw new Error('Failed to load config');
      const data = await response.json();
      setConfig(data);
    } catch (err) {
      console.error('Error loading config:', err);
    }
  };

  const loadIacTemplates = async () => {
    try {
      const response = await fetch(`${API_URL}/iac/templates`);
      if (!response.ok) throw new Error('Failed to load IaC templates');
      const data = await response.json();
      setIacTemplates(data);
    } catch (err) {
      console.error('Error loading IaC templates:', err);
    }
  };

  const executeScript = async (scriptName) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scriptName, params: {} })
      });
      if (!response.ok) throw new Error('Execution failed');
      const result = await response.json();
      
      setExecutionLog(prev => [{
        id: Date.now(),
        scriptName,
        status: result.status,
        output: result.output,
        timestamp: new Date().toLocaleString()
      }, ...prev]);
      
      setShowExecutionPanel(true);
      loadScripts();
      loadStats();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadScript = async (e) => {
    e.preventDefault();
    if (!uploadData.name || !uploadData.content) {
      setError('Script name and content required');
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/scripts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(uploadData)
      });
      if (!response.ok) throw new Error('Upload failed');
      
      setUploadData({ name: '', category: 'Deployment', content: '' });
      setShowUploadModal(false);
      loadScripts();
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateResource = async (e) => {
    e.preventDefault();
    if (!resourceData.name) {
      setError('Resource name required');
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/resources`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(resourceData)
      });
      if (!response.ok) throw new Error('Creation failed');
      
      setResourceData({ name: '', type: '', status: 'running', cost: 0, region: 'East US' });
      loadResources();
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteScript = async (id) => {
    if (!window.confirm('Delete this script?')) return;
    try {
      const response = await fetch(`${API_URL}/scripts/${id}`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Deletion failed');
      loadScripts();
    } catch (err) {
      setError(err.message);
    }
  };

  const deleteResource = async (id) => {
    if (!window.confirm('Delete this resource?')) return;
    try {
      const response = await fetch(`${API_URL}/resources/${id}`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Deletion failed');
      loadResources();
    } catch (err) {
      setError(err.message);
    }
  };

  const generateIaCTemplate = async (e) => {
    e.preventDefault();
    if (!iacData.name) {
      setError('Template name required');
      return;
    }

    try {
      setLoading(true);
      const payload = { ...iacData };
      if (advancedMode) {
        payload.config = advancedConfig;
      }
      
      const response = await fetch(`${API_URL}/iac/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!response.ok) throw new Error('Generation failed');
      
      setIacData({ name: '', type: 'terraform', resourceType: 'virtual_machine', environment: 'dev', region: 'eastus' });
      setShowIacModal(false);
      loadIacTemplates();
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadIaCTemplate = async (templateId) => {
    try {
      const response = await fetch(`${API_URL}/iac/download/${templateId}`);
      if (!response.ok) throw new Error('Download failed');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `template-${templateId}`;
      a.click();
    } catch (err) {
      setError(err.message);
    }
  };

  const deleteIaCTemplate = async (id) => {
    if (!window.confirm('Delete this template?')) return;
    try {
      const response = await fetch(`${API_URL}/iac/templates/${id}`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Deletion failed');
      loadIacTemplates();
    } catch (err) {
      setError(err.message);
    }
  };

  // ==================== RENDER FUNCTIONS ====================

  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <div className="text-blue-600 text-sm font-medium">Total Scripts</div>
          <div className="text-3xl font-bold text-blue-900 mt-2">{scripts.length}</div>
          <div className="text-xs text-blue-600 mt-1">Available for execution</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <div className="text-green-600 text-sm font-medium">Total Resources</div>
          <div className="text-3xl font-bold text-green-900 mt-2">{resources.length}</div>
          <div className="text-xs text-green-600 mt-1">Across all regions</div>
        </div>
        <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
          <div className="text-orange-600 text-sm font-medium">Total Cost</div>
          <div className="text-3xl font-bold text-orange-900 mt-2">${(resources.reduce((s, r) => s + (r.cost || 0), 0) / 1000).toFixed(1)}K</div>
          <div className="text-xs text-orange-600 mt-1">Monthly estimated</div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
          <div className="text-purple-600 text-sm font-medium">Executions</div>
          <div className="text-3xl font-bold text-purple-900 mt-2">{executionLog.length}</div>
          <div className="text-xs text-purple-600 mt-1">In log history</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <List className="w-5 h-5" />
            Recent Resources
          </h3>
          {resources.length > 0 ? (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {resources.slice(0, 5).map((resource) => (
                <div key={resource.id} className="flex items-center justify-between p-3 bg-gray-50 rounded border border-gray-200 hover:bg-gray-100">
                  <div className="flex items-center gap-3">
                    <Server className="w-4 h-4 text-gray-500" />
                    <div>
                      <div className="font-medium text-sm">{resource.name}</div>
                      <div className="text-xs text-gray-500">{resource.type}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      resource.status === 'running' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                    }`}>
                      {resource.status}
                    </span>
                    <span className="text-sm text-gray-600">${resource.cost || 0}/mo</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No resources yet</p>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Terminal className="w-5 h-5" />
            Quick Actions
          </h3>
          <div className="space-y-2">
            <button 
              onClick={() => setShowUploadModal(true)}
              className="w-full p-3 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium flex items-center justify-center gap-2">
              <Plus className="w-4 h-4" />
              Upload Script
            </button>
            <button 
              onClick={() => setSelectedCategory('scripts')}
              className="w-full p-3 bg-green-600 text-white rounded hover:bg-green-700 text-sm font-medium flex items-center justify-center gap-2">
              <PlayCircle className="w-4 h-4" />
              View Scripts
            </button>
            <button 
              onClick={() => { setSelectedCategory(null); loadStats(); }}
              className="w-full p-3 bg-purple-600 text-white rounded hover:bg-purple-700 text-sm font-medium flex items-center justify-center gap-2">
              <RefreshCw className="w-4 h-4" />
              Refresh Stats
            </button>
            <button 
              onClick={() => setShowExecutionPanel(true)}
              className="w-full p-3 bg-orange-600 text-white rounded hover:bg-orange-700 text-sm font-medium flex items-center justify-center gap-2">
              <Eye className="w-4 h-4" />
              View Logs
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderScripts = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">PowerShell Script Library</h2>
        <button 
          onClick={() => setShowUploadModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Upload Script
        </button>
      </div>

      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading scripts...</div>
      ) : scripts.length > 0 ? (
        <div className="grid grid-cols-1 gap-3">
          {scripts.map((script) => (
            <div key={script.id} className="bg-white p-4 rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1">
                  <Terminal className="w-5 h-5 text-blue-600 mt-1" />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold">{script.name}</h3>
                      <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs font-medium">
                        {script.category}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{script.description}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span>Executions: {script.execCount}</span>
                      <span>Last run: {script.lastRun || 'Never'}</span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button 
                    onClick={() => executeScript(script.name)}
                    disabled={loading}
                    className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm font-medium disabled:bg-gray-400">
                    {loading ? 'Executing...' : 'Execute'}
                  </button>
                  <button 
                    onClick={() => deleteScript(script.id)}
                    className="px-3 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500">
          <Terminal className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>No scripts yet. Upload one to get started!</p>
        </div>
      )}
    </div>
  );

  const renderResources = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Resource Inventory</h2>
        <button 
          onClick={() => setEditingItem('newResource')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Add Resource
        </button>
      </div>

      {editingItem === 'newResource' && (
        <form onSubmit={handleCreateResource} className="bg-blue-50 p-4 rounded-lg border border-blue-200 space-y-3">
          <input 
            type="text" 
            placeholder="Resource name" 
            value={resourceData.name}
            onChange={(e) => setResourceData({...resourceData, name: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded"
          />
          <input 
            type="text" 
            placeholder="Type" 
            value={resourceData.type}
            onChange={(e) => setResourceData({...resourceData, type: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded"
          />
          <input 
            type="number" 
            placeholder="Monthly cost" 
            value={resourceData.cost}
            onChange={(e) => setResourceData({...resourceData, cost: parseFloat(e.target.value)})}
            className="w-full px-3 py-2 border border-gray-300 rounded"
          />
          <div className="flex gap-2">
            <button type="submit" className="flex-1 px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700">
              Create
            </button>
            <button 
              type="button"
              onClick={() => setEditingItem(null)}
              className="flex-1 px-3 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400">
              Cancel
            </button>
          </div>
        </form>
      )}

      {resources.length > 0 ? (
        <div className="grid grid-cols-1 gap-3">
          {resources.map((resource) => (
            <div key={resource.id} className="bg-white p-4 rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Server className="w-5 h-5 text-gray-500" />
                  <div>
                    <div className="font-semibold">{resource.name}</div>
                    <div className="text-sm text-gray-500">{resource.type} • {resource.region}</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    resource.status === 'running' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                  }`}>
                    {resource.status}
                  </span>
                  <span className="text-sm font-semibold">${resource.cost || 0}/mo</span>
                  <button 
                    onClick={() => deleteResource(resource.id)}
                    className="px-3 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500">
          <Package className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>No resources yet. Add one to get started!</p>
        </div>
      )}
    </div>
  );

  const renderIaC = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Infrastructure as Code</h2>
        <div className="flex gap-2">
          <button 
            onClick={() => setAdvancedMode(!advancedMode)}
            className={`px-4 py-2 rounded font-medium ${advancedMode ? 'bg-purple-600 text-white' : 'bg-gray-200 text-gray-700'}`}>
            {advancedMode ? '✓ Advanced Mode' : 'Basic Mode'}
          </button>
          <button 
            onClick={() => setShowIacModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Generate Template
          </button>
        </div>
      </div>

      {iacTemplates.length > 0 ? (
        <div className="grid grid-cols-1 gap-3">
          {iacTemplates.map((template) => (
            <div key={template.id} className="bg-white p-4 rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1">
                  <FileCode className="w-5 h-5 text-blue-600 mt-1" />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold">{template.name}</h3>
                      <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs font-medium">
                        {template.type}
                      </span>
                      <span className="px-2 py-0.5 bg-blue-100 text-blue-600 rounded text-xs font-medium">
                        {template.resourceType}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">Environment: {template.environment} • Region: {template.region}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span>Created: {new Date(template.createdAt).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button 
                    onClick={() => downloadIaCTemplate(template.id)}
                    className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm font-medium flex items-center gap-1">
                    <Download className="w-4 h-4" />
                    Download
                  </button>
                  <button 
                    onClick={() => deleteIaCTemplate(template.id)}
                    className="px-3 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500">
          <FileCode className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>No IaC templates yet. Generate one to get started!</p>
        </div>
      )}

      {showIacModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
          <div className="bg-white rounded-lg w-full max-w-4xl shadow-2xl my-8">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white z-10">
              <h3 className="text-xl font-bold">Generate IaC Template {advancedMode && '(Advanced)'}</h3>
              <button onClick={() => setShowIacModal(false)} className="text-gray-500 hover:text-gray-700">
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <form onSubmit={generateIaCTemplate} className="p-6 space-y-6 max-h-96 overflow-y-auto">
              <div className="space-y-4 pb-6 border-b border-gray-200">
                <h4 className="font-semibold text-gray-800">Basic Settings</h4>
                
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Template Name</label>
                    <input 
                      type="text"
                      placeholder="e.g., prod-web-tier"
                      value={iacData.name}
                      onChange={(e) => setIacData({...iacData, name: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">IaC Type</label>
                    <select 
                      value={iacData.type}
                      onChange={(e) => setIacData({...iacData, type: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded">
                      <option value="terraform">Terraform</option>
                      <option value="arm">ARM Template</option>
                      <option value="bicep">Bicep</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Resource Type</label>
                    <select 
                      value={iacData.resourceType}
                      onChange={(e) => setIacData({...iacData, resourceType: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded">
                      <option value="virtual_machine">Virtual Machine</option>
                      <option value="app_service">App Service</option>
                      <option value="sql_database">SQL Database</option>
                      <option value="storage_account">Storage Account</option>
                      <option value="virtual_network">Virtual Network</option>
                      <option value="aks_cluster">AKS Cluster</option>
                      <option value="enterprise_setup">Enterprise Setup</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Environment</label>
                    <select 
                      value={iacData.environment}
                      onChange={(e) => setIacData({...iacData, environment: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded">
                      <option value="dev">Development</option>
                      <option value="test">Testing</option>
                      <option value="staging">Staging</option>
                      <option value="prod">Production</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Region</label>
                    <select 
                      value={iacData.region}
                      onChange={(e) => setIacData({...iacData, region: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded">
                      <option value="eastus">East US</option>
                      <option value="westus">West US</option>
                      <option value="westus2">West US 2</option>
                      <option value="centralus">Central US</option>
                      <option value="northeurope">North Europe</option>
                      <option value="westeurope">West Europe</option>
                      <option value="uksouth">UK South</option>
                    </select>
                  </div>
                </div>
              </div>

              {advancedMode && (
                <>
                  <div className="space-y-4 pb-6 border-b border-gray-200">
                    <h4 className="font-semibold text-gray-800">VM & Compute</h4>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Number of VMs</label>
                        <input 
                          type="number"
                          min="1"
                          max="10"
                          value={advancedConfig.vmCount}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, vmCount: parseInt(e.target.value)})}
                          className="w-full px-3 py-2 border border-gray-300 rounded"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">VM Size</label>
                        <select 
                          value={advancedConfig.vmSize}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, vmSize: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded text-sm">
                          <option value="Standard_B1s">Standard_B1s</option>
                          <option value="Standard_B2s">Standard_B2s</option>
                          <option value="Standard_D2s_v3">Standard_D2s_v3</option>
                          <option value="Standard_D4s_v3">Standard_D4s_v3</option>
                          <option value="Standard_D8s_v3">Standard_D8s_v3</option>
                        </select>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Disk Type</label>
                        <select 
                          value={advancedConfig.diskType}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, diskType: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded text-sm">
                          <option value="Premium_LRS">Premium SSD</option>
                          <option value="Standard_LRS">Standard SSD</option>
                          <option value="StandardSSD_LRS">Standard SSD v2</option>
                          <option value="UltraSSD_LRS">Ultra SSD</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Disk Size (GB)</label>
                        <input 
                          type="number"
                          min="32"
                          max="4095"
                          value={advancedConfig.diskSize}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, diskSize: parseInt(e.target.value)})}
                          className="w-full px-3 py-2 border border-gray-300 rounded"
                        />
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4 pb-6 border-b border-gray-200">
                    <h4 className="font-semibold text-gray-800">Network</h4>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">VNet Address Space</label>
                        <input 
                          type="text"
                          placeholder="10.0.0.0/16"
                          value={advancedConfig.vnetAddressSpace}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, vnetAddressSpace: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Subnet Address Space</label>
                        <input 
                          type="text"
                          placeholder="10.0.1.0/24"
                          value={advancedConfig.subnetAddressSpace}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, subnetAddressSpace: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                        />
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <label className="flex items-center gap-2">
                        <input 
                          type="checkbox"
                          checked={advancedConfig.enableStaticIP}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, enableStaticIP: e.target.checked})}
                          className="w-4 h-4"
                        />
                        <span className="text-sm font-medium text-gray-700">Static IP</span>
                      </label>
                      <label className="flex items-center gap-2">
                        <input 
                          type="checkbox"
                          checked={advancedConfig.enablePublicIP}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, enablePublicIP: e.target.checked})}
                          className="w-4 h-4"
                        />
                        <span className="text-sm font-medium text-gray-700">Public IP</span>
                      </label>
                    </div>
                  </div>

                  <div className="space-y-4 pb-6 border-b border-gray-200">
                    <h4 className="font-semibold text-gray-800">Load Balancers & Firewall</h4>
                    
                    <div className="flex gap-4">
                      <label className="flex items-center gap-2">
                        <input 
                          type="checkbox"
                          checked={advancedConfig.enableInternalLB}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, enableInternalLB: e.target.checked})}
                          className="w-4 h-4"
                        />
                        <span className="text-sm font-medium text-gray-700">Internal LB</span>
                      </label>

                      <label className="flex items-center gap-2">
                        <input 
                          type="checkbox"
                          checked={advancedConfig.enableExternalLB}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, enableExternalLB: e.target.checked})}
                          className="w-4 h-4"
                        />
                        <span className="text-sm font-medium text-gray-700">External LB</span>
                      </label>

                      <label className="flex items-center gap-2">
                        <input 
                          type="checkbox"
                          checked={advancedConfig.enableFirewall}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, enableFirewall: e.target.checked})}
                          className="w-4 h-4"
                        />
                        <span className="text-sm font-medium text-gray-700">NSG</span>
                      </label>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Allowed Ports</label>
                      <input 
                        type="text"
                        placeholder="3389,5985,5986,443,80"
                        value={advancedConfig.allowedPorts}
                        onChange={(e) => setAdvancedConfig({...advancedConfig, allowedPorts: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                      />
                    </div>
                  </div>

                  <div className="space-y-4 pb-6 border-b border-gray-200">
                    <label className="flex items-center gap-2">
                      <input 
                        type="checkbox"
                        checked={advancedConfig.enableAKS}
                        onChange={(e) => setAdvancedConfig({...advancedConfig, enableAKS: e.target.checked})}
                        className="w-4 h-4"
                      />
                      <span className="text-sm font-semibold text-gray-700">AKS Cluster</span>
                    </label>

                    {advancedConfig.enableAKS && (
                      <div className="grid grid-cols-3 gap-4 pl-6">
                        <input 
                          type="number"
                          min="1"
                          placeholder="Nodes"
                          value={advancedConfig.aksNodeCount}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, aksNodeCount: parseInt(e.target.value)})}
                          className="px-3 py-2 border border-gray-300 rounded text-sm"
                        />
                        <select 
                          value={advancedConfig.aksVMSize}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, aksVMSize: e.target.value})}
                          className="px-3 py-2 border border-gray-300 rounded text-sm">
                          <option value="Standard_D2s_v3">D2s_v3</option>
                          <option value="Standard_D4s_v3">D4s_v3</option>
                        </select>
                        <select 
                          value={advancedConfig.aksVersion}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, aksVersion: e.target.value})}
                          className="px-3 py-2 border border-gray-300 rounded text-sm">
                          <option value="1.27.0">1.27.0</option>
                          <option value="1.26.0">1.26.0</option>
                        </select>
                      </div>
                    )}
                  </div>

                  <div className="space-y-4 pb-6 border-b border-gray-200">
                    <label className="flex items-center gap-2">
                      <input 
                        type="checkbox"
                        checked={advancedConfig.enableSQL}
                        onChange={(e) => setAdvancedConfig({...advancedConfig, enableSQL: e.target.checked})}
                        className="w-4 h-4"
                      />
                      <span className="text-sm font-semibold text-gray-700">SQL Server</span>
                    </label>

                    {advancedConfig.enableSQL && (
                      <div className="grid grid-cols-3 gap-4 pl-6">
                        <select 
                          value={advancedConfig.sqlVersion}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, sqlVersion: e.target.value})}
                          className="px-3 py-2 border border-gray-300 rounded text-sm">
                          <option value="2019">SQL 2019</option>
                          <option value="2022">SQL 2022</option>
                        </select>
                        <select 
                          value={advancedConfig.sqlEdition}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, sqlEdition: e.target.value})}
                          className="px-3 py-2 border border-gray-300 rounded text-sm">
                          <option value="Standard">Standard</option>
                          <option value="Enterprise">Enterprise</option>
                        </select>
                        <input 
                          type="text"
                          placeholder="SQL Admin"
                          value={advancedConfig.sqlAdminUsername}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, sqlAdminUsername: e.target.value})}
                          className="px-3 py-2 border border-gray-300 rounded text-sm"
                        />
                      </div>
                    )}
                  </div>

                  <div className="space-y-4 pb-6">
                    <h4 className="font-semibold text-gray-800">Security</h4>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <label className="flex items-center gap-2">
                        <input 
                          type="checkbox"
                          checked={advancedConfig.enableDSC}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, enableDSC: e.target.checked})}
                          className="w-4 h-4"
                        />
                        <span className="text-sm text-gray-700">DSC</span>
                      </label>

                      <label className="flex items-center gap-2">
                        <input 
                          type="checkbox"
                          checked={advancedConfig.enableSecretStore}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, enableSecretStore: e.target.checked})}
                          className="w-4 h-4"
                        />
                        <span className="text-sm text-gray-700">Key Vault</span>
                      </label>

                      <label className="flex items-center gap-2">
                        <input 
                          type="checkbox"
                          checked={advancedConfig.enablePostConfig}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, enablePostConfig: e.target.checked})}
                          className="w-4 h-4"
                        />
                        <span className="text-sm text-gray-700">Post-Deploy</span>
                      </label>

                      <label className="flex items-center gap-2">
                        <input 
                          type="checkbox"
                          checked={advancedConfig.enableUmbrellaPolicy}
                          onChange={(e) => setAdvancedConfig({...advancedConfig, enableUmbrellaPolicy: e.target.checked})}
                          className="w-4 h-4"
                        />
                        <span className="text-sm text-gray-700">Policies</span>
                      </label>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
                      <input 
                        type="text"
                        value={advancedConfig.tags}
                        onChange={(e) => setAdvancedConfig({...advancedConfig, tags: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                      />
                    </div>
                  </div>
                </>
              )}

              <div className="flex gap-2 pt-4 sticky bottom-0 bg-white border-t">
                <button 
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 font-medium">
                  {loading ? 'Generating...' : 'Generate Template'}
                </button>
                <button 
                  type="button"
                  onClick={() => setShowIacModal(false)}
                  className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 font-medium">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );

  const renderAdmin = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Admin Control Panel</h2>
      
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h3 className="text-lg font-semibold mb-4">Configuration</h3>
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Azure Subscription ID</label>
            <input 
              type="text" 
              placeholder="Enter Subscription ID" 
              value={config.AZURE_SUBSCRIPTION_ID || ''}
              className="w-full px-3 py-2 border border-gray-300 rounded"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Default Region</label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded">
              <option>eastus</option>
              <option>westus</option>
              <option>centralus</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Naming Convention Pattern</label>
            <input 
              type="text" 
              value={config.NAMING_PATTERN || '[env]-[type]-[location]-[instance]'}
              className="w-full px-3 py-2 border border-gray-300 rounded"
            />
          </div>
          <button className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 font-medium">
            Save Configuration
          </button>
        </div>
      </div>
    </div>
  );

  const renderUploadModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-2xl shadow-2xl">
        <div className="p-6 border-b border-gray-200 flex items-center justify-between">
          <h3 className="text-xl font-bold">Upload PowerShell Script</h3>
          <button onClick={() => setShowUploadModal(false)} className="text-gray-500 hover:text-gray-700">
            <X className="w-6 h-6" />
          </button>
        </div>
        
        <form onSubmit={handleUploadScript} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Script Name</label>
            <input 
              type="text"
              placeholder="e.g., Deploy-Environment.ps1"
              value={uploadData.name}
              onChange={(e) => setUploadData({...uploadData, name: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <select 
              value={uploadData.category}
              onChange={(e) => setUploadData({...uploadData, category: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded">
              <option>Deployment</option>
              <option>Management</option>
              <option>Database</option>
              <option>WebApp</option>
              <option>Reporting</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Script Content</label>
            <textarea 
              placeholder="Paste PowerShell script..."
              rows="10"
              value={uploadData.content}
              onChange={(e) => setUploadData({...uploadData, content: e.target.value})}
              className="w-full px-3 py-2 font-mono text-sm border border-gray-300 rounded"
            />
          </div>

          {error && <div className="text-red-600 text-sm">{error}</div>}

          <div className="flex gap-2 pt-4">
            <button 
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400">
              {loading ? 'Uploading...' : 'Upload Script'}
            </button>
            <button 
              type="button"
              onClick={() => setShowUploadModal(false)}
              className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  const renderExecutionPanel = () => (
    <div className="fixed bottom-0 right-0 w-1/2 h-96 bg-gray-900 text-white shadow-2xl rounded-tl-lg flex flex-col z-40">
      <div className="p-3 bg-gray-800 flex items-center justify-between">
        <h4 className="font-semibold flex items-center gap-2">
          <Terminal className="w-4 h-4" />
          Execution Log ({executionLog.length})
        </h4>
        <button 
          onClick={() => setShowExecutionPanel(false)}
          className="text-gray-400 hover:text-white">
          <X className="w-4 h-4" />
        </button>
      </div>
      <div className="flex-1 p-4 overflow-y-auto font-mono text-sm space-y-4">
        {executionLog.length > 0 ? (
          executionLog.map(log => (
            <div key={log.id} className="border-b border-gray-700 pb-3">
              <div className={`text-xs mb-1 ${log.status === 'success' ? 'text-green-400' : 'text-red-400'}`}>
                {log.timestamp} - {log.scriptName} [{log.status}]
              </div>
              <div className="text-gray-300 text-xs whitespace-pre-wrap max-h-20 overflow-y-auto">
                {log.output?.substring(0, 200)}...
              </div>
            </div>
          ))
        ) : (
          <div className="text-gray-500 text-center py-8">No executions yet</div>
        )}
      </div>
    </div>
  );

  const renderContent = () => {
    if (activeTab === 'dashboard') return renderDashboard();
    if (selectedCategory === 'scripts') return renderScripts();
    if (selectedCategory === 'compute') return renderResources();
    if (selectedCategory === 'iac') return renderIaC();
    if (selectedCategory === 'admin') return renderAdmin();
    
    return (
      <div className="text-center py-20">
        <Boxes className="w-16 h-16 mx-auto text-gray-400 mb-4" />
        <h3 className="text-xl font-semibold text-gray-600">Module Coming Soon</h3>
        <p className="text-gray-500">This module is under development</p>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white p-6 shadow-lg">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Cloud className="w-8 h-8" />
            DevOps Master Suite
          </h1>
          <p className="text-blue-100 mt-1">Unified Platform for Azure Infrastructure, Deployment & Management</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        <div className="flex gap-6">
          <div className="w-64 space-y-2">
            <button
              onClick={() => { setActiveTab('dashboard'); setSelectedCategory(null); }}
              className={`w-full text-left px-4 py-3 rounded-lg font-medium transition-colors ${
                activeTab === 'dashboard' && !selectedCategory
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              Dashboard
            </button>
            
            <div className="pt-4 pb-2 px-4 text-xs font-semibold text-gray-500 uppercase">
              Modules
            </div>
            
            {categories.map((cat) => {
              const Icon = cat.icon;
              return (
                <button
                  key={cat.id}
                  onClick={() => { setActiveTab('module'); setSelectedCategory(cat.id); }}
                  className={`w-full text-left px-4 py-3 rounded-lg font-medium transition-colors flex items-center gap-3 ${
                    selectedCategory === cat.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="text-sm">{cat.name}</span>
                </button>
              );
            })}
          </div>

          <div className="flex-1">
            {renderContent()}
          </div>
        </div>
      </div>

      {showUploadModal && renderUploadModal()}
      {showExecutionPanel && renderExecutionPanel()}
    </div>
  );
};

export default DevOpsMasterSuite;