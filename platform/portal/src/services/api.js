import axios from 'axios'

const API_BASE_URL = '/api'

// Plugin Management API
export const pluginAPI = {
  list: async () => {
    const response = await axios.get(`${API_BASE_URL}/plugins/`)
    return response.data
  },
  
  get: async (pluginId) => {
    const response = await axios.get(`${API_BASE_URL}/plugins/${pluginId}`)
    return response.data
  },
  
  upload: async (file, name = null) => {
    const formData = new FormData()
    formData.append('file', file)
    if (name) {
      formData.append('name', name)
    }
    
    const response = await axios.post(`${API_BASE_URL}/plugins/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
  
  remove: async (pluginId) => {
    const response = await axios.delete(`${API_BASE_URL}/plugins/${pluginId}`)
    return response.data
  },
  
  update: async (pluginId, file) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await axios.post(`${API_BASE_URL}/plugins/${pluginId}/update`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
}

// Deployment Management API
export const deploymentAPI = {
  list: async (status = null, limit = null) => {
    const params = {}
    if (status) params.status = status
    if (limit) params.limit = limit
    
    const response = await axios.get(`${API_BASE_URL}/deployments/`, { params })
    return response.data
  },
  
  get: async (deploymentId) => {
    const response = await axios.get(`${API_BASE_URL}/deployments/${deploymentId}`)
    return response.data
  },
  
  start: async (name, target, config = {}) => {
    const response = await axios.post(`${API_BASE_URL}/deployments/start`, {
      name,
      target,
      config,
    })
    return response.data
  },
  
  stop: async (deploymentId) => {
    const response = await axios.post(`${API_BASE_URL}/deployments/${deploymentId}/stop`)
    return response.data
  },
  
  getLogs: async (deploymentId) => {
    const response = await axios.get(`${API_BASE_URL}/deployments/${deploymentId}/logs`)
    return response.data
  },
}
