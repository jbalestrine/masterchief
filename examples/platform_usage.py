"""
Example usage of MasterChief Platform Phase 1 & 2 components.

This example demonstrates:
1. Creating the Flask application
2. Publishing events to the event bus
3. Streaming logs
4. Using WebSocket for real-time updates
"""
import asyncio
import logging
from platform.app import create_app, run_app
from core.event_bus import Event, get_event_bus
from platform.event_bus import EventType, EventPublisher
from platform.logs import LogCollector, LogEntry

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_event_publishing():
    """Example of publishing events."""
    # Get event bus instance
    event_bus = get_event_bus()
    
    # Create an event publisher
    publisher = EventPublisher(source="example", event_bus=event_bus)
    
    # Publish deployment started event
    await publisher.publish_deployment_started(
        deployment_id="deploy-001",
        metadata={"environment": "production", "service": "api"}
    )
    logger.info("Published deployment started event")
    
    # Publish deployment progress
    await publisher.publish_deployment_progress(
        deployment_id="deploy-001",
        progress=50,
        message="Installing dependencies"
    )
    logger.info("Published deployment progress event")
    
    # Publish plugin event
    await publisher.publish_plugin_event(
        event_type=EventType.PLUGIN_INSTALLED.value,
        plugin_id="monitoring-plugin",
        data={"version": "1.0.0", "author": "MasterChief Team"}
    )
    logger.info("Published plugin installed event")
    
    # Publish log entry
    await publisher.publish_log_entry(
        level="INFO",
        message="Application started successfully",
        metadata={"component": "main"}
    )
    logger.info("Published log entry event")
    
    # Publish system health
    await publisher.publish_system_health(
        status="healthy",
        metrics={"cpu": 45.2, "memory": 60.5, "disk": 70.0}
    )
    logger.info("Published system health event")


async def example_log_collection():
    """Example of collecting and streaming logs."""
    # Create log collector
    collector = LogCollector()
    
    # Add a log handler
    def log_handler(log_entry: LogEntry):
        logger.info(f"Collected log: [{log_entry.level}] {log_entry.message}")
    
    collector.add_handler(log_handler)
    
    # Start collecting
    await collector.start_collecting()
    
    # Collect some logs
    log1 = collector.create_log_entry(
        level="INFO",
        source="webapp",
        message="User logged in",
        metadata={"user_id": "123", "ip": "192.168.1.1"}
    )
    await collector.collect_log(log1)
    
    log2 = collector.create_log_entry(
        level="ERROR",
        source="database",
        message="Connection timeout",
        metadata={"host": "db.example.com"}
    )
    await collector.collect_log(log2)
    
    # Stop collecting
    await collector.stop_collecting()


def example_subscribing_to_events():
    """Example of subscribing to events."""
    event_bus = get_event_bus()
    
    # Define event handlers
    def handle_deployment_started(event: Event):
        logger.info(f"Deployment started: {event.data.get('deployment_id')}")
    
    def handle_plugin_installed(event: Event):
        logger.info(f"Plugin installed: {event.data.get('plugin_id')}")
    
    async def handle_system_health(event: Event):
        logger.info(f"System health: {event.data.get('status')}")
        logger.info(f"Metrics: {event.data.get('metrics')}")
    
    # Subscribe to events
    event_bus.subscribe(EventType.DEPLOYMENT_STARTED.value, handle_deployment_started)
    event_bus.subscribe(EventType.PLUGIN_INSTALLED.value, handle_plugin_installed)
    event_bus.subscribe(EventType.SYSTEM_HEALTH.value, handle_system_health)
    
    logger.info("Subscribed to deployment, plugin, and system events")


async def main():
    """Main example function."""
    logger.info("=== MasterChief Platform Example ===")
    
    # Example 1: Subscribe to events
    logger.info("\n1. Setting up event subscriptions")
    example_subscribing_to_events()
    
    # Example 2: Publish events
    logger.info("\n2. Publishing events")
    await example_event_publishing()
    
    # Wait a bit for async handlers
    await asyncio.sleep(1)
    
    # Example 3: Log collection
    logger.info("\n3. Collecting logs")
    await example_log_collection()
    
    logger.info("\n=== Example Complete ===")


def run_full_application():
    """Example of running the full Flask application."""
    logger.info("Creating MasterChief Platform application...")
    
    # Create the Flask app
    app = create_app()
    
    logger.info("Application created successfully!")
    logger.info("\nAvailable endpoints:")
    logger.info("  - http://localhost:8080/health")
    logger.info("  - http://localhost:8080/health/ready")
    logger.info("  - http://localhost:8080/api/v1/")
    logger.info("  - http://localhost:8080/api/v1/logs")
    logger.info("\nWebSocket endpoint:")
    logger.info("  - ws://localhost:8080/socket.io/")
    logger.info("\nStarting server on http://0.0.0.0:8080")
    
    # Run the application
    run_app(app, host='0.0.0.0', port=8080, debug=True)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'server':
        # Run full Flask application
        run_full_application()
    else:
        # Run examples
        asyncio.run(main())
