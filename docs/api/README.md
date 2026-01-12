# MasterChief Platform API Reference

## Base URL

```
https://your-server:8443/api
```

## Authentication

Currently, the API does not require authentication. In production, implement JWT or OAuth2.

## Endpoints

### Platform Health

#### GET /health

Get platform health status.

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "api": "up",
    "database": "up",
    "monitoring": "up"
  }
}
```

---

## Service Management

### GET /api/services

List all system services.

**Response:**
```json
[
  {
    "name": "docker",
    "status": "running",
    "enabled": true,
    "description": "Docker Application Container Engine"
  }
]
```

### GET /api/services/{service}

Get specific service status.

### POST /api/services/{service}/start

Start a service.

### POST /api/services/{service}/stop

Stop a service.

### POST /api/services/{service}/restart

Restart a service.

### GET /api/services/{service}/logs

Get service logs.

**Query Parameters:**
- `lines` (int): Number of log lines to return (default: 100)

---

## Bare Metal Management

### GET /api/bare-metal/hardware

Get hardware information.

**Response:**
```json
{
  "cpu": {
    "model": "Intel Xeon",
    "cores": 4
  },
  "memory": {
    "total_bytes": 17179869184,
    "available_bytes": 8589934592
  },
  "disks": [...],
  "network": [...],
  "system": {...}
}
```

### GET /api/bare-metal/storage/disks

List all disks and partitions.

### GET /api/bare-metal/network/interfaces

List network interfaces.

---

## Process Management

### GET /api/processes

List all processes with resource usage.

**Response:**
```json
[
  {
    "pid": 1234,
    "name": "python3",
    "user": "root",
    "cpu_percent": 2.5,
    "memory_percent": 1.2,
    "status": "running"
  }
]
```

### GET /api/processes/{pid}

Get detailed process information.

### POST /api/processes/{pid}/kill

Kill a process.

**Request Body:**
```json
{
  "signal": "TERM"
}
```

---

## Package Management

### GET /api/packages/search?q={query}

Search for packages.

**Query Parameters:**
- `q` (string): Search query
- `manager` (string): Package manager (apt, pip, npm, all)

### GET /api/packages/installed

List installed packages.

**Query Parameters:**
- `manager` (string): Package manager filter

### POST /api/packages/install

Install a package.

**Request Body:**
```json
{
  "package": "nginx",
  "manager": "apt"
}
```

### POST /api/packages/remove

Remove a package.

### POST /api/packages/update

Update all packages.

---

## User Management

### GET /api/users

List all users.

### GET /api/users/{username}

Get user details.

---

## CMDB & Asset Inventory

### GET /api/cmdb/assets

List all assets.

### GET /api/cmdb/assets/{asset_id}

Get asset details.

### POST /api/cmdb/discover

Trigger asset discovery.

---

## Backup & Recovery

### GET /api/backup/backups

List all backups.

### POST /api/backup/backups

Create a new backup.

**Request Body:**
```json
{
  "type": "full"
}
```

### POST /api/backup/backups/{backup_id}/restore

Restore from backup.

---

## Monitoring & Health

### GET /api/monitoring/health

Get system health.

**Response:**
```json
{
  "status": "healthy",
  "cpu": {
    "percent": 45.2,
    "cores": 4
  },
  "memory": {
    "total": 17179869184,
    "available": 8589934592,
    "percent": 50.0
  },
  "disk": {
    "total": 107374182400,
    "used": 42949672960,
    "percent": 40.0
  }
}
```

### GET /api/monitoring/metrics

Get detailed metrics.

### GET /api/monitoring/alerts

Get active alerts.

---

## Error Responses

All endpoints may return the following error responses:

### 404 Not Found
```json
{
  "error": "Not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. In production, implement rate limiting to prevent abuse.

## Pagination

For endpoints that return lists, implement pagination:

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 50, max: 100)

---

## WebSocket Support

Future versions will support WebSocket connections for real-time updates:

```
wss://your-server:8443/ws
```

Topics:
- `services` - Service status updates
- `processes` - Process monitoring
- `monitoring` - System metrics
- `alerts` - Alert notifications
