import React, { useState, useEffect } from 'react'
import { deploymentAPI } from '../services/api'
import DeploymentCard from '../components/DeploymentCard'
import DeploymentForm from '../components/DeploymentForm'
import '../styles/DeploymentDashboard.css'

function DeploymentDashboard() {
  const [deployments, setDeployments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [statusFilter, setStatusFilter] = useState(null)

  useEffect(() => {
    loadDeployments()
    // Auto-refresh every 5 seconds
    const interval = setInterval(loadDeployments, 5000)
    return () => clearInterval(interval)
  }, [statusFilter])

  const loadDeployments = async () => {
    try {
      setError(null)
      const response = await deploymentAPI.list(statusFilter)
      if (response.success) {
        setDeployments(response.deployments)
      } else {
        setError(response.error || 'Failed to load deployments')
      }
    } catch (err) {
      setError(err.message || 'Failed to load deployments')
    } finally {
      setLoading(false)
    }
  }

  const handleStartDeployment = async (name, target, config) => {
    try {
      const response = await deploymentAPI.start(name, target, config)
      if (response.success) {
        setShowForm(false)
        loadDeployments()
      } else {
        alert(`Failed to start deployment: ${response.error}`)
      }
    } catch (err) {
      alert(`Failed to start deployment: ${err.message}`)
    }
  }

  const handleStopDeployment = async (deploymentId) => {
    if (!window.confirm('Are you sure you want to stop this deployment?')) {
      return
    }

    try {
      const response = await deploymentAPI.stop(deploymentId)
      if (response.success) {
        loadDeployments()
      } else {
        alert(`Failed to stop deployment: ${response.error}`)
      }
    } catch (err) {
      alert(`Failed to stop deployment: ${err.message}`)
    }
  }

  const getStatusCounts = () => {
    const counts = {
      pending: 0,
      running: 0,
      success: 0,
      failed: 0,
      stopped: 0,
    }
    
    deployments.forEach(d => {
      if (counts[d.status] !== undefined) {
        counts[d.status]++
      }
    })
    
    return counts
  }

  const statusCounts = getStatusCounts()

  return (
    <div className="deployment-dashboard">
      <div className="page-header">
        <h2>Deployment Dashboard</h2>
        <button 
          className="btn btn-primary"
          onClick={() => setShowForm(true)}
        >
          Start New Deployment
        </button>
      </div>

      <div className="status-summary">
        <div className="status-card">
          <div className="status-count">{statusCounts.running}</div>
          <div className="status-label">Running</div>
        </div>
        <div className="status-card">
          <div className="status-count">{statusCounts.success}</div>
          <div className="status-label">Success</div>
        </div>
        <div className="status-card">
          <div className="status-count">{statusCounts.failed}</div>
          <div className="status-label">Failed</div>
        </div>
        <div className="status-card">
          <div className="status-count">{statusCounts.pending}</div>
          <div className="status-label">Pending</div>
        </div>
      </div>

      <div className="filter-bar">
        <label>Filter by status:</label>
        <select 
          value={statusFilter || ''} 
          onChange={(e) => setStatusFilter(e.target.value || null)}
        >
          <option value="">All</option>
          <option value="pending">Pending</option>
          <option value="running">Running</option>
          <option value="success">Success</option>
          <option value="failed">Failed</option>
          <option value="stopped">Stopped</option>
        </select>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      {loading ? (
        <div className="loading">Loading deployments...</div>
      ) : (
        <div className="deployment-list">
          {deployments.length === 0 ? (
            <div className="empty-state">
              <p>No deployments found.</p>
              <button 
                className="btn btn-primary"
                onClick={() => setShowForm(true)}
              >
                Start Your First Deployment
              </button>
            </div>
          ) : (
            deployments.map(deployment => (
              <DeploymentCard
                key={deployment.id}
                deployment={deployment}
                onStop={handleStopDeployment}
                onRefresh={loadDeployments}
              />
            ))
          )}
        </div>
      )}

      {showForm && (
        <DeploymentForm
          onClose={() => setShowForm(false)}
          onSubmit={handleStartDeployment}
        />
      )}
    </div>
  )
}

export default DeploymentDashboard
