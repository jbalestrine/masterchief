# Quick Start Guide - DevOps Web GUI (Phase 1 & 2)

This guide helps you get started with the MasterChief Platform components implemented in Phases 1 and 2.

## Prerequisites

- Python 3.10 or higher
- Redis server (optional but recommended)
- PostgreSQL (for future phases)

## Installation

### 1. Install Dependencies

```bash
cd /path/to/masterchief
pip install -r requirements.txt
```

### 2. Start Redis (Optional)

```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or using local installation
redis-server
```

## Running the Platform

### Option 1: Run Full Application

```bash
# Start the Flask application with WebSocket support
python examples/platform_usage.py server
```

The server will start on `http://0.0.0.0:8080`

### Option 2: Run Examples

```bash
# Run example code demonstrating event bus and log collection
python examples/platform_usage.py
```

### Option 3: Use Application Factory

```python
from platform.app import create_app, run_app

app = create_app()
run_app(app, host='0.0.0.0', port=8080)
```

## Testing the API

### Health Check

```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "masterchief-api"
}
```

### Readiness Check

```bash
curl http://localhost:8080/health/ready
```

### Gateway Info

```bash
curl http://localhost:8080/api/v1/
```

### Query Logs

```bash
# Get recent logs
curl http://localhost:8080/api/v1/logs?limit=10

# Filter by level
curl http://localhost:8080/api/v1/logs?level=ERROR

# Search logs
curl http://localhost:8080/api/v1/logs/search?q=deployment

# Get log stats
curl http://localhost:8080/api/v1/logs/stats
```

## Using WebSocket

### JavaScript Client Example

```javascript
// Connect to WebSocket
const socket = io('http://localhost:8080');

// Handle connection
socket.on('connect', () => {
  console.log('Connected to WebSocket');
  
  // Subscribe to deployment channel
  socket.emit('subscribe', { channel: 'deployments' });
});

// Handle subscription confirmation
socket.on('subscribed', (data) => {
  console.log('Subscribed to:', data.channel);
});

// Handle deployment updates
socket.on('deployment_update', (data) => {
  console.log('Deployment update:', data);
});

// Handle log entries
socket.on('log_entry', (data) => {
  console.log('Log:', data.level, data.message);
});

// Ping/Pong
socket.emit('ping');
socket.on('pong', (data) => {
  console.log('Pong received');
});
```

### Python Client Example

```python
import socketio

# Create Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print('Connected to WebSocket')
    sio.emit('subscribe', {'channel': 'deployments'})

@sio.event
def subscribed(data):
    print(f"Subscribed to: {data['channel']}")

@sio.event
def deployment_update(data):
    print(f"Deployment update: {data}")

@sio.event
def log_entry(data):
    print(f"Log: [{data['level']}] {data['message']}")

# Connect
sio.connect('http://localhost:8080')
sio.wait()
```

## Using Event Bus

### Publishing Events

```python
import asyncio
from core.event_bus import get_event_bus
from platform.event_bus import EventPublisher, EventType

async def publish_deployment():
    event_bus = get_event_bus()
    publisher = EventPublisher(source="my-service", event_bus=event_bus)
    
    # Publish deployment started
    await publisher.publish_deployment_started(
        deployment_id="deploy-123",
        metadata={"environment": "production"}
    )
    
    # Publish deployment progress
    await publisher.publish_deployment_progress(
        deployment_id="deploy-123",
        progress=50,
        message="Deploying services"
    )
    
    # Publish deployment completed
    await publisher.publish_deployment_completed(
        deployment_id="deploy-123",
        result={"status": "success"}
    )

asyncio.run(publish_deployment())
```

### Subscribing to Events

```python
from core.event_bus import get_event_bus, Event
from platform.event_bus import EventType

# Get event bus
event_bus = get_event_bus()

# Define handler
def handle_deployment(event: Event):
    print(f"Deployment event: {event.type}")
    print(f"Data: {event.data}")

# Subscribe
event_bus.subscribe(EventType.DEPLOYMENT_STARTED.value, handle_deployment)
event_bus.subscribe(EventType.DEPLOYMENT_COMPLETED.value, handle_deployment)
```

## Using State Management

### Storing and Retrieving State

```python
import asyncio
from platform.state import get_state_store

async def manage_state():
    # Get state store (Redis-backed)
    store = get_state_store(redis_client)
    
    # Store deployment state
    await store.set("deployment:123", {
        "status": "running",
        "progress": 50,
        "environment": "production"
    })
    
    # Retrieve state
    state = await store.get("deployment:123")
    print(f"Deployment state: {state}")
    
    # Store with TTL (expires in 300 seconds)
    await store.set("temp:session", {"user": "admin"}, ttl=300)
    
    # Increment counter
    count = await store.increment("counter:deployments")
    print(f"Total deployments: {count}")

asyncio.run(manage_state())
```

### Using State Models

```python
from platform.state.models import DeploymentState, StateStatus

# Create deployment state
deployment = DeploymentState(
    id="deploy-123",
    environment="production",
    target="server-01",
    progress=50,
    message="Installing packages",
    status=StateStatus.ACTIVE
)

# Convert to dict
data = deployment.to_dict()

# Store in state store
await store.set(f"deployment:{deployment.id}", data)
```

## Log Streaming

### Collecting Logs

```python
import asyncio
from platform.logs import LogCollector

async def collect_logs():
    collector = LogCollector()
    
    # Add handler
    def print_log(log_entry):
        print(f"[{log_entry.level}] {log_entry.message}")
    
    collector.add_handler(print_log)
    
    # Start collecting
    await collector.start_collecting()
    
    # Create and collect log
    log = collector.create_log_entry(
        level="INFO",
        source="webapp",
        message="User logged in",
        metadata={"user_id": "123"}
    )
    await collector.collect_log(log)

asyncio.run(collect_logs())
```

## Configuration

### Environment Variables

```bash
# Redis
export REDIS_URL=redis://localhost:6379/0

# Database
export DATABASE_URL=postgresql://user:pass@localhost/masterchief

# API
export JWT_SECRET=your-secret-key-here

# Logging
export LOG_LEVEL=INFO
```

### Configuration File

Edit `config/default.py` to customize settings:

```python
# API Settings
API_RATE_LIMIT_REQUESTS = 100
API_RATE_LIMIT_WINDOW = 60

# WebSocket Settings
WEBSOCKET_CORS_ORIGINS = "*"

# Cache Settings
CACHE_DEFAULT_TTL = 300
```

## Docker Compose

Start the full stack:

```bash
docker-compose up
```

Services:
- MasterChief API: http://localhost:8443
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Troubleshooting

### Redis Connection Failed

If Redis is not available, the platform will run with reduced functionality. Install and start Redis:

```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis
```

### Import Errors

Ensure you're in the correct directory:

```bash
cd /path/to/masterchief
export PYTHONPATH=$PWD
```

### WebSocket Not Connecting

Check that eventlet is installed:

```bash
pip install eventlet
```

Verify the server is running with SocketIO support:

```bash
python examples/platform_usage.py server
```

## Next Steps

1. Explore the API endpoints
2. Connect a WebSocket client
3. Publish custom events
4. Build on top of the platform infrastructure
5. Wait for Phase 3+ implementations (Plugin Wizard, Dashboard, Web UI)

## Resources

- Full Implementation Summary: `PHASE_1_2_IMPLEMENTATION.md`
- API Gateway: `platform/gateway/`
- Event Bus: `platform/event_bus/`
- State Management: `platform/state/`
- Real-Time: `platform/realtime/`
- Log Streaming: `platform/logs/`
- Examples: `examples/platform_usage.py`
