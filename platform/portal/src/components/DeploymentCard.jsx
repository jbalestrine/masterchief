import React, { useState } from 'react'
import { deploymentAPI } from '../services/api'

function DeploymentCard({ deployment, onStop, onRefresh }) {
  const [showLogs, setShowLogs] = useState(false)
  const [logs, setLogs] = useState([])
  const [loadingLogs, setLoadingLogs] = useState(false)

  const getStatusClass = (status) => {
    const statusMap = {
      pending: 'status-pending',
      running: 'status-running',
      success: 'status-success',
      failed: 'status-failed',
      stopped: 'status-stopped',
    }
    return statusMap[status] || ''
  }

  const loadLogs = async () => {
    if (showLogs) {
      setShowLogs(false)
      return
    }

    setLoadingLogs(true)
    try {
      const response = await deploymentAPI.getLogs(deployment.id)
      if (response.success) {
        setLogs(response.logs)
        setShowLogs(true)
      } else {
        alert(`Failed to load logs: ${response.error}`)
      }
    } catch (err) {
      alert(`Failed to load logs: ${err.message}`)
    } finally {
      setLoadingLogs(false)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className={`deployment-card ${getStatusClass(deployment.status)}`}>
      <div className="deployment-header">
        <div className="deployment-info">
          <h3>{deployment.name}</h3>
          <span className={`status-badge ${getStatusClass(deployment.status)}`}>
            {deployment.status}
          </span>
        </div>
        <div className="deployment-actions">
          <button
            className="btn btn-sm btn-secondary"
            onClick={loadLogs}
            disabled={loadingLogs}
          >
            {showLogs ? 'Hide Logs' : 'View Logs'}
          </button>
          {deployment.status === 'running' && (
            <button
              className="btn btn-sm btn-danger"
              onClick={() => onStop(deployment.id)}
            >
              Stop
            </button>
          )}
          <button
            className="btn btn-sm btn-secondary"
            onClick={onRefresh}
          >
            ↻
          </button>
        </div>
      </div>

      <div className="deployment-details">
        <div className="detail-row">
          <span className="detail-label">Target:</span>
          <span className="detail-value">{deployment.target}</span>
        </div>
        <div className="detail-row">
          <span className="detail-label">Created:</span>
          <span className="detail-value">{formatDate(deployment.created_at)}</span>
        </div>
        {deployment.started_at && (
          <div className="detail-row">
            <span className="detail-label">Started:</span>
            <span className="detail-value">{formatDate(deployment.started_at)}</span>
          </div>
        )}
        {deployment.completed_at && (
          <div className="detail-row">
            <span className="detail-label">Completed:</span>
            <span className="detail-value">{formatDate(deployment.completed_at)}</span>
          </div>
        )}
        {deployment.error && (
          <div className="detail-row">
            <span className="detail-label">Error:</span>
            <span className="detail-value error-text">{deployment.error}</span>
          </div>
        )}
      </div>

      {showLogs && (
        <div className="deployment-logs">
          <h4>Logs</h4>
          <div className="logs-content">
            {logs.length === 0 ? (
              <p>No logs available</p>
            ) : (
              logs.map((log, index) => (
                <div key={index} className="log-line">{log}</div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default DeploymentCard
