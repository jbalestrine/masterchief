import React, { useState, useEffect } from 'react';
import { Cloud, Server, Database, Network, Boxes, Terminal, Settings, PlayCircle, StopCircle, List, Plus, FileCode, GitBranch, Layers, Edit, Save, X, Upload, Download, Trash2, Copy, Eye, Clock, TrendingUp, Activity, Shield, Bell, RefreshCw, AlertCircle, Check, Package, Code, Folder, FolderOpen, File, Zap, Globe, MessageSquare, Bot, Radio, Book, Archive, ExternalLink, Monitor } from 'lucide-react';

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
  const [iacTemplates, setIacTemplates] = useState([]);
  const [customModules, setCustomModules] = useState([]);
  const [fileSystem, setFileSystem] = useState({});
  const [services, setServices] = useState([]);
  const [deployments, setDeployments] = useState([]);
  
  // Modal States
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showExecutionPanel, setShowExecutionPanel] = useState(false);
  const [showIacModal, setShowIacModal] = useState(false);
  const [showModuleBuilder, setShowModuleBuilder] = useState(false);
  const [showFileManager, setShowFileManager] = useState(false);
  const [showServiceManager, setShowServiceManager] = useState(false);
  const [showWebPreview, setShowWebPreview] = useState(false);
  const [showIRCChat, setShowIRCChat] = useState(false);
  const [showDeployment, setShowDeployment] = useState(false);

  // Form States
  const [uploadData, setUploadData] = useState({ name: '', category: 'Deployment', content: '' });
  const [resourceData, setResourceData] = useState({ name: '', type: '', status: 'running', cost: 0, region: 'East US' });
  const [iacData, setIacData] = useState({ 
    name: '', 
    type: 'terraform', 
    resourceType: 'virtual_machine',
    environment: 'dev',
    region: 'eastus'
  });
  
  // Module Builder States
  const [moduleData, setModuleData] = useState({
    name: '',
    type: 'webapp',
    description: '',
    features: [],
    scripts: [],
    ports: [3000],
    config: {}
  });

  // File Manager States
  const [currentPath, setCurrentPath] = useState('/');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [fileContent, setFileContent] = useState('');
  const [editingFile, setEditingFile] = useState(null);

  // Service States
  const [serviceConfig, setServiceConfig] = useState({
    type: 'nodejs',
    name: '',
    port: 3000,
    directory: '',
    autoStart: true,
    config: ''
  });

  // Deployment States
  const [deployConfig, setDeployConfig] = useState({
    target: 'local',
    type: 'webapp',
    server: 'iis',
    installDependencies: true,
    autoConfig: true,
    sourceDir: '',
    targetPath: ''
  });

  // IRC Chat States
  const [ircMessages, setIrcMessages] = useState([]);
  const [ircCommand, setIrcCommand] = useState('');
  const [botTraining, setBotTraining] = useState([]);

  // Advanced IaC Config
  const [advancedMode, setAdvancedMode] = useState(false);
  const [advancedConfig, setAdvancedConfig] = useState({
    vmCount: 1,
    vmSize: 'Standard_D2s_v3',
    enableSOFS: false,
    enableSQL: false,
    enableAKS: false,
    enablePublicIP: true
  });

  const categories = [
    { id: 'iac', name: 'Infrastructure as Code', icon: FileCode, color: 'blue' },
    { id: 'modules', name: 'Custom Modules', icon: Boxes, color: 'indigo' },
    { id: 'files', name: 'File Manager', icon: Folder, color: 'yellow' },
    { id: 'compute', name: 'Compute Resources', icon: Server, color: 'green' },
    { id: 'services', name: 'Service Manager', icon: Zap, color: 'red' },
    { id: 'webapp', name: 'Web Applications', icon: Globe, color: 'cyan' },
    { id: 'irc', name: 'IRC & Chat Services', icon: MessageSquare, color: 'purple' },
    { id: 'media', name: 'Media Servers', icon: Radio, color: 'pink' },
    { id: 'scripts', name: 'PowerShell Scripts', icon: Terminal, color: 'orange' },
    { id: 'admin', name: 'Admin Panel', icon: Settings, color: 'gray' }
  ];

  const moduleTypes = [
    { id: 'webapp', name: 'Web Application', icon: Globe },
    { id: 'api', name: 'REST API', icon: Code },
    { id: 'sofs', name: 'Scale-Out File Server', icon: Database },
    { id: 'irc', name: 'IRC Chat Server', icon: MessageSquare },
    { id: 'shoutcast', name: 'Shoutcast Server', icon: Radio },
    { id: 'docusaurus', name: 'Docusaurus Docs', icon: Book },
    { id: 'nodejs', name: 'Node.js App', icon: Server },
    { id: 'custom', name: 'Custom Service', icon: Boxes }
  ];

  const serviceTypes = {
    nodejs: { name: 'Node.js Server', defaultPort: 3000 },
    iis: { name: 'IIS Web Server', defaultPort: 80 },
    apache: { name: 'Apache Server', defaultPort: 80 },
    xampp: { name: 'XAMPP Stack', defaultPort: 80 },
    inspircd: { name: 'InspIRCd', defaultPort: 6667 },
    shoutcast: { name: 'Shoutcast', defaultPort: 8000 },
    docusaurus: { name: 'Docusaurus', defaultPort: 3001 }
  };

  // ==================== API CALLS ====================

  useEffect(() => {
    loadScripts();
    loadResources();
    loadStats();
    loadCustomModules();
    loadServices();
    loadDeployments();
  }, []);

  const loadScripts = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/scripts`);
      if (!response.ok) throw new Error('Failed to load scripts');
      const data = await response.json();
      setScripts(data);
    } catch (err) {
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

  const loadCustomModules = async () => {
    try {
      const response = await fetch(`${API_URL}/modules`);
      if (!response.ok) throw new Error('Failed to load modules');
      const data = await response.json();
      setCustomModules(data);
    } catch (err) {
      console.error('Error loading modules:', err);
    }
  };

  const loadServices = async () => {
    try {
      const response = await fetch(`${API_URL}/services`);
      if (!response.ok) throw new Error('Failed to load services');
      const data = await response.json();
      setServices(data);
    } catch (err) {
      console.error('Error loading services:', err);
    }
  };

  const loadDeployments = async () => {
    try {
      const response = await fetch(`${API_URL}/deployments`);
      if (!response.ok) throw new Error('Failed to load deployments');
      const data = await response.json();
      setDeployments(data);
    } catch (err) {
      console.error('Error loading deployments:', err);
    }
  };

  const loadFileSystem = async (path = '/') => {
    try {
      const response = await fetch(`${API_URL}/files?path=${encodeURIComponent(path)}`);
      if (!response.ok) throw new Error('Failed to load files');
      const data = await response.json();
      setFileSystem(data);
    } catch (err) {
      console.error('Error loading files:', err);
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
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createModule = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/modules`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(moduleData)
      });
      if (!response.ok) throw new Error('Module creation failed');
      
      const result = await response.json();
      setShowModuleBuilder(false);
      setModuleData({ name: '', type: 'webapp', description: '', features: [], scripts: [], ports: [3000], config: {} });
      loadCustomModules();
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const uploadFiles = async (files) => {
    try {
      setLoading(true);
      const formData = new FormData();
      Array.from(files).forEach(file => {
        formData.append('files', file);
      });
      formData.append('path', currentPath);

      const response = await fetch(`${API_URL}/files/upload`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) throw new Error('Upload failed');
      loadFileSystem(currentPath);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createZip = async (files, outputName) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/files/zip`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ files, outputName, path: currentPath })
      });
      
      if (!response.ok) throw new Error('Zip creation failed');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = outputName;
      a.click();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const saveFile = async (path, content) => {
    try {
      const response = await fetch(`${API_URL}/files/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path, content })
      });
      
      if (!response.ok) throw new Error('Save failed');
      loadFileSystem(currentPath);
      setEditingFile(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const createService = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/services`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(serviceConfig)
      });
      
      if (!response.ok) throw new Error('Service creation failed');
      setShowServiceManager(false);
      setServiceConfig({ type: 'nodejs', name: '', port: 3000, directory: '', autoStart: true, config: '' });
      loadServices();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const controlService = async (serviceId, action) => {
    try {
      const response = await fetch(`${API_URL}/services/${serviceId}/${action}`, {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error(`Service ${action} failed`);
      loadServices();
    } catch (err) {
      setError(err.message);
    }
  };

  const deployApplication = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/deploy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(deployConfig)
      });
      
      if (!response.ok) throw new Error('Deployment failed');
      const result = await response.json();
      setShowDeployment(false);
      loadDeployments();
      
      setExecutionLog(prev => [{
        id: Date.now(),
        scriptName: 'Deployment',
        status: 'success',
        output: result.message,
        timestamp: new Date().toLocaleString()
      }, ...prev]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const sendIRCCommand = async (command) => {
    try {
      const response = await fetch(`${API_URL}/irc/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command })
      });
      
      if (!response.ok) throw new Error('Command failed');
      const result = await response.json();
      
      setIrcMessages(prev => [...prev, {
        type: 'command',
        text: command,
        response: result.output,
        timestamp: new Date().toLocaleString()
      }]);
      
      setIrcCommand('');
    } catch (err) {
      setError(err.message);
    }
  };

  // ==================== RENDER FUNCTIONS ====================

  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-5 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <div className="text-blue-600 text-sm font-medium">Scripts</div>
          <div className="text-3xl font-bold text-blue-900 mt-2">{scripts.length}</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <div className="text-green-600 text-sm font-medium">Resources</div>
          <div className="text-3xl font-bold text-green-900 mt-2">{resources.length}</div>
        </div>
        <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-200">
          <div className="text-indigo-600 text-sm font-medium">Modules</div>
          <div className="text-3xl font-bold text-indigo-900 mt-2">{customModules.length}</div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
          <div className="text-purple-600 text-sm font-medium">Services</div>
          <div className="text-3xl font-bold text-purple-900 mt-2">{services.filter(s => s.status === 'running').length}/{services.length}</div>
        </div>
        <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
          <div className="text-orange-600 text-sm font-medium">Deployments</div>
          <div className="text-3xl font-bold text-orange-900 mt-2">{deployments.length}</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Running Services
          </h3>
          <div className="space-y-2">
            {services.filter(s => s.status === 'running').map(service => (
              <div key={service.id} className="flex items-center justify-between p-3 bg-green-50 rounded">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <div>
                    <div className="font-medium text-sm">{service.name}</div>
                    <div className="text-xs text-gray-500">{service.type} • Port {service.port}</div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button 
                    onClick={() => controlService(service.id, 'restart')}
                    className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200">
                    Restart
                  </button>
                  <button 
                    onClick={() => controlService(service.id, 'stop')}
                    className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200">
                    Stop
                  </button>
                </div>
              </div>
            ))}
            {services.filter(s => s.status === 'running').length === 0 && (
              <p className="text-gray-500 text-center py-4">No services running</p>
            )}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5" />
            Quick Actions
          </h3>
          <div className="grid grid-cols-2 gap-2">
            <button 
              onClick={() => setShowModuleBuilder(true)}
              className="p-3 bg-indigo-600 text-white rounded hover:bg-indigo-700 text-sm font-medium flex items-center justify-center gap-2">
              <Plus className="w-4 h-4" />
              New Module
            </button>
            <button 
              onClick={() => setShowServiceManager(true)}
              className="p-3 bg-purple-600 text-white rounded hover:bg-purple-700 text-sm font-medium flex items-center justify-center gap-2">
              <Zap className="w-4 h-4" />
              Add Service
            </button>
            <button 
              onClick={() => { setSelectedCategory('files'); loadFileSystem(); }}
              className="p-3 bg-yellow-600 text-white rounded hover:bg-yellow-700 text-sm font-medium flex items-center justify-center gap-2">
              <Folder className="w-4 h-4" />
              Files
            </button>
            <button 
              onClick={() => setShowDeployment(true)}
              className="p-3 bg-green-600 text-white rounded hover:bg-green-700 text-sm font-medium flex items-center justify-center gap-2">
              <Upload className="w-4 h-4" />
              Deploy
            </button>
            <button 
              onClick={() => setShowIRCChat(true)}
              className="p-3 bg-purple-600 text-white rounded hover:bg-purple-700 text-sm font-medium flex items-center justify-center gap-2">
              <MessageSquare className="w-4 h-4" />
              IRC Chat
            </button>
            <button 
              onClick={() => setShowExecutionPanel(true)}
              className="p-3 bg-orange-600 text-white rounded hover:bg-orange-700 text-sm font-medium flex items-center justify-center gap-2">
              <Terminal className="w-4 h-4" />
              Logs
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderModuleBuilder = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Module Builder</h2>
        <button 
          onClick={() => setShowModuleBuilder(true)}
          className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Create Module
        </button>
      </div>

      {customModules.length > 0 ? (
        <div className="grid grid-cols-1 gap-4">
          {customModules.map(module => (
            <div key={module.id} className="bg-white p-4 rounded-lg border border-gray-200 hover:shadow-md">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1">
                  <Boxes className="w-6 h-6 text-indigo-600 mt-1" />
                  <div>
                    <h3 className="font-semibold text-lg">{module.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">{module.description}</p>
                    <div className="flex items-center gap-3 mt-2">
                      <span className="px-2 py-1 bg-indigo-100 text-indigo-700 rounded text-xs font-medium">
                        {module.type}
                      </span>
                      <span className="text-xs text-gray-500">
                        {module.scripts?.length || 0} scripts
                      </span>
                      <span className="text-xs text-gray-500">
                        Ports: {module.ports?.join(', ') || 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button className="px-3 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200">
                    <Eye className="w-4 h-4" />
                  </button>
                  <button className="px-3 py-2 bg-green-100 text-green-700 rounded hover:bg-green-200">
                    <PlayCircle className="w-4 h-4" />
                  </button>
                  <button className="px-3 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <Boxes className="w-16 h-16 mx-auto text-gray-400 mb-4" />
          <p className="text-gray-600 mb-4">No custom modules yet</p>
          <button 
            onClick={() => setShowModuleBuilder(true)}
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700">
            Create Your First Module
          </button>
        </div>
      )}
    </div>
  );

  const renderFileManager = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-bold">File Manager</h2>
          <span className="text-sm text-gray-500">{currentPath}</span>
        </div>
        <div className="flex gap-2">
          <input
            type="file"
            multiple
            onChange={(e) => uploadFiles(e.target.files)}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 cursor-pointer flex items-center gap-2">
            <Upload className="w-4 h-4" />
            Upload
          </label>
          <button 
            onClick={() => selectedFiles.length > 0 && createZip(selectedFiles, 'archive.zip')}
            disabled={selectedFiles.length === 0}
            className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:bg-gray-400 flex items-center gap-2">
            <Archive className="w-4 h-4" />
            Zip Selected
          </button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="col-span-1 bg-white p-4 rounded-lg border border-gray-200">
          <h3 className="font-semibold mb-3">Directory Tree</h3>
          <div className="space-y-1">
            <div 
              onClick={() => setCurrentPath('/')}
              className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded cursor-pointer">
              <FolderOpen className="w-4 h-4" />
              <span className="text-sm">Root</span>
            </div>
            <div 
              onClick={() => setCurrentPath('/modules')}
              className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded cursor-pointer ml-4">
              <Folder className="w-4 h-4" />
              <span className="text-sm">modules</span>
            </div>
            <div 
              onClick={() => setCurrentPath('/deployments')}
              className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded cursor-pointer ml-4">
              <Folder className="w-4 h-4" />
              <span className="text-sm">deployments</span>
            </div>
            <div 
              onClick={() => setCurrentPath('/webapps')}
              className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded cursor-pointer ml-4">
              <Folder className="w-4 h-4" />
              <span className="text-sm">webapps</span>
            </div>
          </div>
        </div>

        <div className="col-span-3 bg-white p-4 rounded-lg border border-gray-200">
          <h3 className="font-semibold mb-3">Files</h3>
          <div className="grid grid-cols-3 gap-2">
            {/* Mock files for demonstration */}
            {['index.html', 'style.css', 'script.js', 'config.json', 'README.md'].map(file => (
              <div 
                key={file}
                onClick={() => {
                  const newSelected = selectedFiles.includes(file) 
                    ? selectedFiles.filter(f => f !== file)
                    : [...selectedFiles, file];
                  setSelectedFiles(newSelected);
                }}
                className={`flex items-center gap-2 p-3 rounded border-2 cursor-pointer transition-all ${
                  selectedFiles.includes(file) 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}>
                <File className="w-5 h-5 text-gray-500" />
                <div>
                  <div className="text-sm font-medium">{file}</div>
                  <div className="text-xs text-gray-500">2 KB</div>
                </div>
              </div>
            ))}
          </div>
          
          {editingFile && (
            <div className="mt-4 space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="font-semibold">Editing: {editingFile}</h4>
                <button 
                  onClick={() => saveFile(`${currentPath}/${editingFile}`, fileContent)}
                  className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-sm">
                  Save
                </button>
              </div>
              <textarea 
                value={fileContent}
                onChange={(e) => setFileContent(e.target.value)}
                className="w-full h-64 p-3 border border-gray-300 rounded font-mono text-sm"
                placeholder="File content..."
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderServices = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Service Manager</h2>
        <button 
          onClick={() => setShowServiceManager(true)}
          className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Add Service
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {services.map(service => (
          <div key={service.id} className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={`w-3 h-3 rounded-full ${service.status === 'running' ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
                <div>
                  <div className="font-semibold">{service.name}</div>
                  <div className="text-sm text-gray-500">{service.type} • Port {service.port} • {service.directory}</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-3 py-1 rounded text-sm font-medium ${
                  service.status === 'running' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                }`}>
                  {service.status}
                </span>
                {service.status === 'running' ? (
                  <>
                    <button 
                      onClick={() => controlService(service.id, 'restart')}
                      className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-sm">
                      Restart
                    </button>
                    <button 
                      onClick={() => controlService(service.id, 'stop')}
                      className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 text-sm">
                      Stop
                    </button>
                  </>
                ) : (
                  <button 
                    onClick={() => controlService(service.id, 'start')}
                    className="px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200 text-sm">
                    Start
                  </button>
                )}
                <button className="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200">
                  <Monitor className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderIRCChat = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-4xl h-3/4 flex flex-col shadow-2xl">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between bg-purple-600 text-white rounded-t-lg">
          <h3 className="text-lg font-bold flex items-center gap-2">
            <MessageSquare className="w-5 h-5" />
            IRC Chat & Bot Training
          </h3>
          <button onClick={() => setShowIRCChat(false)} className="hover:bg-purple-700 p-1 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="flex-1 flex">
          <div className="flex-1 flex flex-col">
            <div className="flex-1 p-4 overflow-y-auto bg-gray-900 text-green-400 font-mono text-sm">
              {ircMessages.map((msg, i) => (
                <div key={i} className="mb-2">
                  <span className="text-gray-500">[{msg.timestamp}]</span>
                  {msg.type === 'command' ? (
                    <>
                      <span className="text-yellow-400"> &gt; {msg.text}</span>
                      <div className="text-green-400 ml-4">{msg.response}</div>
                    </>
                  ) : (
                    <span className="text-blue-400"> {msg.text}</span>
                  )}
                </div>
              ))}
            </div>
            
            <div className="p-4 border-t border-gray-200 bg-gray-800">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={ircCommand}
                  onChange={(e) => setIrcCommand(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendIRCCommand(ircCommand)}
                  placeholder="Enter command or message..."
                  className="flex-1 px-3 py-2 bg-gray-900 text-green-400 border border-gray-700 rounded font-mono"
                />
                <button 
                  onClick={() => sendIRCCommand(ircCommand)}
                  className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700">
                  Send
                </button>
              </div>
            </div>
          </div>
          
          <div className="w-64 border-l border-gray-200 p-4 bg-gray-50">
            <h4 className="font-semibold mb-3">Bot Training</h4>
            <div className="space-y-2 text-sm">
              <button className="w-full p-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-left">
                !help - Show commands
              </button>
              <button className="w-full p-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-left">
                !status - Server status
              </button>
              <button className="w-full p-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-left">
                !deploy - Deploy app
              </button>
              <button className="w-full p-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-left">
                !services - List services
              </button>
            </div>
            
            <div className="mt-4">
              <h4 className="font-semibold mb-2 text-sm">Quick Actions</h4>
              <div className="space-y-1">
                <button className="w-full p-2 bg-green-600 text-white rounded hover:bg-green-700 text-xs">
                  Start Training
                </button>
                <button className="w-full p-2 bg-orange-600 text-white rounded hover:bg-orange-700 text-xs">
                  Export Data
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Module Builder Modal
  if (showModuleBuilder) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg w-full max-w-3xl shadow-2xl max-h-[90vh] overflow-y-auto">
          <div className="p-6 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white z-10">
            <h3 className="text-xl font-bold">Create Custom Module</h3>
            <button onClick={() => setShowModuleBuilder(false)} className="text-gray-500 hover:text-gray-700">
              <X className="w-6 h-6" />
            </button>
          </div>
          
          <form onSubmit={createModule} className="p-6 space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Module Name</label>
              <input 
                type="text"
                value={moduleData.name}
                onChange={(e) => setModuleData({...moduleData, name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded"
                placeholder="e.g., My Custom App"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Module Type</label>
              <div className="grid grid-cols-2 gap-3">
                {moduleTypes.map(type => {
                  const Icon = type.icon;
                  return (
                    <button
                      key={type.id}
                      type="button"
                      onClick={() => setModuleData({...moduleData, type: type.id})}
                      className={`p-3 rounded border-2 flex items-center gap-3 transition-all ${
                        moduleData.type === type.id
                          ? 'border-indigo-500 bg-indigo-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}>
                      <Icon className="w-5 h-5" />
                      <span className="text-sm font-medium">{type.name}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
              <textarea 
                value={moduleData.description}
                onChange={(e) => setModuleData({...moduleData, description: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded"
                rows="3"
                placeholder="Describe your module..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Ports (comma-separated)</label>
              <input 
                type="text"
                value={moduleData.ports.join(', ')}
                onChange={(e) => setModuleData({...moduleData, ports: e.target.value.split(',').map(p => parseInt(p.trim())).filter(p => !isNaN(p))})}
                className="w-full px-3 py-2 border border-gray-300 rounded"
                placeholder="3000, 3001, 8080"
              />
            </div>

            <div className="flex gap-2 pt-4">
              <button 
                type="submit"
                disabled={loading}
                className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:bg-gray-400 font-medium">
                {loading ? 'Creating...' : 'Create Module'}
              </button>
              <button 
                type="button"
                onClick={() => setShowModuleBuilder(false)}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 font-medium">
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  // Service Manager Modal
  if (showServiceManager) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg w-full max-w-2xl shadow-2xl">
          <div className="p-6 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-xl font-bold">Add New Service</h3>
            <button onClick={() => setShowServiceManager(false)} className="text-gray-500 hover:text-gray-700">
              <X className="w-6 h-6" />
            </button>
          </div>
          
          <form onSubmit={createService} className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Service Type</label>
              <select 
                value={serviceConfig.type}
                onChange={(e) => setServiceConfig({
                  ...serviceConfig, 
                  type: e.target.value,
                  port: serviceTypes[e.target.value].defaultPort
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded">
                {Object.entries(serviceTypes).map(([key, value]) => (
                  <option key={key} value={key}>{value.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Service Name</label>
              <input 
                type="text"
                value={serviceConfig.name}
                onChange={(e) => setServiceConfig({...serviceConfig, name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded"
                placeholder="e.g., my-nodejs-app"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Application Type</label>
                <select 
                  value={deployConfig.type}
                  onChange={(e) => setDeployConfig({...deployConfig, type: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded">
                  <option value="webapp">Web Application</option>
                  <option value="api">API Service</option>
                  <option value="static">Static Site</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Web Server</label>
              <select 
                value={deployConfig.server}
                onChange={(e) => setDeployConfig({...deployConfig, server: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded">
                <option value="iis">IIS (Install if needed)</option>
                <option value="apache">Apache (Install if needed)</option>
                <option value="xampp">XAMPP (Install if needed)</option>
                <option value="nodejs">Node.js Server</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Source Directory</label>
              <input 
                type="text"
                value={deployConfig.sourceDir}
                onChange={(e) => setDeployConfig({...deployConfig, sourceDir: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded"
                placeholder="/path/to/source"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Target Path</label>
              <input 
                type="text"
                value={deployConfig.targetPath}
                onChange={(e) => setDeployConfig({...deployConfig, targetPath: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded"
                placeholder="/var/www/html or C:\inetpub\wwwroot"
              />
            </div>

            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <input 
                  type="checkbox"
                  checked={deployConfig.installDependencies}
                  onChange={(e) => setDeployConfig({...deployConfig, installDependencies: e.target.checked})}
                  className="w-4 h-4"
                />
                <span className="text-sm font-medium text-gray-700">Install dependencies (npm install)</span>
              </label>
              <label className="flex items-center gap-2">
                <input 
                  type="checkbox"
                  checked={deployConfig.autoConfig}
                  onChange={(e) => setDeployConfig({...deployConfig, autoConfig: e.target.checked})}
                  className="w-4 h-4"
                />
                <span className="text-sm font-medium text-gray-700">Auto-configure web server</span>
              </label>
            </div>

            <div className="flex gap-2 pt-4">
              <button 
                type="submit"
                disabled={loading}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400 font-medium">
                {loading ? 'Deploying...' : 'Deploy Now'}
              </button>
              <button 
                type="button"
                onClick={() => setShowDeployment(false)}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 font-medium">
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  const renderContent = () => {
    if (activeTab === 'dashboard') return renderDashboard();
    if (selectedCategory === 'modules') return renderModuleBuilder();
    if (selectedCategory === 'files') return renderFileManager();
    if (selectedCategory === 'services') return renderServices();
    if (selectedCategory === 'scripts') return <div className="p-4">Scripts module - Coming from previous implementation</div>;
    if (selectedCategory === 'compute') return <div className="p-4">Compute module - Coming from previous implementation</div>;
    if (selectedCategory === 'iac') return <div className="p-4">IaC module - Coming from previous implementation</div>;
    
    return (
      <div className="text-center py-20">
        <Boxes className="w-16 h-16 mx-auto text-gray-400 mb-4" />
        <h3 className="text-xl font-semibold text-gray-600">Module Coming Soon</h3>
        <p className="text-gray-500">This module is under development</p>
      </div>
    );
  };

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

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 text-white p-6 shadow-lg">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Cloud className="w-8 h-8" />
            DevOps Master Suite
          </h1>
          <p className="text-blue-100 mt-1">Enterprise Modular Platform for Infrastructure, Deployment & Service Management</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        <div className="flex gap-6">
          <div className="w-64 space-y-2">
            <button
              onClick={() => { setActiveTab('dashboard'); setSelectedCategory(null); }}
              className={`w-full text-left px-4 py-3 rounded-lg font-medium transition-colors ${
                activeTab === 'dashboard' && !selectedCategory
                  ? 'bg-indigo-600 text-white'
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
                      ? 'bg-indigo-600 text-white'
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

      {showExecutionPanel && renderExecutionPanel()}
      {showIRCChat && renderIRCChat()}
      
      {error && (
        <div className="fixed bottom-4 right-4 bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2 z-50">
          <AlertCircle className="w-5 h-5" />
          <span>{error}</span>
          <button onClick={() => setError(null)} className="ml-2">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
};

export default DevOpsMasterSuite;Port</label>
                <input 
                  type="number"
                  value={serviceConfig.port}
                  onChange={(e) => setServiceConfig({...serviceConfig, port: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Directory</label>
                <input 
                  type="text"
                  value={serviceConfig.directory}
                  onChange={(e) => setServiceConfig({...serviceConfig, directory: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded"
                  placeholder="/path/to/service"
                />
              </div>
            </div>

            <div>
              <label className="flex items-center gap-2">
                <input 
                  type="checkbox"
                  checked={serviceConfig.autoStart}
                  onChange={(e) => setServiceConfig({...serviceConfig, autoStart: e.target.checked})}
                  className="w-4 h-4"
                />
                <span className="text-sm font-medium text-gray-700">Auto-start on system boot</span>
              </label>
            </div>

            <div className="flex gap-2 pt-4">
              <button 
                type="submit"
                disabled={loading}
                className="flex-1 px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:bg-gray-400 font-medium">
                {loading ? 'Creating...' : 'Create Service'}
              </button>
              <button 
                type="button"
                onClick={() => setShowServiceManager(false)}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 font-medium">
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  // Deployment Modal
  if (showDeployment) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg w-full max-w-2xl shadow-2xl">
          <div className="p-6 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-xl font-bold">Deploy Application</h3>
            <button onClick={() => setShowDeployment(false)} className="text-gray-500 hover:text-gray-700">
              <X className="w-6 h-6" />
            </button>
          </div>
          
          <form onSubmit={deployApplication} className="p-6 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Deployment Target</label>
                <select 
                  value={deployConfig.target}
                  onChange={(e) => setDeployConfig({...deployConfig, target: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded">
                  <option value="local">Local Machine</option>
                  <option value="network">Network Share</option>
                  <option value="azure">Azure VM</option>
                  <option value="frontend">Frontend Directory</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">