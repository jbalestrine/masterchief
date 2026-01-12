# Data Ingestion Examples

This document provides examples of using the IRC bot's data ingestion system.

## Table of Contents

- [Webhooks](#webhooks)
- [REST API Polling](#rest-api-polling)
- [File Watching](#file-watching)
- [Database Queries](#database-queries)
- [Streaming Data](#streaming-data)
- [Log Tailing](#log-tailing)
- [Metrics Collection](#metrics-collection)

## Webhooks

### GitHub Webhook Integration

```python
from chatops.irc.bot_engine.bot import create_bot
from chatops.irc.bot_engine.ingestion.webhooks import WebhookIngestion

# Create bot
bot = create_bot("irc.example.com", 6667, "devbot", ["#dev"])

# Setup webhook receiver
webhook = WebhookIngestion("github_webhooks", {
    "port": 8080,
    "host": "0.0.0.0",
    "secret": "your_github_webhook_secret",
    "webhook_type": "github"
})

# Register with ingestion manager
bot.ingestion_manager.register_source(webhook)

# Add webhook handler
def handle_github_push(connection, event, args):
    data = event.data
    repo = data.get('repository', 'unknown')
    commits = len(data.get('commits', []))
    
    # Send to IRC channel
    for channel in bot.channels_to_join:
        connection.privmsg(channel, 
            f"[GitHub] {commits} new commits pushed to {repo}")

# Bind to webhook events
bot.bind("webhook", "-|-", "github/push", handle_github_push)

# Start webhook server
import asyncio
asyncio.create_task(webhook.start())

# Start bot
bot.start()
```

### Alertmanager Webhook

```python
def handle_alert(connection, event, args):
    data = event.data
    alerts = data.get('alerts', [])
    
    for alert in alerts:
        status = alert.get('status')
        labels = alert.get('labels', {})
        alertname = labels.get('alertname', 'Unknown')
        severity = labels.get('severity', 'info')
        
        message = f"[Alert:{severity}] {alertname} - Status: {status}"
        
        for channel in bot.channels_to_join:
            connection.privmsg(channel, message)

# Setup Alertmanager webhook
alertmanager_webhook = WebhookIngestion("alertmanager", {
    "port": 8081,
    "secret": "alertmanager_secret",
    "webhook_type": "alertmanager"
})

bot.ingestion_manager.register_source(alertmanager_webhook)
bot.bind("webhook", "-|-", "alertmanager/*", handle_alert)
```

## REST API Polling

### Polling a Status API

```python
from chatops.irc.bot_engine.ingestion.api import APIIngestion

# Setup API poller
api_poller = APIIngestion("service_status", {
    "url": "https://api.example.com/status",
    "method": "GET",
    "auth_type": "api_key",
    "auth_config": {
        "key": "X-API-Key",
        "value": "your_api_key"
    },
    "polling_interval": 300  # Poll every 5 minutes
})

bot.ingestion_manager.register_source(api_poller)

def handle_status_change(connection, event, args):
    data = event.data
    status = data.get('status', 'unknown')
    
    if status != 'healthy':
        for channel in bot.channels_to_join:
            connection.privmsg(channel, 
                f"⚠️ Service status changed: {status}")

bot.bind("api", "-|-", "service_status", handle_status_change)

import asyncio
asyncio.create_task(api_poller.start())
```

## File Watching

### Watch for Configuration Changes

```python
from chatops.irc.bot_engine.ingestion.files import FileIngestion

# Setup file watcher
file_watcher = FileIngestion("config_watcher", {
    "path": "/etc/myapp/config",
    "pattern": "*.yaml",
    "formats": ["yaml"],
    "recursive": True,
    "initial_scan": False
})

bot.ingestion_manager.register_source(file_watcher)

def handle_config_change(connection, event, args):
    filepath = event.metadata.get('filepath')
    event_type = event.metadata.get('event_type')
    
    message = f"[Config] {event_type}: {filepath}"
    
    for channel in bot.channels_to_join:
        connection.privmsg(channel, message)

bot.bind("file", "-|-", "*.yaml", handle_config_change)

import asyncio
asyncio.create_task(file_watcher.start())
```

### Process JSON Data Files

```python
file_processor = FileIngestion("data_processor", {
    "path": "/data/input",
    "pattern": "*.json",
    "formats": ["json"],
    "initial_scan": True
})

bot.ingestion_manager.register_source(file_processor)

def process_json_file(connection, event, args):
    data = event.data
    filename = event.metadata.get('filename')
    
    # Process data
    records = data.get('records', [])
    
    for channel in bot.channels_to_join:
        connection.privmsg(channel, 
            f"[Data] Processed {len(records)} records from {filename}")

bot.bind("file", "-|-", "/data/input/*.json", process_json_file)
```

## Database Queries

### Monitor PostgreSQL Database

```python
from chatops.irc.bot_engine.ingestion.database import DatabaseIngestion

# Setup database monitor
db_monitor = DatabaseIngestion("postgres_monitor", {
    "db_type": "postgresql",
    "connection_string": "postgresql://user:pass@localhost:5432/mydb",
    "query": "SELECT id, status FROM deployments WHERE status = 'failed' ORDER BY created_at DESC LIMIT 10",
    "polling_interval": 60,
    "change_detection": True,
    "key_field": "id"
})

bot.ingestion_manager.register_source(db_monitor)

def handle_failed_deployments(connection, event, args):
    rows = event.data.get('rows', [])
    
    if rows:
        message = f"[Database] {len(rows)} new failed deployment(s) detected"
        for channel in bot.channels_to_join:
            connection.privmsg(channel, message)

bot.bind("db", "-|-", "postgres_monitor", handle_failed_deployments)

import asyncio
asyncio.create_task(db_monitor.start())
```

### MongoDB Collection Monitor

```python
import json

mongodb_monitor = DatabaseIngestion("mongo_monitor", {
    "db_type": "mongodb",
    "connection_string": "mongodb://localhost:27017/",
    "query": json.dumps({
        "database": "myapp",
        "collection": "events",
        "query": {"severity": "critical"}
    }),
    "polling_interval": 30,
    "change_detection": True
})

bot.ingestion_manager.register_source(mongodb_monitor)

def handle_critical_events(connection, event, args):
    rows = event.data.get('rows', [])
    
    for row in rows:
        event_name = row.get('name', 'Unknown')
        for channel in bot.channels_to_join:
            connection.privmsg(channel, 
                f"🚨 Critical Event: {event_name}")

bot.bind("db", "-|-", "mongo_monitor", handle_critical_events)
```

## Streaming Data

### Kafka Consumer

```python
from chatops.irc.bot_engine.ingestion.streaming import StreamingIngestion

# Setup Kafka consumer
kafka_consumer = StreamingIngestion("deployment_events", {
    "stream_type": "kafka",
    "connection": {
        "brokers": ["localhost:9092"]
    },
    "topic": "deployments",
    "consumer_group": "irc-bot",
    "auto_commit": True
})

bot.ingestion_manager.register_source(kafka_consumer)

def handle_deployment(connection, event, args):
    data = event.data
    service = data.get('service', 'unknown')
    environment = data.get('environment', 'unknown')
    status = data.get('status', 'unknown')
    
    message = f"[Deploy] {service} to {environment}: {status}"
    
    for channel in bot.channels_to_join:
        connection.privmsg(channel, message)

bot.bind("stream", "-|-", "deployment_events", handle_deployment)

import asyncio
asyncio.create_task(kafka_consumer.start())
```

### Redis Pub/Sub

```python
redis_subscriber = StreamingIngestion("notifications", {
    "stream_type": "redis",
    "connection": {
        "host": "localhost",
        "port": 6379
    },
    "channel": "notifications"
})

bot.ingestion_manager.register_source(redis_subscriber)

def handle_notification(connection, event, args):
    data = event.data
    message = data.get('message', 'No message')
    
    for channel in bot.channels_to_join:
        connection.privmsg(channel, f"[Notify] {message}")

bot.bind("stream", "-|-", "notifications", handle_notification)
```

## Log Tailing

### Tail Application Logs

```python
from chatops.irc.bot_engine.ingestion.logs import LogIngestion

# Setup log tailer
log_tailer = LogIngestion("app_logs", {
    "path": "/var/log/myapp/app.log",
    "format": "json",
    "follow": True,
    "from_beginning": False
})

bot.ingestion_manager.register_source(log_tailer)

def handle_app_log(connection, event, args):
    data = event.data
    level = data.get('level', 'info')
    message = data.get('message', '')
    
    # Only alert on errors
    if level in ['error', 'critical']:
        for channel in bot.channels_to_join:
            connection.privmsg(channel, 
                f"[Log:{level}] {message}")

bot.bind("log", "-|-", "app_logs", handle_app_log)

import asyncio
asyncio.create_task(log_tailer.start())
```

### Syslog Monitoring

```python
syslog_monitor = LogIngestion("syslog", {
    "path": "/var/log/syslog",
    "format": "syslog",
    "follow": True
})

bot.ingestion_manager.register_source(syslog_monitor)

def handle_syslog(connection, event, args):
    data = event.data
    hostname = data.get('hostname', 'unknown')
    tag = data.get('tag', 'unknown')
    message = data.get('message', '')
    
    # Filter for specific tags
    if tag in ['sudo', 'sshd']:
        for channel in bot.channels_to_join:
            connection.privmsg(channel, 
                f"[Syslog] {hostname}:{tag} - {message}")

bot.bind("log", "-|-", "syslog", handle_syslog)
```

## Metrics Collection

### Prometheus Metrics with Alerting

```python
from chatops.irc.bot_engine.ingestion.metrics import MetricsIngestion

# Setup metrics collector
metrics_collector = MetricsIngestion("cpu_monitor", {
    "metric_type": "prometheus",
    "connection": {
        "host": "localhost",
        "port": 9090
    },
    "query": "avg(rate(node_cpu_seconds_total{mode='idle'}[5m])) * 100",
    "polling_interval": 30,
    "threshold": 80,
    "threshold_condition": "gt"
})

bot.ingestion_manager.register_source(metrics_collector)

def handle_high_cpu(connection, event, args):
    alerts = event.metadata.get('alerts', [])
    
    for alert in alerts:
        metric = alert.get('metric', {})
        value = metric.get('value', 0)
        
        message = f"⚠️ [Metrics] High CPU usage detected: {value:.2f}%"
        
        for channel in bot.channels_to_join:
            connection.privmsg(channel, message)

bot.bind("metric", "-|-", "cpu_monitor", handle_high_cpu)

import asyncio
asyncio.create_task(metrics_collector.start())
```

### InfluxDB Query

```python
influx_metrics = MetricsIngestion("influx_monitor", {
    "metric_type": "influxdb",
    "connection": {
        "url": "http://localhost:8086",
        "token": "your_token",
        "org": "myorg",
        "bucket": "metrics"
    },
    "query": '''
        from(bucket: "metrics")
        |> range(start: -5m)
        |> filter(fn: (r) => r._measurement == "http_requests")
        |> filter(fn: (r) => r._field == "count")
        |> sum()
    ''',
    "polling_interval": 60
})

bot.ingestion_manager.register_source(influx_metrics)

def handle_influx_metrics(connection, event, args):
    metrics = event.data.get('metrics', [])
    
    for metric in metrics:
        value = metric.get('value', 0)
        message = f"[Metrics] HTTP requests (5m): {value}"
        
        for channel in bot.channels_to_join:
            connection.privmsg(channel, message)

bot.bind("metric", "-|-", "influx_monitor", handle_influx_metrics)
```

## Complete Example

Here's a complete example that integrates multiple ingestion sources:

```python
#!/usr/bin/env python3
"""Complete IRC bot with data ingestion example."""

import asyncio
from chatops.irc.bot_engine.bot import create_bot
from chatops.irc.bot_engine.ingestion.webhooks import WebhookIngestion
from chatops.irc.bot_engine.ingestion.files import FileIngestion
from chatops.irc.bot_engine.ingestion.metrics import MetricsIngestion


def main():
    # Create bot
    bot = create_bot("irc.example.com", 6667, "devbot", ["#dev", "#ops"])
    
    # Setup webhooks
    github_webhook = WebhookIngestion("github", {
        "port": 8080,
        "secret": "github_secret",
        "webhook_type": "github"
    })
    bot.ingestion_manager.register_source(github_webhook)
    
    # Setup file watcher
    config_watcher = FileIngestion("configs", {
        "path": "/etc/myapp",
        "pattern": "*.yaml",
        "formats": ["yaml"]
    })
    bot.ingestion_manager.register_source(config_watcher)
    
    # Setup metrics
    cpu_monitor = MetricsIngestion("cpu", {
        "metric_type": "prometheus",
        "connection": {"host": "localhost", "port": 9090},
        "query": "cpu_usage",
        "threshold": 80,
        "threshold_condition": "gt"
    })
    bot.ingestion_manager.register_source(cpu_monitor)
    
    # Define handlers
    def handle_webhook(conn, event, args):
        print(f"Webhook: {event.data}")
        
    def handle_file(conn, event, args):
        print(f"File: {event.metadata.get('filepath')}")
        
    def handle_metric(conn, event, args):
        print(f"Metric alert: {event.data}")
    
    # Bind handlers
    bot.bind("webhook", "-|-", "*", handle_webhook)
    bot.bind("file", "-|-", "*.yaml", handle_file)
    bot.bind("metric", "-|-", "*", handle_metric)
    
    # Start ingestion sources
    async def start_ingestion():
        await github_webhook.start()
        await config_watcher.start()
        await cpu_monitor.start()
    
    asyncio.create_task(start_ingestion())
    
    # Start bot
    bot.start()


if __name__ == "__main__":
    main()
```

## Configuration

You can also configure ingestion sources via `config.yml`:

```yaml
ingestion:
  webhooks:
    enabled: true
    port: 8080
    secret: "your_webhook_secret"
    
  files:
    enabled: true
    watch_directories:
      - "/var/log/myapp"
      - "/etc/myapp/config"
      
  streaming:
    enabled: true
    kafka:
      brokers:
        - "localhost:9092"
    
  metrics:
    enabled: true
    prometheus:
      host: "localhost"
      port: 9090
```

Then load and use the configuration in your bot code.
