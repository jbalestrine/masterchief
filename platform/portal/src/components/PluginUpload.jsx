import React, { useState } from 'react'
import { pluginAPI } from '../services/api'

function PluginUpload({ onClose, onSuccess }) {
  const [file, setFile] = useState(null)
  const [pluginName, setPluginName] = useState('')
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      if (selectedFile.name.endsWith('.zip')) {
        setFile(selectedFile)
        setError(null)
      } else {
        setError('Please select a .zip file')
        setFile(null)
      }
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!file) {
      setError('Please select a file')
      return
    }

    setUploading(true)
    setError(null)

    try {
      const response = await pluginAPI.upload(file, pluginName || null)
      if (response.success) {
        onSuccess()
      } else {
        setError(response.error || 'Failed to upload plugin')
      }
    } catch (err) {
      setError(err.message || 'Failed to upload plugin')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Upload Plugin</h3>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="pluginFile">Plugin File (.zip)</label>
            <input
              type="file"
              id="pluginFile"
              accept=".zip"
              onChange={handleFileChange}
              disabled={uploading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="pluginName">Plugin Name (optional)</label>
            <input
              type="text"
              id="pluginName"
              value={pluginName}
              onChange={(e) => setPluginName(e.target.value)}
              placeholder="Leave empty to use name from manifest"
              disabled={uploading}
            />
          </div>

          {error && (
            <div className="alert alert-error">
              {error}
            </div>
          )}

          <div className="modal-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
              disabled={uploading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={uploading || !file}
            >
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default PluginUpload
