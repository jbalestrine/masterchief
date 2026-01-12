import React from 'react'

function PluginCard({ plugin, onRemove }) {
  return (
    <div className="plugin-card">
      <div className="plugin-header">
        <h3>{plugin.name}</h3>
        <span className="plugin-type">{plugin.type}</span>
      </div>
      <div className="plugin-body">
        <p className="plugin-description">{plugin.description || 'No description available'}</p>
        <div className="plugin-meta">
          <span className="plugin-version">v{plugin.version}</span>
          {plugin.author && <span className="plugin-author">by {plugin.author}</span>}
        </div>
      </div>
      <div className="plugin-actions">
        <button 
          className="btn btn-danger btn-sm"
          onClick={() => onRemove(plugin.id)}
        >
          Remove
        </button>
      </div>
    </div>
  )
}

export default PluginCard
