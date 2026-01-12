import React, { useState, useEffect } from 'react'
import { pluginAPI } from '../services/api'
import PluginCard from '../components/PluginCard'
import PluginUpload from '../components/PluginUpload'
import '../styles/PluginManagement.css'

function PluginManagement() {
  const [plugins, setPlugins] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showUpload, setShowUpload] = useState(false)

  useEffect(() => {
    loadPlugins()
  }, [])

  const loadPlugins = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await pluginAPI.list()
      if (response.success) {
        setPlugins(response.plugins)
      } else {
        setError(response.error || 'Failed to load plugins')
      }
    } catch (err) {
      setError(err.message || 'Failed to load plugins')
    } finally {
      setLoading(false)
    }
  }

  const handleUploadSuccess = () => {
    setShowUpload(false)
    loadPlugins()
  }

  const handleRemove = async (pluginId) => {
    if (!window.confirm('Are you sure you want to remove this plugin?')) {
      return
    }

    try {
      const response = await pluginAPI.remove(pluginId)
      if (response.success) {
        loadPlugins()
      } else {
        alert(`Failed to remove plugin: ${response.error}`)
      }
    } catch (err) {
      alert(`Failed to remove plugin: ${err.message}`)
    }
  }

  return (
    <div className="plugin-management">
      <div className="page-header">
        <h2>Plugin Management</h2>
        <button 
          className="btn btn-primary"
          onClick={() => setShowUpload(true)}
        >
          Upload Plugin
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      {loading ? (
        <div className="loading">Loading plugins...</div>
      ) : (
        <div className="plugin-grid">
          {plugins.length === 0 ? (
            <div className="empty-state">
              <p>No plugins installed yet.</p>
              <button 
                className="btn btn-primary"
                onClick={() => setShowUpload(true)}
              >
                Upload Your First Plugin
              </button>
            </div>
          ) : (
            plugins.map(plugin => (
              <PluginCard
                key={plugin.id}
                plugin={plugin}
                onRemove={handleRemove}
              />
            ))
          )}
        </div>
      )}

      {showUpload && (
        <PluginUpload
          onClose={() => setShowUpload(false)}
          onSuccess={handleUploadSuccess}
        />
      )}
    </div>
  )
}

export default PluginManagement
