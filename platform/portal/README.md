# MasterChief Web Portal

React-based web interface for the MasterChief DevOps Platform.

## Features

- **Plugin Management**: Upload, view, and remove plugins
- **Deployment Dashboard**: Start, monitor, and stop deployments
- **Real-time Updates**: Auto-refresh deployment status
- **Responsive Design**: Works on desktop and mobile devices

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- MasterChief backend API running on http://localhost:5000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Development

The development server runs on http://localhost:3000 and proxies API requests to http://localhost:5000.

### API Integration

The portal integrates with the following API endpoints:

**Plugins:**
- `GET /api/plugins/` - List plugins
- `POST /api/plugins/upload` - Upload plugin
- `DELETE /api/plugins/:id` - Remove plugin

**Deployments:**
- `GET /api/deployments/` - List deployments
- `POST /api/deployments/start` - Start deployment
- `POST /api/deployments/:id/stop` - Stop deployment
- `GET /api/deployments/:id/logs` - Get deployment logs

## Technology Stack

- React 18
- React Router 6
- Axios for API calls
- Vite for build tooling
