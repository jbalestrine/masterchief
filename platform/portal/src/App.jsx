import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import PluginManagement from './pages/PluginManagement'
import DeploymentDashboard from './pages/DeploymentDashboard'
import './styles/App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="navbar-brand">
            <h1>MasterChief DevOps Platform</h1>
          </div>
          <div className="navbar-menu">
            <Link to="/" className="navbar-item">Plugins</Link>
            <Link to="/deployments" className="navbar-item">Deployments</Link>
          </div>
        </nav>
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<PluginManagement />} />
            <Route path="/deployments" element={<DeploymentDashboard />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
