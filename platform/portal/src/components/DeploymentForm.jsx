import React, { useState } from 'react'

function DeploymentForm({ onClose, onSubmit }) {
  const [name, setName] = useState('')
  const [target, setTarget] = useState('dev')
  const [config, setConfig] = useState('')
  const [error, setError] = useState(null)

  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (!name.trim()) {
      setError('Deployment name is required')
      return
    }

    let parsedConfig = {}
    if (config.trim()) {
      try {
        parsedConfig = JSON.parse(config)
      } catch (err) {
        setError('Invalid JSON in configuration')
        return
      }
    }

    onSubmit(name, target, parsedConfig)
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Start New Deployment</h3>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="deploymentName">Deployment Name *</label>
            <input
              type="text"
              id="deploymentName"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Production Deploy v1.2.3"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="deploymentTarget">Target Environment *</label>
            <select
              id="deploymentTarget"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              required
            >
              <option value="dev">Development</option>
              <option value="staging">Staging</option>
              <option value="prod">Production</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="deploymentConfig">Configuration (JSON, optional)</label>
            <textarea
              id="deploymentConfig"
              value={config}
              onChange={(e) => setConfig(e.target.value)}
              placeholder='{"key": "value"}'
              rows="5"
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
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
            >
              Start Deployment
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default DeploymentForm
